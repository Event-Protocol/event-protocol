import sys
import os
import yaml
import logging
from web3 import Web3
from dotenv import load_dotenv
from src.intent_engine import IntentEngine, fetch_contract_abi, extract_events_from_abi, choose_trigger
from src.device_manager import DeviceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

def main():
    try:
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

        logger.info(f"Connected to network: Chain ID {web3_instance.eth.chain_id}")
        
        # Initialize device manager
        device_manager = DeviceManager(module_configs)

        # Get contract address and fetch ABI
        print("\n" + "="*50)
        contract_address = input("Enter the DAI contract address on Sepolia: ")
        logger.info("Fetching contract ABI...")
        abi_json = fetch_contract_abi(contract_address)
        events = extract_events_from_abi(abi_json)
        
        # Select event to monitor
        selected_event = choose_trigger(events)
        
        # Initialize intent engine
        engine = IntentEngine(intents_dir, device_manager, web3_instance)

        print("\n" + "="*50)
        logger.info(f"Starting event listener for {selected_event['name']} events")
        logger.info(f"Contract address: {contract_address}")
        logger.info("Waiting for transfers... (Press Ctrl+C to stop)")
        print("="*50 + "\n")

        # Start listening for events
        engine.listen_to_event(selected_event, contract_address, abi_json)

    except KeyboardInterrupt:
        logger.info("\nStopping event listener...")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()