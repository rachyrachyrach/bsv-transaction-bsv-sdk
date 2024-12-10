import os
import asyncio
import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, WhatsOnChainBroadcaster

PRIVATE_KEY = os.environ.get('PRIVATE_KEY') # insert your wallet's private key by using export PRIVATE_KEY local file
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS') ## insert the wallet address you're sending money to. client id by export TARGET_ADDRESS local file

async def fetch_utxos(address):
    """Fetches UTXOs from WhatsOnChain for a given address."""
    print(f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/unspent")
    url = f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/unspent"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching UTXOs:", response.status_code, response.text)
        return []

async def fetch_transaction(txid):
    """Fetches the full transaction details for a given txid from WhatsOnChain."""
    url = f"https://api.whatsonchain.com/v1/bsv/main/tx/{txid}/hex"
    response = requests.get(url)
    if response.status_code == 200:
        # Directly access the text content since the response is in raw hex format
        return Transaction.from_hex(response.text)
    else:
        print("Error fetching transaction:", response.status_code, response.text)
        return None


async def create_and_broadcast_transaction(utxo):
    # Initialize private key and recipient address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()

    # Fetch the full source transaction for the UTXO
    source_tx = await fetch_transaction(utxo['tx_hash'])
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
        satoshis=1000  # Specify the amount to send (in satoshis)
    )

    # Define the change output back to the sender
    tx_output_change = TransactionOutput(
        locking_script=P2PKH().lock(address),
        satoshis=utxo['value'] - 1000 - 1000  # Deduct amount sent and a fee of 1000 satoshis
        
    )

    # Create the transaction with the input and outputs
    tx = Transaction([tx_input], [tx_output, tx_output_change])
    print("output is")
    print(utxo['value'] - 1000 - 100)
    print(f"value is {utxo['value']}")

    # Set the fee, sign the transaction, and broadcast it
    tx.fee(1000)
    tx.sign()

    # Broadcast transaction to mainnet using WhatsOnChainBroadcaster
    broadcaster = WhatsOnChainBroadcaster()
    await broadcaster.broadcast(tx)

    print(f"Transaction ID: {tx.txid()}")
    print(f"Raw hex: {tx.hex()}")

async def main():
    # Initialize private key and address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()

    # Fetch UTXOs for the address
    utxos = await fetch_utxos(address)
    if not utxos:
        print("No UTXOs available to create a transaction.")
        return

    # Use the first available UTXO for creating a transaction
    #example of my utxos https://api.whatsonchain.com/v1/bsv/main/address/1PXxMeP14C1A73y8Lf8DNT2o5EWGftGDUV/unspent for my Yours Wallet 1PXxMeP14C1A73y8Lf8DNT2o5EWGftGDUV
    for utxo in utxos:
        if utxo['value'] > 1000: #loopy loop that searches through all utxos to find the first one that is greater than 1000 satoshis
            break
    await create_and_broadcast_transaction(utxo)

if __name__ == "__main__":
    asyncio.run(main())
