import tkinter as tk
from PIL import Image, ImageTk
from components.Toolbar import ToolbarButton
from functools import partial

class PaymentWindow:
    def __init__(self, parent, product, on_payment_complete):
        self.window = tk.Toplevel(parent)
        self.window.title("Payment")
        self.window.minsize(400, 500)
        self.window.configure(background="#ECECEC")
        
        # Store references
        self.parent = parent
        self.product = product
        self.on_payment_complete = on_payment_complete
        
        # Calculate position to center the window
        width = 400
        height = 500
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create main frame
        main_frame = tk.Frame(self.window, bg="#ECECEC", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Product info
        product_frame = tk.LabelFrame(main_frame, text="Product Details", bg="#ECECEC", font=("Arial", 12, "bold"))
        product_frame.pack(fill="x", pady=(0, 20))
        
        # Product image
        try:
            img = Image.open(product.get("image", "assets/products/default.png"))
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(product_frame, image=photo, bg="#ECECEC")
            img_label.image = photo
            img_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading product image: {e}")
        
        # Product name and price
        tk.Label(product_frame, text=product["name"], font=("Arial", 14, "bold"), bg="#ECECEC").pack()
        tk.Label(product_frame, text=f"Price: £{product['price']:.2f}", font=("Arial", 12), bg="#ECECEC").pack(pady=5)
        
        # Payment section
        payment_frame = tk.LabelFrame(main_frame, text="Enter Payment", bg="#ECECEC", font=("Arial", 12, "bold"))
        payment_frame.pack(fill="x", pady=(0, 20))
        
        # Currency input
        self.amount_var = tk.StringVar()
        self.amount_var.trace('w', self.validate_amount)
        
        amount_frame = tk.Frame(payment_frame, bg="#ECECEC")
        amount_frame.pack(pady=10)
        
        tk.Label(amount_frame, text="£", font=("Arial", 14), bg="#ECECEC").pack(side="left")
        amount_entry = tk.Entry(amount_frame, textvariable=self.amount_var, font=("Arial", 14), width=10)
        amount_entry.pack(side="left", padx=5)
        
        # Quick amount buttons
        quick_amounts_frame = tk.Frame(payment_frame, bg="#ECECEC")
        quick_amounts_frame.pack(pady=10)
        
        amounts = [0.50, 1.00, 2.00, 5.00, 10.00]
        for amount in amounts:
            btn = tk.Button(
                quick_amounts_frame,
                text=f"£{amount:.2f}",
                command=lambda a=amount: self.add_amount(a),
                bg="#4CAF50",
                fg="white",
                activebackground="#45a049",
                activeforeground="white",
                width=8
            )
            btn.pack(side="left", padx=5)
        
        # Total and change
        self.total_var = tk.StringVar(value="£0.00")
        self.change_var = tk.StringVar(value="£0.00")
        
        total_frame = tk.Frame(payment_frame, bg="#ECECEC")
        total_frame.pack(pady=10)
        
        tk.Label(total_frame, text="Total Paid:", font=("Arial", 12), bg="#ECECEC").pack(side="left")
        tk.Label(total_frame, textvariable=self.total_var, font=("Arial", 12, "bold"), bg="#ECECEC").pack(side="left", padx=5)
        
        change_frame = tk.Frame(payment_frame, bg="#ECECEC")
        change_frame.pack(pady=5)
        
        tk.Label(change_frame, text="Change:", font=("Arial", 12), bg="#ECECEC").pack(side="left")
        tk.Label(change_frame, textvariable=self.change_var, font=("Arial", 12, "bold"), bg="#ECECEC").pack(side="left", padx=5)
        
        # Pay button
        self.pay_button = tk.Button(
            main_frame,
            text="Pay",
            command=self.process_payment,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.pay_button.pack(pady=20)
        
        # Cancel button
        cancel_button = tk.Button(
            main_frame,
            text="Cancel",
            command=self.window.destroy,
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            activeforeground="white",
            font=("Arial", 12)
        )
        cancel_button.pack()
        
        # Set focus to amount entry
        amount_entry.focus()
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
    
    def validate_amount(self, *args):
        try:
            amount = float(self.amount_var.get() or 0)
            if amount < 0:
                self.amount_var.set("0")
                amount = 0
            self.total_var.set(f"£{amount:.2f}")
            
            # Calculate change
            change = amount - self.product["price"]
            self.change_var.set(f"£{change:.2f}")
            
            # Enable/disable pay button
            self.pay_button.configure(state="normal" if amount >= self.product["price"] else "disabled")
        except ValueError:
            self.amount_var.set("0")
    
    def add_amount(self, amount):
        try:
            current = float(self.amount_var.get() or 0)
            self.amount_var.set(f"{current + amount:.2f}")
        except ValueError:
            self.amount_var.set(f"{amount:.2f}")
    
    def process_payment(self):
        try:
            amount = float(self.amount_var.get())
            if amount >= self.product["price"]:
                self.on_payment_complete(amount)
                self.window.destroy()
        except ValueError:
            pass

def paymentWindow(parent, product, on_payment_complete):
    PaymentWindow(parent, product, on_payment_complete)
    parent.wait_window() 