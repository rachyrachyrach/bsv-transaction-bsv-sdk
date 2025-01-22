from yenpoint_1satordinals.core import OneSatOrdinal
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, WhatsOnChainBroadcaster
import logging
import os
import asyncio
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS')

async def create_and_broadcast_ordinal():
    private_key = PrivateKey(PRIVATE_KEY)
    sender_address = private_key.address()
    
    # Get UTXOs
    response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/address/{sender_address}/unspent")
    utxos = response.json()
    
    if not utxos:
        logger.info("No UTXOs found - need BSV in wallet first")
        return None
        
    utxo = next((u for u in utxos if u['value'] > 1000), None)
    if not utxo:
        logger.info("No UTXO with sufficient funds found")
        return None

    logger.info(f"Creating ordinal from {sender_address} to {TARGET_ADDRESS}")
    
    # Get source transaction
    response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/tx/{utxo['tx_hash']}/hex")
    source_tx = Transaction.from_hex(response.text)
    
    # Create input
    tx_input = TransactionInput(
        source_transaction=source_tx,
        source_txid=utxo['tx_hash'],
        source_output_index=utxo['tx_pos'],
        unlocking_script_template=P2PKH().unlock(private_key)
    )
    
    # Read and create ordinal
    with open('mollymatch_logo.jpg', 'rb') as f:
        image_data = f.read()
        logger.info(f"Image size: {len(image_data)} bytes")
    
    ordinal = OneSatOrdinal()
    ordinal_script = ordinal.create_1sat_ordinal(
        TARGET_ADDRESS,
        'image/jpeg',
        image_data
    )
    
    # Create transaction
    ordinal_output = TransactionOutput(
        locking_script=ordinal_script,
        satoshis=1
    )
    
    tx = Transaction([tx_input], [ordinal_output])
    
    # Add change output
    change_amount = utxo['value'] - 1000
    if change_amount > 0:
        change_output = TransactionOutput(
            locking_script=P2PKH().lock(sender_address),
            satoshis=change_amount
        )
        tx.outputs.append(change_output)
    
    tx.sign()
    
    # Broadcast and get TXID
    broadcaster = WhatsOnChainBroadcaster()
    response = await broadcaster.broadcast(tx)
    txid = tx.txid()
    
    # Submit to GorillaPool
    gorilla_url = f"https://ordinals.gorillapool.io/api/v1/bsv20/tx/{txid}"
    gorilla_response = requests.post(gorilla_url)
    
    logger.info(f"Transaction broadcasted! TXID: {txid}")
    logger.info(f"View your ordinal at: https://ordinals.gorillapool.io/content/{txid}")
    
    return txid

if __name__ == "__main__":
    txid = asyncio.run(create_and_broadcast_ordinal())
    if txid:
        print("Success! Ordinal created and broadcasted.")
        print(f"TXID: {txid}")
        print(f"View at: https://ordinals.gorillapool.io/content/{txid}")
