import os
from web3 import Web3
import yaml
from dotenv import load_dotenv
import requests
import json
import time

# Load environment variables
load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

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
                print(f"Trigger matched intent: {intent['name']}")
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
            print(f"Executing action: {action}")
            device = action.get("device")
            if device:
                self.device_manager.execute_action(device, action)
            else:
                print("No device specified for action.")

    def trigger_http_action(self, state):
        url = "http://localhost:5000/device/light"
        payload = {"state": state}
        try:
            response = requests.post(url, json=payload)
            print(f"Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to trigger action: {e}")

# Fetch contract ABI dynamically
def fetch_contract_abi(contract_address):
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    result = response.json()
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

# Listen to blockchain events or other triggers
def listen_to_events(intent_engine):
    contract_address = input("Enter the contract address: ")
    abi = fetch_contract_abi(contract_address)
    events = extract_events_from_abi(abi)

    # Let user select an event
    selected_event = choose_trigger(events)

    # Create contract and event filter
    contract = w3.eth.contract(address=contract_address, abi=abi)
    event_filter = contract.events[selected_event["name"]].createFilter(fromBlock="latest")

    print(f"Listening for {selected_event['name']} events...")
    while True:
        for event in event_filter.get_new_entries():
            trigger = {
                "event": selected_event["name"],
                "contract_address": contract_address,
                "args": event["args"]
            }
            intent_engine.process_trigger(trigger)
        time.sleep(1)

# Monitor non-contract triggers (e.g., block numbers or ETH price)
def monitor_non_contract_triggers(intent_engine):
    print("Monitoring block numbers and ETH price...")
    while True:
        block_number = w3.eth.blockNumber
        eth_price = get_eth_price()
        print(f"Block Number: {block_number}, ETH Price: {eth_price}")
        # Add logic to match block number or price to intents
        time.sleep(10)

# Fetch ETH price (example using Chainlink)
def get_eth_price():
    # Replace with Chainlink oracle call or another API
    return w3.fromWei(w3.eth.get_balance("0x0000000000000000000000000000000000000000"), "ether")

if __name__ == "__main__":
    engine = IntentEngine("intents.yaml")
    intent_engine = engine

    # Choose monitoring type
    choice = input("Monitor (1) Contract Events or (2) Non-Contract Triggers? ")
    if choice == "1":
        listen_to_events(intent_engine)
    elif choice == "2":
        monitor_non_contract_triggers(intent_engine)
    else:
        print("Invalid choice.")
