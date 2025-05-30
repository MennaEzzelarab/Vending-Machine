import tkinter as tk
from tkinter import ttk
from lcd import typerwriter
from windows.receipt import receiptWindow
import states as states

messages = [
    "Sorry, we could not\nprovide you with\nyour choice today",
    "We hope to see\nyou soon again :)",
    "Have a good day!"
]


# Cart button class
class CartButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(
            self,
            parent,
            fg="#F0F0F0",
            activeforeground="#F0F0F0",
            font=("Helvetica", 12, "bold"),
            cursor="hand1",
            bd=0,
            relief="flat",
            borderwidth=0,
            pady=10,
            compound="top",
            *args,
            **kwargs
        )


def cartWindow(config):
    c = config["controller"]
    parent = config["parent"]
    payIcon = config["payIcon"]
    cancelIcon = config["cancelIcon"]
    continueIcon = config["continueIcon"]

    win = tk.Toplevel()
    win.title("Cart")
    win.geometry("350x700")  # Reduced width
    win.configure(bg="white")
    win.minsize(350, 500)  # Reduced minimum width
    win.resizable(True, True)  # Allow resizing

    # Create main container with padding
    main_container = tk.Frame(win, bg="white", padx=15, pady=20)  # Reduced padding
    main_container.pack(fill="both", expand=True)

    # Create canvas and scrollbar for vertical scrolling
    canvas = tk.Canvas(main_container, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    
    # Create scrollable frame
    content_frame = tk.Frame(canvas, bg="white")
    
    # Configure canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    scrollbar.pack_forget()  # Hide the scrollbar
    
    # Create window in canvas
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", width=canvas.winfo_width())
    
    # Update scroll region when content changes
    def _configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Update the width of the frame to match canvas
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind('<Configure>', _configure_canvas)
    content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Add title with icon
    title_frame = tk.Frame(content_frame, bg="white")
    title_frame.pack(fill="x", pady=(0, 20))

    tk.Label(
        title_frame,
        text="Your Cart",
        font=("Helvetica", 24, "bold"),  # Slightly smaller title
        bg="white"
    ).pack()

    tk.Label(
        title_frame,
        text="Review your items before checkout",
        font=("Helvetica", 12),  # Slightly smaller subtitle
        bg="white",
        fg="#666666"
    ).pack(pady=(5, 0))

    # Create items container
    items_container = tk.Frame(content_frame, bg="white")
    items_container.pack(fill="both", expand=True, pady=10)

    # Add items to cart with better styling
    for item_id, item in c.basket.items():
        item_frame = tk.Frame(items_container, bg="white", pady=8)  # Reduced padding
        item_frame.pack(fill="x", pady=3)  # Reduced padding
        
        # Item name and amount
        name_frame = tk.Frame(item_frame, bg="white")
        name_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            name_frame,
            text=item['name'],
            font=("Helvetica", 12),  # Slightly smaller font
            bg="white",
            justify="left"
        ).pack(side="left")
        
        tk.Label(
            name_frame,
            text=f"x{item['amount']}",
            font=("Helvetica", 12),  # Slightly smaller font
            bg="white",
            fg="#666666"
        ).pack(side="left", padx=(5, 0))
        
        # Item price
        price_frame = tk.Frame(item_frame, bg="white")
        price_frame.pack(side="right")
        
        tk.Label(
            price_frame,
            text=f"LE {item['price'] * item['amount']:.2f}",
            font=("Helvetica", 12),  # Slightly smaller font
            bg="white",
            justify="right"
        ).pack(side="right")

    # Add separator line
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=20)

    # Add total with better styling
    total_frame = tk.Frame(content_frame, bg="white")
    total_frame.pack(fill="x", pady=10)
    
    tk.Label(
        total_frame,
        text="Total:",
        font=("Helvetica", 14, "bold"),  # Slightly smaller font
        bg="white"
    ).pack(side="left")
    
    tk.Label(
        total_frame,
        text=f"LE {c.subtotal.get():.2f}",
        font=("Helvetica", 14, "bold"),  # Slightly smaller font
        bg="white"
    ).pack(side="right")

    # Add buttons with better styling
    button_frame = tk.Frame(content_frame, bg="white")
    button_frame.pack(fill="x", pady=20)

    # Checkout button with hover effect
    checkout_button = tk.Button(
        button_frame,
        text="Checkout",
        command=lambda: handle_checkout(win, c),
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 12, "bold"),
        cursor="hand2",
        activebackground="#45a049",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=10
    )
    checkout_button.pack(fill="x", pady=(0, 5))

    # Continue Shopping button with hover effect
    continue_button = tk.Button(
        button_frame,
        text="Continue Shopping",
        command=win.destroy,
        bg="#2196F3",
        fg="white",
        font=("Helvetica", 12, "bold"),
        cursor="hand2",
        activebackground="#1976D2",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=10
    )
    continue_button.pack(fill="x", pady=(0, 5))

    # Cancel Order button with hover effect
    cancel_button = tk.Button(
        button_frame,
        text="Cancel Order",
        command=lambda: handle_cancel_order(win, c),
        bg="#f44336",
        fg="white",
        font=("Helvetica", 12, "bold"),
        cursor="hand2",
        activebackground="#da190b",
        activeforeground="white",
        relief="flat",
        padx=10,
        pady=10
    )
    cancel_button.pack(fill="x")

    # Bind mousewheel to scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Unbind mousewheel when widget is destroyed
    def _on_destroy(event):
        canvas.unbind_all("<MouseWheel>")
    
    win.bind("<Destroy>", _on_destroy)

    # Make window modal
    win.transient(parent)
    win.grab_set()
    parent.wait_window(win)

def handle_checkout(win, c):
    win.destroy()
    # Open receipt window after cart is closed
    receiptWindow({"controller": c, "parent": c})

def handle_cancel_order(win, c):
    # Clear the basket
    c.basket = {}
    c.subtotal.set(0)
    c.cart.set(0)
    # Close the window
    win.destroy()
