import sys
import os
import yaml
from src.intent_engine import IntentEngine
from src.device_manager import DeviceManager
from src.intent_engine import fetch_contract_abi, extract_events_from_abi, choose_trigger

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

# Define the paths for configuration files
modules_file_path = os.path.join(project_root, "modules.yaml")
intents_file_path = os.path.join(project_root, "intents.yaml")

# Load modules configuration
with open(modules_file_path, "r") as file:
    module_configs = yaml.safe_load(file)["modules"]

# Initialize device manager
device_manager = DeviceManager(module_configs)

# Dynamic ABI fetching and user interaction
contract_address = input("Enter the DAI contract address on Sepolia: ")
abi_json = fetch_contract_abi(contract_address)
events = extract_events_from_abi(abi_json)
selected_event = choose_trigger(events)

# Update the intents.yaml trigger with the selected contract address
with open(intents_file_path, "r") as file:
    intents = yaml.safe_load(file)
intents["intents"][0]["trigger"]["contract_address"] = contract_address

# Save the updated intents
with open(intents_file_path, "w") as file:
    yaml.dump(intents, file)

# Initialize the intent engine
engine = IntentEngine(intents_file_path, device_manager)

# Listen for blockchain events
print(f"Listening for {selected_event['name']} events on {contract_address}...")
while True:
    engine.listen_to_event(selected_event, contract_address, abi_json)
