from components.Toolbar import ToolbarButton
from components.product import ProductList, ProductItem
from components.keypad import Keypad
from lcd import typerwriter
import states as states
from tinydb import TinyDB
import tkinter as tk
from functools import partial
from windows.login import loginWindow
from PIL import Image, ImageTk, ImageDraw
import os

class Toolbar:
    def __init__(self, parent, c):
        self.container = tk.Frame(parent, height=20, bg="white")
        self.container.pack(pady=(8, 0), padx=8, fill="x")

        ToolbarButton(
            self.container,
            text="Admin",
            command=partial(loginWindow, parent, c),
            image=c.chartImage,
            bg="#8A7BD9",
            activebackground="#463A87",
        ).pack(fill="x", pady=(0, 4))

productDB = TinyDB("database/product.json")

# Ensure required directories exist
os.makedirs("assets/products", exist_ok=True)

# Create default product image if it doesn't exist
DEFAULT_IMAGE = "assets/products/default.png"
if not os.path.exists(DEFAULT_IMAGE):
    img = Image.new('RGB', (100, 100), color='gray')
    d = ImageDraw.Draw(img)
    d.text((10, 40), "Product", fill='white')
    img.save(DEFAULT_IMAGE)

class Controller(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.container = tk.Frame(self, bg="#373C40")
        self.container.pack()

        self.products = []

        self.selected = None
        self.amount = 0
        self.subtotal = tk.DoubleVar(self.container, 0)
        self.basket = {}
        self.state = states.CODE

        # Load and resize the lock.png image for chartImage
        icon_size = (24, 24)  # Desired size for the icon
        try:
            image = Image.open("assets/icons/lock.png")
            image = image.resize(icon_size, Image.LANCZOS)  # High-quality resizing
            self.chartImage = ImageTk.PhotoImage(image)
        except FileNotFoundError:
            print("Error: lock.png not found in assets/icons/")
            self.chartImage = None  # Fallback to no image

        # Load other images without resizing
        self.coin = tk.PhotoImage(file="assets/icons/coin.png")
        self.productImage = tk.PhotoImage(file="assets/icons/product.png")

        self.cart = tk.IntVar(self.container, 0)

        self.screenMessage = tk.StringVar(self.container, "")

        self.locked = False

        # Start with a welcome message
        typerwriter(self, ["Welcome!"])

        for product in productDB.all():
            try:
                self.products.append(
                    ProductItem(
                        self,
                        product.doc_id,
                        product["name"],
                        product.get("image", DEFAULT_IMAGE),
                        product["quantity"],
                        product["price"],
                    )
                )
            except Exception as e:
                print(f"Error loading product {product['name']}: {e}")
                # Try loading with default image
                try:
                    self.products.append(
                        ProductItem(
                            self,
                            product.doc_id,
                            product["name"],
                            DEFAULT_IMAGE,
                            product["quantity"],
                            product["price"],
                        )
                    )
                except Exception as e:
                    print(f"Failed to load product {product['name']} even with default image: {e}")

        self.productList = ProductList(self.container, self)
        self.productList.pack(side="left", expand=1, fill="both", padx=(0, 4))

        self.display = tk.Frame(self.container, bg="white")
        self.display.pack(side="right", expand=1, fill="both", padx=(4, 0))

        self.keypad = Keypad(
            self.display,
            self,
        )
        self.keypad.pack(fill="x", padx=8, pady=8)
        self.toolbar = Toolbar(self.display, self)

    # Update subtotal
    def updateSubtotal(self, new):
        self.subtotal.set(round(self.subtotal.get() + new, 2))

    # Number of the same product
    def setAmount(self, new):
        self.amount = int(new)

    # Save current product choice
    def setSelected(self, new):
        self.selected = new

    # Lock keypad
    def toggleLock(self, state):
        self.locked = state