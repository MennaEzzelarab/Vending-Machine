import tkinter as tk
from tinydb import TinyDB
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from components.product import ProductItem, ProductList

productDB = TinyDB("database/product.json")
MAX_ITEMS_PER_PRODUCT = 30  # Adjust based on vending machine capacity

# Popup window to display warning messages
def popupWindow(parent, message):
    newWindow = tk.Toplevel(parent)
    newWindow.title("Message")
    window_width = 400
    window_height = 150
    center_window(newWindow, window_width, window_height)
    newWindow.resizable(False, False)
    newWindow.configure(background="white")

    # Message label with nicer font and padding
    msg_label = tk.Label(
        newWindow,
        text=message,
        bg="white",
        font=("Helvetica", 12),
        wraplength=380,
        justify="center",
        padx=20,
        pady=20
    )
    msg_label.pack(expand=True, fill="both")

    # OK button to close popup
    ok_button = tk.Button(
        newWindow,
        text="OK",
        command=newWindow.destroy,
        width=10,
        bg="#2780B4",
        fg="white",
        font=("Helvetica", 11, "bold"),
        activebackground="#2d88bc",
        activeforeground="white",
        border=0,
        cursor="hand2",
        pady=5
    )
    ok_button.pack(pady=(0, 15))

    newWindow.transient(parent)
    newWindow.grab_set()
    parent.wait_window(newWindow)


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def update_main_interface(controller):
    """Update the main interface with the latest product data"""
    if not controller:
        return

    try:
        # Clear existing products
        controller.products.clear()
        
        # Reload products from database
        for product in productDB.all():
            try:
                controller.products.append(
                    ProductItem(
                        controller,
                        product.doc_id,
                        product["name"],
                        product.get("image", "assets/products/default.png"),
                        product["quantity"],
                        product["price"],
                    )
                )
            except Exception as e:
                print(f"Error loading product {product['name']}: {e}")
                continue
        
        # Refresh the product list display
        if hasattr(controller, 'productList'):
            controller.productList.destroy()
        controller.productList = ProductList(controller.container, controller)
        controller.productList.pack(side="right", expand=1, fill="both", padx=(0, 4))
        
        # Force update of the display
        controller.update_idletasks()
        controller.update()
        
    except Exception as e:
        print(f"Error updating main interface: {e}")

