from dotenv import load_dotenv
import os
import yaml
import importlib
import logging
import requests
import json
import time
from web3 import Web3

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class IntentEngine:
    def __init__(self, intents_dir, device_manager, web3_instance):
        self.device_manager = device_manager
        self.web3 = web3_instance
        self.intents = self.load_intents(intents_dir)
        self.intent_modules = self.load_intent_modules(intents_dir)
        self.processed_tx_hashes = set()  # Track processed transactions

    def load_intents(self, intents_dir):
        intents = []
        for folder in os.listdir(intents_dir):
            intent_path = os.path.join(intents_dir, folder, "intent.yaml")
            if os.path.isfile(intent_path):
                with open(intent_path, "r") as file:
                    intent_config = yaml.safe_load(file)
                    intents.append(intent_config)
        return intents

    def load_intent_modules(self, intents_dir):
        modules = {}
        for intent in self.intents:
            module_name = intent["module"]
            try:
                module = importlib.import_module(f"src.intents.{module_name}.{module_name}")
                intent_class_name = "".join(word.capitalize() for word in module_name.split("_"))
                intent_class = getattr(module, intent_class_name)
                modules[module_name] = intent_class
            except AttributeError:
                logger.error(f"Class '{intent_class_name}' not found in module '{module_name}'.")
            except Exception as e:
                logger.error(f"Failed to load module {module_name}: {e}")
        return modules

    def process_trigger(self, trigger):
        for intent in self.intents:
            if self.matches(intent, trigger):
                logger.info(f"Trigger matched intent: {intent['name']}")
                module_name = intent["module"]
                if module_name in self.intent_modules:
                    try:
                        intent_instance = self.intent_modules[module_name](
                            intent, self.device_manager, self.web3
                        )
                        intent_instance.process_event(trigger)
                    except Exception as e:
                        logger.error(f"Error processing trigger: {e}")
                else:
                    logger.error(f"Intent module {module_name} not found.")

    def matches(self, intent, trigger):
        trigger_event = trigger.get("event")
        intent_trigger = intent["trigger"]
        contract_match = (
            intent_trigger.get("contract_address") == "dynamic" or
            intent_trigger.get("contract_address") == trigger.get("contract_address")
        )
        return intent_trigger["event"] == trigger_event and contract_match

    def listen_to_event(self, selected_event, contract_address, abi_json):
        """Listen for new blockchain events."""
        if not self.web3.is_connected():
            logger.error("Web3 is not connected to the Ethereum node.")
            return

        # Create contract instance
        contract = self.web3.eth.contract(address=contract_address, abi=abi_json)
        
        # Create filter for new events
        event_filter = contract.events[selected_event["name"]].create_filter(
            from_block='latest'
        )

        logger.info(f"Listening for new {selected_event['name']} events on {contract_address}...")
        logger.info("Waiting for transfers... (Press Ctrl+C to stop)")

        # Main event loop
        while True:
            try:
                new_events = event_filter.get_new_entries()
                
                for event in new_events:
                    tx_hash = event['transactionHash'].hex()
                    if tx_hash not in self.processed_tx_hashes:
                        logger.info(f"New event detected! Transaction hash: {tx_hash}")
                        self.processed_tx_hashes.add(tx_hash)
                        trigger = {
                            "event": selected_event["name"],
                            "contract_address": contract_address,
                            "args": event["args"]
                        }
                        self.process_trigger(trigger)
                
                # Clean up old transaction hashes if the set gets too large
                if len(self.processed_tx_hashes) > 1000:
                    logger.info("Cleaning up old transaction hashes...")
                    self.processed_tx_hashes.clear()
                
                time.sleep(2)  # Poll every 2 seconds

            except Exception as e:
                logger.error(f"Error in event listener: {e}")
                # Recreate filter if there's an error
                event_filter = contract.events[selected_event["name"]].create_filter(
                    from_block='latest'
                )
                time.sleep(5)  # Wait a bit longer on error

def fetch_contract_abi(contract_address):
    """Fetch contract ABI from Etherscan."""
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
    if not ETHERSCAN_API_KEY:
        raise Exception("ETHERSCAN_API_KEY is not set.")

    url = f"https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    result = response.json()

    if result["status"] == "1" and result["message"] == "OK":
        return json.loads(result["result"])
    else:
        raise Exception(f"Error fetching ABI: {result.get('message', 'Unknown error')}")

def extract_events_from_abi(abi):
    """Extract events from contract ABI."""
    return [item for item in abi if item.get("type") == "event"]

def choose_trigger(events):
    """Allow user to choose an event trigger."""
    print("\nAvailable Events:")
    for i, event in enumerate(events):
        print(f"{i + 1}: {event['name']}")
    while True:
        try:
            choice = int(input("\nSelect an event by number: ")) - 1
            if 0 <= choice < len(events):
                return events[choice]
            print(f"Please enter a number between 1 and {len(events)}")
        except ValueError:
            print("Please enter a valid number")