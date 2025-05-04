import os
from tinydb import TinyDB
from random import uniform, randint
from PIL import Image, ImageDraw

DATABASE = "database/product.json"

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# Remove existing database
if os.path.exists(DATABASE):
    os.remove(DATABASE)

db = TinyDB(DATABASE)

# Default product image
DEFAULT_IMAGE = "assets/products/default.png"

# Ensure products directory exists
os.makedirs("assets/products", exist_ok=True)

# Create default product image if it doesn't exist
if not os.path.exists(DEFAULT_IMAGE):
    # Create a simple default image
    img = Image.new('RGB', (100, 100), color='gray')
    d = ImageDraw.Draw(img)
    d.text((10, 40), "Product", fill='white')
    img.save(DEFAULT_IMAGE)

colors = [
    'red', 'blue', 'purple',
    'green', 'orange', 'pink',
    'yellow', '#EF4B4C', '#4AA976'
]

products = os.listdir('./assets/products')

for product in products:
    productName = product.split(".")[0]
    db.insert({
        'name': productName.split("-")[0].capitalize() + " " + productName.split("-")[1].capitalize(),
        'image': f"assets/products/{product}",
        'quantity': randint(0, 90),
        'price': round(uniform(3.99, 5.99), 2),
        'displayed': True
    })
