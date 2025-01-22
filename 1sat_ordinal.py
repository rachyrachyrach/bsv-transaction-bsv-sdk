from yenpoint_1satordinals.core import OneSatOrdinal
from bsv import PrivateKey, P2PKH, Transaction
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
TARGET_ADDRESS = os.environ.get('TARGET_ADDRESS')

def create_ordinal_test():
    # Initialize private key
    private_key = PrivateKey(PRIVATE_KEY)
    sender_address = private_key.address()
    
    logger.info(f"Creating ordinal from {sender_address} to {TARGET_ADDRESS}")
    
    # Read image file
    image_path = 'test_image.jpg'
    content_type = 'image/jpeg'
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
        logger.info(f"Image size: {len(image_data)} bytes")
    
    # Create ordinal script
    ordinal = OneSatOrdinal()
    ordinal_script = ordinal.create_1sat_ordinal(
        TARGET_ADDRESS,
        content_type,
        image_data
    )
    
    # Create transaction with the ordinal script
    tx = Transaction()
    tx.add_output(ordinal_script)
    
    logger.info(f"Created transaction with ordinal script")
    return tx

if __name__ == "__main__":
    if not PRIVATE_KEY or not TARGET_ADDRESS:
        logger.error("Please set PRIVATE_KEY and TARGET_ADDRESS environment variables")
        exit(1)
        
    try:
        tx = create_ordinal_test()
        print("Success! Transaction created.")
        print(f"Transaction hex: {tx.hex()}")
    except Exception as e:
        logger.error(f"Error creating ordinal: {str(e)}")
