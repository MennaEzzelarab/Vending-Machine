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

        # Add tray canvas that fills x and lets us center the tray inside it
        self.tray_canvas = tk.Canvas(self.container, height=50, bg="white", highlightthickness=0)
        self.tray_canvas.pack(fill="x", pady=(0, 4))

        # Tray dimensions
        self.tray_width = 200
        self.tray_height = 36

        # Store controller for tray status
        self.controller = c

        # Delay drawing until layout is finalized
        self.tray_canvas.bind("<Configure>", self.draw_tray)

        ToolbarButton(
            self.container,
            text="Admin",
            command=partial(loginWindow, parent, c),
            image=c.chartImage,
            bg="#8a0303",
            activebackground="#463A87",
        ).pack(fill="x", pady=(0, 4))

    def draw_tray(self, event=None):
        self.tray_canvas.delete("tray")  # Clear previous drawing

        canvas_width = self.tray_canvas.winfo_width()
        x0 = (canvas_width - self.tray_width) // 2
        x1 = x0 + self.tray_width

        self.tray_canvas.create_rectangle(
            x0, 7, x1, 7 + self.tray_height,
            fill="#3E3E3E",
            outline="#C0C0C0",
            width=2,
            tags="tray"
        )

        self.tray_canvas.create_text(
            (x0 + x1) / 2, 7 + self.tray_height / 2,
            text="Delivery Tray",
            font=("Helvetica", 9, "bold"),
            fill="#FFFFFF",
            tags="tray"
        )

        # Make tray clickable
        self.tray_canvas.tag_bind("tray", "<Button-1>", lambda event: self.open_tray_window())

    def open_tray_window(self):
        # Create a new Toplevel window
        tray_window = tk.Toplevel(self.container)
        tray_window.title("Delivery Tray Status")
        tray_window.geometry("200x150")
        tray_window.configure(bg="white")

        # Determine tray status message
        status_message = "Tray empty" if self.controller.tray_status == "empty" else "Item delivered!"

        # Display status
        tk.Label(
            tray_window,
            text=status_message,
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg="#3E3E3E"
        ).pack(pady=20)

        # Close button
        tk.Button(
            tray_window,
            text="Close",
            command=tray_window.destroy,
            bg="#8a0303",
            fg="white",
            font=("Helvetica", 10),
            activebackground="#463A87"
        ).pack(pady=10)

        # Reset tray status to empty after checking
        if self.controller.tray_status == "delivered":
            self.controller.tray_status = "empty"

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
        self.tray_status = "empty"  # Initialize tray status

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
        self.inventory = tk.PhotoImage(file="assets/icons/chart.png")

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