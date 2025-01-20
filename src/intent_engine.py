import os
import yaml
import time
import json
import requests
from web3 import Web3
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Web3 connection
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node.")

class IntentEngine:
    def __init__(self, config_file, device_manager):
        self.intents = self.load_intents(config_file)
        self.device_manager = device_manager

    def load_intents(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)["intents"]

    def process_trigger(self, trigger):
        for intent in self.intents:
            if self.matches(intent, trigger):
                logger.info(f"Trigger matched intent: {intent['name']}")
                self.execute_actions(intent['actions'])

    def matches(self, intent, trigger):
        trigger_event = trigger.get("event")
        intent_trigger = intent["trigger"]
        return (
            intent_trigger["event"] == trigger_event and
            intent_trigger.get("contract_address") == trigger.get("contract_address")
        )

    def execute_actions(self, actions):
        for action in actions:
            logger.info(f"Executing action: {action}")
            device = action.get("device")
            if device:
                self.device_manager.execute_action(device, action)
            else:
                logger.warning("No device specified for action.")

    def listen_to_event(self, selected_event, contract_address, abi_json):
        contract = w3.eth.contract(address=contract_address, abi=abi_json)
        event_filter = contract.events[selected_event["name"]].create_filter(from_block="latest")

        logger.info(f"Listening for {selected_event['name']} events on {contract_address}...")
        while True:
            for event in event_filter.get_new_entries():
                trigger = {
                    "event": selected_event["name"],
                    "contract_address": contract_address,
                    "args": event["args"]
                }
                self.process_trigger(trigger)
            time.sleep(1)

def fetch_contract_abi(contract_address):
    url = f"https://api-sepolia.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    result = response.json()
    if result["status"] == "1":
        return json.loads(result["result"])
    else:
        raise Exception(f"Error fetching ABI: {result['message']}")

def extract_events_from_abi(abi):
    return [item for item in abi if item.get("type") == "event"]

def choose_trigger(events):
    print("Available Events:")
    for i, event in enumerate(events):
        print(f"{i + 1}: {event['name']}")
    choice = int(input("Select an event by number: ")) - 1
    return events[choice]

def listen_to_events(intent_engine):
    contract_address = input("Enter the contract address: ")
    abi = fetch_contract_abi(contract_address)
    events = extract_events_from_abi(abi)
    selected_event = choose_trigger(events)
    intent_engine.listen_to_event(selected_event, contract_address, abi)

if __name__ == "__main__":
    from src.device_manager import DeviceManager  # Ensure this module exists and is properly implemented

    # Load device manager and intents
    device_manager = DeviceManager("modules.yaml")
    engine = IntentEngine("intents.yaml", device_manager)

    # Start monitoring events
    listen_to_events(engine)
