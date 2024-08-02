import os
import json
import time
from web3 import Web3
from web3.exceptions import TimeExhausted
from dotenv import load_dotenv
from bsm_data import generate_random_bsm_data

load_dotenv()

sepolia_url = os.getenv("API_Link")
w3 = Web3(Web3.HTTPProvider(sepolia_url))

if not w3.is_connected():
    print("Failed to connect to Web3")
    exit()
print("Connected to Web3")


accounts = [
    "0x9658DF8751FC88C47A1482xxxxxxxxxxxxxxxxx",
    "0x62cD933d7Fxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "0x67cDnfhvbhvbrhxxxxxxxxxxxxxxxxxxxxxxxxx",
]

infura_project_id = os.getenv("INFURA_PROJECT_ID")
address_0 = accounts[0]
private_key_0 = os.getenv("PRIVATE_KEY_0")

def print_node_info():
    try:   
        peer_count = w3.net.peer_count
        print(f"Number of nodes connected: {peer_count}")
    except Exception as e:
        print("Error retrieving node information:", e)


def send_ether(sender_address, recipient_address, private_key, amount_in_ether):
    amount_in_wei = w3.to_wei(amount_in_ether, 'ether')
    nonce = w3.eth.get_transaction_count(sender_address)
    
    tx = {
        'nonce': nonce,
        'to': recipient_address,
        'value': amount_in_wei,
        'gas': 23000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'chainId': 11155111
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash
    except ValueError as e:
        if "already known" in str(e):
            tx['gasPrice'] = w3.to_wei('55', 'gwei')
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return tx_hash
        else:
            raise e

def wait_for_receipt(tx_hash):
    try:
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=250)
        return tx_receipt
    except TimeExhausted:
        print("Transaction was not mined within 250 seconds, stopping process.")
        return None

def print_balances():
    balance_0 = w3.eth.get_balance(address_0)
    print(f"Address 0 balance: {w3.from_wei(balance_0, 'ether')} ETH")
    for i in range(1, len(accounts)):
        balance = w3.eth.get_balance(accounts[i])
        print(f"Address {i} balance: {w3.from_wei(balance, 'ether')} ETH")



bsm_data = generate_random_bsm_data()
print("BSM data transferred:")
print(json.dumps(bsm_data, indent=4))

start_time = time.time()

for i in range(1, len(accounts)):
    tx_hash = send_ether(address_0, accounts[i], private_key_0, 0.00)
    if tx_hash:
        tx_receipt = wait_for_receipt(tx_hash)
        if tx_receipt:
            print(f"Transaction {i} receipt: {tx_receipt}")

end_time = time.time()
total_time = end_time - start_time
print(f"Total time taken to complete the transactions: {total_time:.2f} seconds")

print_balances()
print_node_info()
