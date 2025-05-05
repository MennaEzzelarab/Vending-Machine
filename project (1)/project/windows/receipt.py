import tkinter as tk
from tkinter import ttk
import states as states
from windows.payment_handler import openCurrencyWindow


def receiptWindow(config):
    c = config["controller"]
    parent = config["parent"]
    win = tk.Toplevel()
    win.title("Receipt")
    win.geometry("400x600")  # Increased size
    win.configure(bg="white")
    win.minsize(400, 500)  # Set minimum size

    # Create main container with padding
    main_container = tk.Frame(win, bg="white", padx=20, pady=20)
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

    # Create window in canvas
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", width=canvas.winfo_width())
    
    # Update scroll region when content changes
    def _configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Update the width of the frame to match canvas
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind('<Configure>', _configure_canvas)
    content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Add receipt header with store info
    header_frame = tk.Frame(content_frame, bg="white")
    header_frame.pack(fill="x", pady=(0, 20))

    # Store name
    tk.Label(
        header_frame,
        text="Vending Machine",
        font=("Helvetica", 20, "bold"),
        bg="white"
    ).pack()

    # Date and time
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tk.Label(
        header_frame,
        text=current_time,
        font=("Helvetica", 10),
        bg="white",
        fg="#666666"
    ).pack(pady=(5, 0))

    # Receipt title
    tk.Label(
        content_frame,
        text="Receipt",
        font=("Helvetica", 16, "bold"),
        bg="white"
    ).pack(pady=(0, 20))

    # Add items to receipt with better styling
    for item_id, item in c.basket.items():
        item_frame = tk.Frame(content_frame, bg="white")
        item_frame.pack(fill="x", pady=5)
        
        # Item name and amount
        name_frame = tk.Frame(item_frame, bg="white")
        name_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(
            name_frame,
            text=item['name'],
            font=("Helvetica", 11),
            bg="white",
            justify="left"
        ).pack(side="left")
        
        tk.Label(
            name_frame,
            text=f"x{item['amount']}",
            font=("Helvetica", 11),
            bg="white",
            fg="#666666"
        ).pack(side="left", padx=(5, 0))
        
        # Item price
        price_frame = tk.Frame(item_frame, bg="white")
        price_frame.pack(side="right")
        
        tk.Label(
            price_frame,
            text=f"LE {item['price'] * item['amount']:.2f}",
            font=("Helvetica", 11),
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
        font=("Helvetica", 14, "bold"),
        bg="white"
    ).pack(side="left")
    
    tk.Label(
        total_frame,
        text=f"LE {c.subtotal.get():.2f}",
        font=("Helvetica", 14, "bold"),
        bg="white"
    ).pack(side="right")

    # Add payment method with better styling
    payment_frame = tk.Frame(content_frame, bg="white")
    payment_frame.pack(fill="x", pady=10)
    
    tk.Label(
        payment_frame,
        text="Payment Method:",
        font=("Helvetica", 11),
        bg="white",
        fg="#666666"
    ).pack(side="left")
    
    tk.Label(
        payment_frame,
        text="Cash",
        font=("Helvetica", 11, "bold"),
        bg="white"
    ).pack(side="right")

    # Add thank you message
    tk.Label(
        content_frame,
        text="Thank you for your purchase!",
        font=("Helvetica", 12),
        bg="white",
        fg="#666666"
    ).pack(pady=20)

    # Add buttons with better styling
    button_frame = tk.Frame(content_frame, bg="white")
    button_frame.pack(fill="x", pady=20)

    # Pay button with hover effect
    pay_button = tk.Button(
        button_frame,
        text="Pay",
        command=lambda: handle_payment(win, c),
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 12, "bold"),
        width=15,
        height=2,
        cursor="hand2",
        activebackground="#45a049",
        activeforeground="white",
        relief="flat"
    )
    pay_button.pack(side="left", padx=5, expand=True, fill="x")

    # Cancel button with hover effect
    cancel_button = tk.Button(
        button_frame,
        text="Cancel",
        command=win.destroy,
        bg="#f44336",
        fg="white",
        font=("Helvetica", 12, "bold"),
        width=15,
        height=2,
        cursor="hand2",
        activebackground="#da190b",
        activeforeground="white",
        relief="flat"
    )
    cancel_button.pack(side="right", padx=5, expand=True, fill="x")

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

def handle_payment(win, c):
    win.destroy()
    # Open cash window after receipt is closed
    openCurrencyWindow(c)
