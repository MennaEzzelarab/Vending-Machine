from components.Toolbar import ToolbarButton
from components.product import ProductList, ProductItem
from components.keypad import Keypad
from components.tray import TrayManager
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

        # Store controller reference
        self.controller = c
        print("Toolbar: Controller reference stored")

        # Add tray canvas that fills x and lets us center the tray inside it
        self.tray_canvas = tk.Canvas(self.container, height=50, bg="white", highlightthickness=0)
        self.tray_canvas.pack(fill="x", pady=(0, 4))

        # Tray dimensions
        self.tray_width = 200
        self.tray_height = 36

        # Animation state
        self.default_color = "#3E3E3E"
        self.flash_color = "#00FF00"
        self.is_animating = False

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
        print("Toolbar: Drawing tray...")
        self.tray_canvas.delete("tray")  # Clear previous drawing

        canvas_width = self.tray_canvas.winfo_width()
        x0 = (canvas_width - self.tray_width) // 2
        x1 = x0 + self.tray_width

        # Draw the tray rectangle
        self.tray_canvas.create_rectangle(
            x0, 7, x1, 7 + self.tray_height,
            fill=self.default_color if not self.is_animating else self.flash_color,
            outline="#C0C0C0",
            width=2,
            tags="tray"
        )

        # Get tray contents from TrayManager
        tray_contents = self.controller.tray_manager.get_tray_contents()
        print(f"Toolbar: Current tray contents: {tray_contents}")

        if not tray_contents:
            print("Toolbar: Tray is empty, showing 'Delivery Tray' text")
            self.tray_canvas.create_text(
                (x0 + x1) / 2, 7 + self.tray_height / 2,
                text="Delivery Tray",
                font=("Helvetica", 9, "bold"),
                fill="#FFFFFF",
                tags="tray"
            )
        else:
            # Show item count if there are items
            item_count = self.controller.tray_manager.get_item_count()
            print(f"Toolbar: Tray has {item_count} items, showing count")
            self.tray_canvas.create_text(
                (x0 + x1) / 2, 7 + self.tray_height / 2,
                text=f"{item_count} Item(s)",
                font=("Helvetica", 9, "bold"),
                fill="#FFFFFF",
                tags="tray"
            )

        # Make tray clickable
        self.tray_canvas.tag_bind("tray", "<Button-1>", lambda event: self.open_tray_window())

    def animate_tray(self):
        if self.is_animating:
            return  # Prevent overlapping animations
        self.is_animating = True
        flash_count = 3
        flash_duration = 200  # ms

        def flash(step=0):
            if step >= flash_count * 2:
                self.tray_canvas.itemconfig("tray", fill=self.default_color)
                self.is_animating = False
                self.draw_tray()  # Redraw tray to update text
                return
            color = self.flash_color if step % 2 == 0 else self.default_color
            self.tray_canvas.itemconfig("tray", fill=color)
            self.tray_canvas.after(flash_duration, flash, step + 1)

        flash()

    def open_tray_window(self):
        print("Toolbar: Opening tray window")
        # Create a new Toplevel window
        tray_window = tk.Toplevel(self.container)
        tray_window.title("Delivery Tray Status")
        tray_window.geometry("300x250")
        tray_window.configure(bg="white")

        # Create a frame for the content
        content_frame = tk.Frame(tray_window, bg="white", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Get tray status from TrayManager
        tray_contents = self.controller.tray_manager.get_tray_contents()
        print(f"Toolbar: Tray contents for window: {tray_contents}")
        
        status_message, status_color = self.controller.tray_manager.format_tray_summary()
        print(f"Toolbar: Status message: {status_message}")

        # Display status
        status_label = tk.Label(
            content_frame,
            text=status_message,
            font=("Helvetica", 12),
            bg="white",
            fg=status_color,
            justify="left",
            wraplength=260
        )
        status_label.pack(pady=(0, 20))

        # Add collect button if there are items
        if tray_contents:
            print("Toolbar: Adding collect button")
            collect_btn = tk.Button(
                content_frame,
                text="Collect Items",
                command=lambda: self.collect_items(tray_window),
                bg="#4CAF50",
                fg="white",
                font=("Helvetica", 11, "bold"),
                activebackground="#45a049",
                activeforeground="white",
                padx=20,
                pady=10
            )
            collect_btn.pack(pady=(0, 10))

        # Close button
        close_btn = tk.Button(
            content_frame,
            text="Close",
            command=tray_window.destroy,
            bg="#8a0303",
            fg="white",
            font=("Helvetica", 10),
            activebackground="#463A87",
            padx=20,
            pady=5
        )
        close_btn.pack()

        # Make window modal
        tray_window.transient(self.container)
        tray_window.grab_set()
        self.container.wait_window(tray_window)

    def collect_items(self, window):
        print("Toolbar: Collecting items")
        # Clear tray contents using TrayManager
        self.controller.tray_manager.clear_tray()
        # Redraw tray
        self.draw_tray()
        # Close window
        window.destroy()
        print("Toolbar: Items collected, tray cleared")

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

        # Initialize TrayManager first
        self.tray_manager = TrayManager()
        print("Controller: TrayManager initialized")

        self.products = []
        self.selected = None
        self.amount = 0
        self.subtotal = tk.DoubleVar(self.container, 0)
        self.basket = {}
        self.state = states.CODE
        self.cash_window = None  # Track active cash window

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

        # Load products
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

        # Create UI components
        self.productList = ProductList(self.container, self)
        self.productList.pack(side="left", expand=1, fill="both", padx=(0, 4))

        self.display = tk.Frame(self.container, bg="white")
        self.display.pack(side="right", expand=1, fill="both", padx=(4, 0))

        self.keypad = Keypad(
            self.display,
            self,
        )
        self.keypad.pack(fill="x", padx=8, pady=8)
        
        # Initialize toolbar last, after TrayManager is set up
        self.toolbar = Toolbar(self.display, self)
        print("Controller: UI components initialized")

    def updateSubtotal(self, new):
        self.subtotal.set(round(self.subtotal.get() + new, 2))

    def setAmount(self, new):
        self.amount = int(new)

    def setSelected(self, new):
        self.selected = new

    def toggleLock(self, state):
        self.locked = state