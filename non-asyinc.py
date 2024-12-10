import os
#import asyncio
import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, WhatsOnChainBroadcaster
#Private key L1xkzp3sLV58hXyppmYnijLbz6sxS1fDjEQMN3GyevR27A7nGqGV Yours Wallet PK 
# Yours Wallet 1PXxMeP14C1A73y8Lf8DNT2o5EWGftGDUV
# 
# PK KxJ4TgQNacRaMC4PX24E7Yw8wanFnzY2KAbTeYjnpyVz2pyhpHnE Address 1NGivRZYtqkdW4TxZfkNfEDjnficNxgak8	

# Public Key 029baa7dbe4484b5edbbd68343dff346a1f8af082386b146ebd1a253c4572a6e0a
#Address to Pub. Key 1NGivRZYtqkdW4TxZfkNfEDjnficNxgak8
# Replace with your private key (WIF format)
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS')

def fetch_utxos(address):
    """Fetches UTXOs from WhatsOnChain for a given address."""
    url = f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/unspent"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching UTXOs:", response.status_code, response.text)
        return []

def fetch_transaction(txid):
    """Fetches the full transaction details for a given txid from WhatsOnChain."""
    url = f"https://api.whatsonchain.com/v1/bsv/main/tx/{txid}/hex"
    response = requests.get(url)
    if response.status_code == 200:
        # Directly access the text content since the response is in raw hex format
        return Transaction.from_hex(response.text)
    else:
        print("Error fetching transaction:", response.status_code, response.text)
        return None


def create_and_broadcast_transaction(utxo):
    # Initialize private key and recipient address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()

    # Fetch the full source transaction for the UTXO
    source_tx = fetch_transaction(utxo['tx_hash'])
    if not source_tx:
        print("Failed to fetch source transaction.")
        return

    # Set up the transaction input using the UTXO and source transaction
    tx_input = TransactionInput(
        source_transaction=source_tx,
        source_txid=utxo['tx_hash'],
        source_output_index=utxo['tx_pos'],
        unlocking_script_template=P2PKH().unlock(priv_key)
    )

    # Define the transaction output to the target address
    tx_output = TransactionOutput(
        locking_script=P2PKH().lock(TARGET_ADDRESS),
        satoshis=10000  # Specify the amount to send (in satoshis)
    )

    # Define the change output back to the sender
    tx_output_change = TransactionOutput(
        locking_script=P2PKH().lock(address),
        satoshis=utxo['value'] - 10000 - 1000  # Deduct amount sent and a fee of 1000 satoshis
    )

    # Create the transaction with the input and outputs
    
    tx = Transaction([tx_input], [tx_output, tx_output_change])
    print("output is")
    print(utxo['value'] - 10000 - 1000)
    print(f"value is {utxo['value']}")

    # Set the fee, sign the transaction, and broadcast it
    tx.fee(1000)
    tx.sign()

    # Broadcast transaction to mainnet using WhatsOnChainBroadcaster
    broadcaster = WhatsOnChainBroadcaster()
    broadcaster.broadcast(tx)

    print(f"Transaction ID: {tx.txid()}")
    print(f"Raw hex: {tx.hex()}")

def main():
    # Initialize private key and address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()

    # Fetch UTXOs for the address
    utxos = fetch_utxos(address)
    if not utxos:
        print("No UTXOs available to create a transaction.")
        return

    # Use the first available UTXO for creating a transaction
    for utxo in utxos:
        if utxo['value'] > 11000:
            break
    create_and_broadcast_transaction(utxo)

if __name__ == "__main__":
    main()
