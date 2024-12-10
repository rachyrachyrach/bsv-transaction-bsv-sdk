import os
import requests
from bsv import PrivateKey

# Replace with your private key (WIF format)
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

def list_unspent_transactions():
    # Initialize private key and get the address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()
    
    # Fetch UTXOs from WhatsOnChain API
    url = f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/unspent"
    response = requests.get(url)
    
    if response.status_code == 200:
        utxos = response.json()
        if utxos:
            print(f"Unspent transactions for address {address}:")
            for utxo in utxos:
                print(f"TxID: {utxo['tx_hash']}, Output Index: {utxo['tx_pos']}, Satoshis: {utxo['value']}")
        else:
            print(f"No unspent transactions found for address {address}.")
    else:
        print("Error fetching UTXOs:", response.status_code, response.text)

if __name__ == "__main__":
    list_unspent_transactions()
