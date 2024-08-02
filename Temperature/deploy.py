import os
import firebase_admin
from firebase_admin import credentials, firestore
from web3 import Web3
from dotenv import load_dotenv
import json
from datetime import datetime


load_dotenv()

service_account_key_path = 'Service-Link'


cred = credentials.Certificate(service_account_key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

infura_project_id = os.getenv("INFURA_PROJECT_ID")
private_key_1 = os.getenv("PRIVATE_KEY_2")
private_key_2 = os.getenv("PRIVATE_KEY_1")

sepolia_url = f"API-Key link"
w3 = Web3(Web3.HTTPProvider(sepolia_url))

if not w3.is_connected():
    print("Failed to connect to Web3")
    exit()
print("Connected to Web3")

address_2 = "0x9658DF8751FC88C47Axxxxxxxxxxxxxxxxxxxxxx"
address_1 = "0x62cD933d7F3928de8xxxxxxxxxxxxxxxxxxxxxxx"

def load_last_transaction():
    if os.path.exists('last_transaction.json'):
        with open('last_transaction.json', 'r') as file:
            return json.load(file)
    return None

def save_last_transaction(tx_hash, temperature):
    data = {
        'tx_hash': tx_hash,
        'temperature': temperature
    }
    with open('last_transaction.json', 'w') as file:
        json.dump(data, file)

def get_latest_temperature_from_cloud():
    docs = db.collection('temperatures').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    for doc in docs:
        return doc.to_dict().get('temperature')
    return None


def get_current_temperature():
    pass

def send_ether(sender_address, recipient_address, private_key, amount_in_ether, current_temperature):
    last_transaction = load_last_transaction()
    if last_transaction:
        last_temperature = last_transaction.get('temperature')
        if last_temperature is not None:
            temperature_difference = current_temperature - last_temperature
            if abs(temperature_difference) > 5:
                if temperature_difference > 0:
                    print(f"Warning: The temperature has suddenly increased by {temperature_difference:.2f} degrees!")
                else:
                    print(f"Warning: The temperature has suddenly decreased by {abs(temperature_difference):.2f} degrees!")
            else:
                print(f"Current temperature is {current_temperature:.2f} degrees.")

    nonce = w3.eth.get_transaction_count(sender_address)
    amount_in_wei = w3.to_wei(amount_in_ether, 'ether')
    
    tx = {
        'nonce': nonce,
        'to': recipient_address,
        'value': amount_in_wei,
        'gas': 22000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'chainId': 11155111  
    }
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent with hash: {tx_hash.hex()}")
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        print(f"Transaction receipt: {tx_receipt}")

        
        save_last_transaction(tx_hash.hex(), current_temperature)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return tx_hash

def print_balances():
    balance_1 = w3.eth.get_balance(address_1)
    balance_2 = w3.eth.get_balance(address_2)
    
    print(f"Address 1 balance: {w3.from_wei(balance_1, 'ether')} ETH")
    print(f"Address 2 balance: {w3.from_wei(balance_2, 'ether')} ETH")


current_temperature = get_latest_temperature_from_cloud()
if current_temperature is not None:
    send_ether(address_1, address_2, private_key_1, 0.00, current_temperature)
    print_balances()
else:
    print("No temperature data available.")
