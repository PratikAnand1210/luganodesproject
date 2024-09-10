import os
import json
import logging
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Constants
INFURA_URL = os.getenv('INFURA_URL')
BEACON_DEPOSIT_CONTRACT = "0x00000000219ab540356cBB839Cbe05303d7705Fa"

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if w3.isConnected():
    print("Connected to Ethereum node")
else:
    print("Failed to connect to Ethereum node")

# Setup logging
logging.basicConfig(
    filename='deposit_tracker.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define Deposit class
class Deposit:
    def __init__(self, block_number, block_timestamp, fee, tx_hash, pubkey):
        self.block_number = block_number
        self.block_timestamp = block_timestamp
        self.fee = fee
        self.tx_hash = tx_hash
        self.pubkey = pubkey

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

# Function to fetch deposit details from transaction hash
def fetch_deposit_data(tx_hash):
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        tx = w3.eth.get_transaction(tx_hash)
        
        if receipt and tx:
            block = w3.eth.getBlock(receipt['blockNumber'])
            block_timestamp = datetime.utcfromtimestamp(block['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            gas_fee = w3.fromWei(receipt['gasUsed'] * tx['gasPrice'], 'ether')

            # Assume the public key is in logs (simplified for this task)
            pubkey = receipt['logs'][0]['topics'][1].hex() if receipt['logs'] else "N/A"

            deposit = Deposit(
                block_number=receipt['blockNumber'],
                block_timestamp=block_timestamp,
                fee=gas_fee,
                tx_hash=tx_hash,
                pubkey=pubkey
            )
            
            logging.info(f"Deposit tracked: {deposit}")
            print(f"Deposit tracked: {deposit}")
        else:
            logging.error(f"Transaction receipt not found for hash: {tx_hash}")
    except Exception as e:
        logging.error(f"Error fetching deposit data for hash {tx_hash}: {str(e)}")
        print(f"Error fetching deposit data for hash {tx_hash}: {str(e)}")

# Function to track deposits by filtering logs
def track_deposits():
    try:
        latest_block = w3.eth.block_number
        logging.info(f"Tracking deposits at block number: {latest_block}")
        print(f"Tracking deposits at block number: {latest_block}")

        # Filter logs for the Beacon Deposit Contract
        filter_params = {
            'address': BEACON_DEPOSIT_CONTRACT,
            'fromBlock': latest_block - 1000,  # Check the last 1000 blocks for deposits
            'toBlock': latest_block
        }

        logs = w3.eth.get_logs(filter_params)

        # Loop through logs and fetch deposit data
        for log in logs:
            tx_hash = log['transactionHash'].hex()
            fetch_deposit_data(tx_hash)

    except Exception as e:
        logging.error(f"Error tracking deposits: {str(e)}")
        print(f"Error tracking deposits: {str(e)}")

# Run tracker every 60 seconds
if __name__ == "__main__":
    import time
    while True:
        track_deposits()
        time.sleep(60)  # Check for new deposits every 60 seconds
