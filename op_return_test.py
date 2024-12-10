import os
import asyncio
import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, WhatsOnChainBroadcaster, Script, OpCode
from bsv.script.script import ScriptChunk



## Location of library /Users/rachael/github/4chain-bsv-sdk/.venv/lib/python3.9/site-packages/bsv/script/script.py
# Environment variables for private key and recipient address
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')  # Set this using: export PRIVATE_KEY="your-private-key"
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS')  # Set this using: export TARGET_ADDRESS="recipient-address"

def create_op_return_script(message):
    """
    Creates a Script for OP_RETURN output using ScriptChunk.
    """
    # Define the OP_RETURN opcode and the message as push data
    chunks = [
        ScriptChunk(OpCode.OP_RETURN),  # OP_RETURN opcode
        ScriptChunk(None, message.encode('utf-8'))  # Message as push data
    ]
    print(f"OP_RETURN Script Hex: {Script.from_chunks(chunks).hex()}")
    print(f"OP_RETURN Script ASM: {Script.from_chunks(chunks).to_asm()}")
    return Script.from_chunks(chunks)

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
        return Transaction.from_hex(response.text)
    else:
        print("Error fetching transaction:", response.status_code, response.text)
        return None

async def create_and_broadcast_transaction(utxo):
    # Initialize private key and recipient address
    priv_key = PrivateKey(PRIVATE_KEY)
    address = priv_key.address()

    # Fetch the full source transaction for the UTXO
    print(f"Fetching source transaction for UTXO: {utxo}")
    source_tx = await fetch_transaction(utxo['tx_hash'])
    if not source_tx:
        print("Failed to fetch source transaction.")
        return

    # Set up the transaction input using the UTXO and source transaction
    print(f"Creating transaction input for TXID: {utxo['tx_hash']}, Output Index: {utxo['tx_pos']}")
    tx_input = TransactionInput(
        source_transaction=source_tx,
        source_txid=utxo['tx_hash'],
        source_output_index=utxo['tx_pos'],
        unlocking_script_template=P2PKH().unlock(priv_key)
    )

    # Define the transaction output to the target address
    fee = 1000  # Transaction fee in satoshis
    tx_output = TransactionOutput(
        locking_script=P2PKH().lock(TARGET_ADDRESS),
        satoshis=1000  # Specify the amount to send (in satoshis)
    )

    # Calculate change
    change = utxo['value'] - 1000 - fee
    if change < 0:
        print("Insufficient funds for transaction.")
        return
    print(f"Transaction fee: {fee}, Change: {change}")

    # Define the change output back to the sender
    tx_output_change = TransactionOutput(
        locking_script=P2PKH().lock(address),
        satoshis=change
    )

    # Create the OP_RETURN script with the message
    print("Creating OP_RETURN script.")
    op_return_script = create_op_return_script("Rae was here")
    tx_output_op_return = TransactionOutput(
        locking_script=op_return_script,
        satoshis=1  # OP_RETURN outputs don't carry value
    )

    # Create the transaction with the input and outputs
    print("Building transaction with inputs and outputs.")
    tx = Transaction([tx_input], [tx_output, tx_output_change, tx_output_op_return])

    # Set the fee, sign the transaction
    print("Signing the transaction.")
    tx.fee(fee)
    tx.sign()

    # Debug transaction details
    print("Transaction details:")
    print(f"Inputs: {tx.inputs}")
    print(f"Outputs: {tx.outputs}")
    print(f"Transaction Hex: {tx.hex()}")

    # Displaying the readable text of the OP_RETURN output
    print("OP_RETURN Output Locking Script:", tx_output_op_return.locking_script.hex())


    # Broadcast transaction to mainnet using WhatsOnChainBroadcaster
    print("Broadcasting transaction...")
    broadcaster = WhatsOnChainBroadcaster()
    try:
        await broadcaster.broadcast(tx)
        print("Transaction broadcasted successfully!")
        print(f"Transaction ID: {tx.txid()}")
    except Exception as e:
        print("Broadcast failed with error:", str(e))


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
    for utxo in utxos:
        if utxo['value'] > 1000:  # Find a UTXO greater than 1000 satoshis
            break
    await create_and_broadcast_transaction(utxo)

if __name__ == "__main__":
    asyncio.run(main())
