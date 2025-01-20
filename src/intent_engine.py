from dotenv import load_dotenv
import os
import yaml
import importlib
import logging
import requests
import json
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class IntentEngine:
    def __init__(self, intents_dir, device_manager, web3_instance):
        self.device_manager = device_manager
        self.web3 = web3_instance
        self.intents = self.load_intents(intents_dir)
        self.intent_modules = self.load_intent_modules(intents_dir)

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
            module_path = os.path.join(intents_dir, module_name)
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
                    intent_instance = self.intent_modules[module_name](
                        intent, self.device_manager, self.web3
                    )
                    intent_instance.process_event(trigger)
                else:
                    logger.error(f"Intent module {module_name} not found.")

    def matches(self, intent, trigger):
        trigger_event = trigger.get("event")
        intent_trigger = intent["trigger"]
        return (
            intent_trigger["event"] == trigger_event
            and intent_trigger.get("contract_address") == trigger.get("contract_address")
        )

    def listen_to_event(self, selected_event, contract_address, abi_json):
        if not self.web3.is_connected():
            logger.error("Web3 is not connected to the Ethereum node.")
            return

        contract = self.web3.eth.contract(address=contract_address, abi=abi_json)
        event_filter = contract.events[selected_event["name"]].create_filter(from_block="latest")

        logger.info(f"Listening for {selected_event['name']} events on {contract_address}...")
        while True:
            try:
                logger.debug("Polling for new events...")
                new_entries = event_filter.get_new_entries()
                if not new_entries:
                    logger.debug("No new events found in this iteration.")

                for event in new_entries:
                    logger.debug(f"New Event: {event}")
                    trigger = {
                        "event": selected_event["name"],
                        "contract_address": contract_address,
                        "args": event["args"]
                    }
                    self.process_trigger(trigger)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
            time.sleep(1)

# Fetch contract ABI dynamically
def fetch_contract_abi(contract_address):
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
    if not ETHERSCAN_API_KEY:
        raise Exception("ETHERSCAN_API_KEY is not set.")

    url = f"https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    result = response.json()

    logger.info(f"API URL: {url}")
    logger.info(f"Response: {result}")

    if result["status"] == "1":
        return json.loads(result["result"])  # Parse ABI JSON
    else:
        raise Exception(f"Error fetching ABI: {result['message']}")

# Extract events from ABI
def extract_events_from_abi(abi):
    return [item for item in abi if item.get("type") == "event"]

# Allow user to choose a trigger
def choose_trigger(events):
    print("Available Events:")
    for i, event in enumerate(events):
        print(f"{i + 1}: {event['name']}")
    choice = int(input("Select an event by number: ")) - 1
    return events[choice]
