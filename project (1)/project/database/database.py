from tinydb import TinyDB
import os

# Ensure the directory exists
os.makedirs('./assets/database', exist_ok=True)

# Initialize the TinyDB database
productDB = TinyDB('./database/product.json')