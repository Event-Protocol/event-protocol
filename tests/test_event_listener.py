import logging
from web3 import Web3
from dotenv import load_dotenv
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_event_listener():
    # Initialize Web3
    INFURA_URL = os.getenv("INFURA_URL")
    if not INFURA_URL:
        raise ValueError("INFURA_URL not found in environment variables")
    
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    
    # Verify connection
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum network")
    
    logger.info(f"Connected to network. Chain ID: {w3.eth.chain_id}")
    logger.info(f"Current block number: {w3.eth.block_number}")
    
    # DAI contract on Sepolia
    contract_address = "0xFF34B3d4Aee8ddCd6F9AFFFB6Fe49bD371b8a357"
    
    # Basic Transfer event ABI
    abi = [{
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }]
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Get current block
    start_block = w3.eth.block_number
    logger.info(f"Checking for Transfer events from block {start_block - 100} to {start_block}")
    
    # Get recent events using the correct parameter names
    transfer_filter = contract.events.Transfer.create_filter(
        from_block=start_block - 100,
        to_block=start_block
    )
    
    try:
        events = transfer_filter.get_all_entries()
        logger.info(f"Found {len(events)} Transfer events in recent blocks")
        
        for event in events:
            # Parse event data
            args = event['args']
            from_address = args['from']
            to_address = args['to']
            value = args['value']
            
            logger.info(f"Transfer Event:")
            logger.info(f"  From: {from_address}")
            logger.info(f"  To: {to_address}")
            logger.info(f"  Value: {value}")
            logger.info(f"  Block Number: {event['blockNumber']}")
            logger.info("---")
            
    except Exception as e:
        logger.error(f"Error getting events: {e}")

if __name__ == "__main__":
    try:
        test_event_listener()
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)