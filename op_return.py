import os
import requests
from bsv import PrivateKey, Transaction, TransactionInput, TransactionOutput, P2PKH, Script, OpCode
import hashlib

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS')

def fetch_utxos(address):
    """
    Fetch UTXOs for a given address from WhatsOnChain API.
    """
    url = f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/unspent"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching UTXOs: {response.status_code}, {response.text}")
        return None

def broadcast_tx(raw_tx):
    """
    Broadcast a raw transaction using WhatsOnChain API.
    """
    url = "https://api.whatsonchain.com/v1/bsv/main/tx/raw"
    response = requests.post(url, json={"txhex": raw_tx})
    if response.status_code == 200:
        print(f"Transaction successfully broadcasted! TXID: {response.json()}")
    else:
        print(f"Error broadcasting transaction: {response.status_code}, {response.text}")

def create_op_return_script(data):
    """
    Create an OP_RETURN script for embedding data into the blockchain.
    """
    script = Script()
    script.add_op(OpCode.OP_RETURN)
    script.push(data.encode('utf-8'))
    return script

def create_and_broadcast_transaction(private_key, recipient_address, amount_bsv, message):
    """
    Create and broadcast a BSV transaction using wallet addresses and OP_RETURN outputs.
    """
    # Convert amount from BSV to satoshis
    SATOSHI_CENT = 100_000_000
    amount_satoshis = int(amount_bsv * SATOSHI_CENT)

    # Get address and fetch UTXOs
    address = private_key.address()
    utxos = fetch_utxos(address)
    if not utxos:
        print("No UTXOs available or failed to fetch.")
        return

    # Select the first UTXO (for simplicity)
    utxo = utxos[0]
    print(f"Using UTXO: {utxo}")

    # Fetch the source transaction for the UTXO
    source_tx_hex = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/tx/{utxo['tx_hash']}/hex").text
    source_transaction = Transaction.from_hex(source_tx_hex)

    # Create the transaction
    tx = Transaction()

    # Add the input
    tx.add_input(
        TransactionInput(
            source_transaction=source_transaction,
            source_output_index=utxo['tx_pos'],
            unlocking_script_template=Script(),  # Placeholder, will be signed
        )
    )

    # Create the recipient P2PKH locking script
    recipient_script = P2PKH.lock(recipient_address)

    # Add the recipient output
    tx.add_output(
        TransactionOutput(
            locking_script=recipient_script,
            satoshis=amount_satoshis,
        )
    )

    # Create the OP_RETURN script
    op_return_script = create_op_return_script(message)

    # Add the OP_RETURN output
    tx.add_output(
        TransactionOutput(
            locking_script=op_return_script,
            satoshis=0,  # OP_RETURN outputs do not hold value
        )
    )

    # Estimate the fee (1 sat/byte is typical for BSV)
    estimated_fee = len(tx.serialize()) + 100  # Add some buffer for signature scripts
    change_satoshis = utxo['value'] - amount_satoshis - estimated_fee

    # Add a change output if change is positive
    if change_satoshis > 0:
        change_script = P2PKH.lock(address)
        tx.add_output(
            TransactionOutput(
                locking_script=change_script,
                satoshis=change_satoshis,
            )
        )

    # Sign the transaction
    tx.sign()

    # Broadcast the transaction
    raw_tx = tx.serialize().hex()
    broadcast_tx(raw_tx)

if __name__ == "__main__":
    # Initialize private key
    PRIVATE_KEY = os.environ.get('PRIVATE_KEY')  # Replace with your private key (WIF format)
    priv_key = PrivateKey(PRIVATE_KEY)

    # Define recipient address, amount, and message
    recipient_address = priv_key.address()  # Replace with actual recipient address
    amount_to_send = 0.0001  # Amount in BSV
    message_to_embed = "Rae was here"

    # Create and broadcast the transaction
    create_and_broadcast_transaction(priv_key, recipient_address, amount_to_send, message_to_embed)