def productsWindow(c, parent):
    saveImage = tk.PhotoImage(file="assets/icons/save.png")
    
    newWindow = tk.Toplevel(parent)
    newWindow.title("Products Database")
    window_width = 800
    window_height = 600
    center_window(newWindow, window_width, window_height)
    newWindow.resizable(False, False)
    newWindow.configure(background="white")

    # Create main frame
    main_frame = tk.Frame(newWindow, bg="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create canvas and scrollbar
    canvas = tk.Canvas(main_frame, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    # Configure canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Dictionary to store entry fields
    productEntries = {}

    def refresh_products():
        # Clear existing entries
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        productEntries.clear()

        # Reload products from database
        for product in productDB.all():
            create_product_entry(product)

    def create_product_entry(product):
        # Create frame for each product
        product_frame = tk.Frame(scrollable_frame, bg="white", pady=10)
        product_frame.pack(fill="x", padx=10)

        # Product image
        try:
            img = Image.open(product.get("image", "assets/products/default.png"))
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(product_frame, image=photo, bg="white")
            img_label.image = photo
            img_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Error loading image for {product['name']}: {e}")

        # Product name
        name_frame = tk.Frame(product_frame, bg="white")
        name_frame.pack(side="left", fill="x", expand=True)
        tk.Label(name_frame, text="Name:", bg="white").pack(side="left", padx=(0, 5))
        name_entry = tk.Entry(name_frame, width=20)
        name_entry.insert(0, product["name"])
        name_entry.pack(side="left")

        # Price
        price_frame = tk.Frame(product_frame, bg="white")
        price_frame.pack(side="left", fill="x", expand=True)
        tk.Label(price_frame, text="Price:", bg="white").pack(side="left", padx=(0, 5))
        price_entry = tk.Entry(price_frame, width=10)
        price_entry.insert(0, str(product["price"]))
        price_entry.pack(side="left")

        # Quantity
        quantity_frame = tk.Frame(product_frame, bg="white")
        quantity_frame.pack(side="left", fill="x", expand=True)
        tk.Label(quantity_frame, text="Quantity:", bg="white").pack(side="left", padx=(0, 5))
        quantity_entry = tk.Entry(quantity_frame, width=10)
        quantity_entry.insert(0, str(product["quantity"]))
        quantity_entry.pack(side="left")

        # Store entries in dictionary
        productEntries[product.doc_id] = {
            "name": name_entry,
            "price": price_entry,
            "quantity": quantity_entry
        }

    # Initial load of products
    refresh_products()

    def onSave():
        # First, validate all entries
        for doc_id, field in productEntries.items():
            try:
                quantity = int(field["quantity"].get())
                price = float(field["price"].get())
                name = field["name"].get()

                if quantity < 0 or price < 0:
                    popupWindow(newWindow, f"Negative values are not allowed for '{name}'. Please correct it.")
                    return  # Stop saving

                if quantity > MAX_ITEMS_PER_PRODUCT:
                    popupWindow(newWindow, f"{name} exceeds the maximum limit of {MAX_ITEMS_PER_PRODUCT} items. Please correct it.")
                    return  # Stop saving

            except ValueError:
                popupWindow(newWindow, f"Invalid input for '{field['name'].get()}'. Please correct it.")
                return  # Stop saving

        # If validation passed for all, save all products
        for doc_id, field in productEntries.items():
            quantity = int(field["quantity"].get())
            price = float(field["price"].get())
            name = field["name"].get()

            # Update in database
            productDB.update({
                "name": name,
                "quantity": quantity,
                "price": price
            }, doc_ids=[doc_id])

        # Update the main interface
        update_main_interface(c)
        
        # Show success message
        popupWindow(newWindow, "Products saved successfully.")
        
        # Close and reopen the window
        newWindow.destroy()
        productsWindow(c, parent)

    # Buttons frame
    button_frame = tk.Frame(newWindow, bg="white")
    button_frame.pack(fill="x", pady=10, padx=10)

    # Save button
    save_button = tk.Button(
        button_frame,
        image=saveImage,
        text="Save Changes",
        compound="left",
        command=onSave,
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 11, "bold"),
        activebackground="#45a049",
        activeforeground="white",
        border=0,
        cursor="hand2",
        pady=5,
        padx=10
    )
    save_button.pack(side="right")

    # Refresh button
    refresh_button = tk.Button(
        button_frame,
        text="Refresh",
        command=refresh_products,
        bg="#2196F3",
        fg="white",
        font=("Helvetica", 11, "bold"),
        activebackground="#1976D2",
        activeforeground="white",
        border=0,
        cursor="hand2",
        pady=5,
        padx=10
    )
    refresh_button.pack(side="right", padx=(0, 10))

    def _on_mousewheel(event):
        try:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except tk.TclError:
            pass  # Ignore errors if canvas is destroyed

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    # Bind mousewheel events
    canvas.bind("<Enter>", _bind_mousewheel)
    canvas.bind("<Leave>", _unbind_mousewheel)

    # Unbind mousewheel when window is closed
    def _on_closing():
        try:
            canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        newWindow.destroy()
    
    newWindow.protocol("WM_DELETE_WINDOW", _on_closing)

    newWindow.transient(parent)
    newWindow.grab_set()
    parent.wait_window(newWindow)

def changeProductsWindow(c, parent):
    newWindow = tk.Toplevel(parent)
    newWindow.title("Change Products")
    newWindow.minsize(500, 400)

    # Example layout for managing products
    tk.Label(newWindow, text="Manage Products", font=("Arial", 16)).pack(pady=10)

    # Add product section
    tk.Label(newWindow, text="Add Product:").pack(anchor="w", padx=10)
    add_entry = tk.Entry(newWindow, width=40)
    add_entry.pack(padx=10, pady=5)
    tk.Button(newWindow, text="Add", command=lambda: add_product(add_entry.get())).pack(pady=5)

    # Remove product section
    tk.Label(newWindow, text="Remove Product:").pack(anchor="w", padx=10)
    remove_entry = tk.Entry(newWindow, width=40)
    remove_entry.pack(padx=10, pady=5)
    tk.Button(newWindow, text="Remove", command=lambda: remove_product(remove_entry.get())).pack(pady=5)

    # Close button
    tk.Button(newWindow, text="Close", command=newWindow.destroy).pack(pady=20)

    def add_product(product_name):
        if product_name:
            # Logic to add the product
            messagebox.showinfo("Success", f"Product '{product_name}' added successfully!")
        else:
            messagebox.showerror("Error", "Product name cannot be empty.")

    def remove_product(product_name):
        if product_name:
            # Logic to remove the product
            messagebox.showinfo("Success", f"Product '{product_name}' removed successfully!")
        else:
            messagebox.showerror("Error", "Product name cannot be empty.")

def update_displayed_items(displayed_items):
    # Logic to update the displayed items in the product view
    print("Updated Displayed Items:", displayed_items)

    # Example: Refresh the product view (implement this based on your UI logic)
    # This could involve reloading the product list in the UI
    # For example:
    # product_view.refresh(displayed_items)