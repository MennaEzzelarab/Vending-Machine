import tkinter as tk
from tkinter import ttk
from payment import finishAndPay
import states as states

def openCurrencyWindow(c):
    # Prevent multiple windows
    if c.cash_window is not None and c.cash_window.winfo_exists():
        return

    c.toggleLock(True)  # Lock keypad
    win = tk.Toplevel()
    c.cash_window = win  # Track window
    win.title("Insert Cash")
    win.geometry("400x600")  # Increased size
    win.configure(bg="white")
    win.minsize(350, 500)  # Set minimum size
    win.resizable(True, True)  # Allow resizing

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

    inserted = tk.DoubleVar(value=0.0)
    subtotal = c.subtotal.get()

    def insert(amount):
        current = inserted.get() + amount
        inserted.set(current)
        if current >= subtotal:
            win.destroy()
            success = finishAndPay(c, current, "cash")
            if success:
                print("Payment successful, preparing to add items to tray")
                # Prepare items for tray
                items = []
                for item_id, item in c.basket.items():
                    tray_item = {
                        "name": item["name"],
                        "amount": item["amount"],
                        "price": item["price"]
                    }
                    items.append(tray_item)
                    print(f"Prepared item for tray: {tray_item}")
                
                # Add items to tray using TrayManager
                c.tray_manager.add_items(items)
                
                # Force redraw tray
                c.toolbar.draw_tray()
                
                # Trigger tray animation
                c.toolbar.animate_tray()
                
                # Reset other states
                c.basket = {}  # Clear basket
                c.subtotal.set(0)  # Reset subtotal
                c.cart.set(0)  # Reset cart count
                c.screenMessage.set("Enter Item Code")  # Reset display
                c.state = states.CODE  # Reset state
                c.toggleLock(False)  # Unlock keypad
                c.cash_window = None  # Clear window reference

    # Add title with icon
    title_frame = tk.Frame(content_frame, bg="white")
    title_frame.pack(fill="x", pady=(0, 20))

    tk.Label(
        title_frame,
        text="Insert Cash",
        font=("Helvetica", 24, "bold"),
        bg="white"
    ).pack()

    tk.Label(
        title_frame,
        text="Please insert the required amount",
        font=("Helvetica", 12),
        bg="white",
        fg="#666666"
    ).pack(pady=(5, 0))

    # Add amount display with better styling
    amount_frame = tk.Frame(content_frame, bg="white")
    amount_frame.pack(fill="x", pady=20)
    
    # Amount inserted
    inserted_frame = tk.Frame(amount_frame, bg="white")
    inserted_frame.pack(fill="x", pady=5)
    
    tk.Label(
        inserted_frame,
        text="Amount Inserted:",
        font=("Helvetica", 14),
        bg="white",
        fg="#666666"
    ).pack(side="left")
    
    tk.Label(
        inserted_frame,
        textvariable=inserted,
        font=("Helvetica", 14, "bold"),
        bg="white"
    ).pack(side="right")

    # Total amount
    total_frame = tk.Frame(amount_frame, bg="white")
    total_frame.pack(fill="x", pady=5)
    
    tk.Label(
        total_frame,
        text="Total Amount:",
        font=("Helvetica", 14),
        bg="white",
        fg="#666666"
    ).pack(side="left")
    
    tk.Label(
        total_frame,
        text=f"LE {subtotal:.2f}",
        font=("Helvetica", 14, "bold"),
        bg="white"
    ).pack(side="right")

    # Add separator
    ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=20)

    # Add denomination buttons with better styling
    denominations_frame = tk.Frame(content_frame, bg="white")
    denominations_frame.pack(fill="x", pady=10)

    # Add denomination buttons in a grid
    denominations = [0.5, 1, 5, 10, 20, 50, 100]
    for i, amount in enumerate(denominations):
        btn = tk.Button(
            denominations_frame,
            text=f"LE {amount:.2f}",
            command=lambda a=amount: insert(a),
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=8,
            height=2,
            cursor="hand2",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat"
        )
        btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")

    # Configure grid weights
    for i in range(3):
        denominations_frame.grid_columnconfigure(i, weight=1)

    # Add cancel button with better styling
    cancel_btn = tk.Button(
        content_frame,
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
    cancel_btn.pack(pady=20, fill="x")

    # Bind mousewheel to scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Unbind mousewheel when widget is destroyed
    def _on_destroy(event):
        canvas.unbind_all("<MouseWheel>")
    
    win.bind("<Destroy>", _on_destroy)

    # Make window modal
    win.transient(c)
    win.grab_set()
    c.wait_window(win) 