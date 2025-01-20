import sys
import os
import yaml
from web3 import Web3
from src.intent_engine import IntentEngine, fetch_contract_abi, extract_events_from_abi, choose_trigger
from src.device_manager import DeviceManager

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

# Define the paths for configuration files
modules_file_path = os.path.join(project_root, "modules.yaml")
intents_dir = os.path.join(project_root, "src/intents/")

# Load modules configuration
with open(modules_file_path, "r") as file:
    module_configs = yaml.safe_load(file)["modules"]

# Initialize Web3 instance
INFURA_URL = os.getenv("INFURA_URL")
if not INFURA_URL:
    raise Exception("INFURA_URL is not set in the environment variables.")
web3_instance = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3_instance.is_connected():
    raise Exception("Failed to connect to the Ethereum node.")

# Initialize device manager
device_manager = DeviceManager(module_configs)

# Dynamic ABI fetching and user interaction
contract_address = input("Enter the DAI contract address on Sepolia: ")
abi_json = fetch_contract_abi(contract_address)
events = extract_events_from_abi(abi_json)
selected_event = choose_trigger(events)

# Load intents dynamically
engine = IntentEngine(intents_dir, device_manager, web3_instance)

# Listen for blockchain events
print(f"Listening for {selected_event['name']} events on {contract_address}...")
engine.listen_to_event(selected_event, contract_address, abi_json)
