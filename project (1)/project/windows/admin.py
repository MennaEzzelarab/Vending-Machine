from functools import partial
import tkinter as tk
from tkinter import messagebox, filedialog
from components.Toolbar import ToolbarButton
from windows.inventory import inventoryWindow
from windows.product import productsWindow
from PIL import Image, ImageTk
from windows.product import update_displayed_items
import os
from database.database import productDB  # Ensure productDB is imported from the correct module
from components.product import ProductItem, ProductList
import shutil


class Toolbar:
    def __init__(self, parent, c):
        self.container = tk.Frame(parent, height=20, bg="#ECECEC")
        self.container.pack(pady=(8, 0), padx=8, fill="x")

        # Inventory button
        ToolbarButton(
            self.container,
            text="Inventory status",
            command=partial(inventoryWindow, parent),
            image=c.chartImage,
            bg="#00BCD4",
            activebackground="#008BA3",
        ).pack(fill="x", pady=(0, 4))

        # Products button
        ToolbarButton(
            self.container,
            text="Products Database",
            command=partial(productsWindow, c, parent),
            image=c.productImage,
            bg="#7C4DFF",
            activebackground="#651FFF",
        ).pack(fill="x", pady=(0, 4))

        # Change Products button
        ToolbarButton(
            self.container,
            text="Change Products",
            command=partial(self.changeProductsWindow, c, parent),
            bg="#FF9800",
            activebackground="#FB8C00",
        ).pack(fill="x", pady=(0, 4))

    def changeProductsWindow(self, c, parent):
        # Create the Change Products window
        newWindow = tk.Toplevel(parent)
        newWindow.title("Manage Products")
        newWindow.minsize(600, 400)
        newWindow.configure(background="#ECECEC")

        # Create main canvas with scrollbar
        canvas = tk.Canvas(newWindow, bg="#ECECEC", highlightthickness=0)
        scrollbar = tk.Scrollbar(newWindow, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ECECEC")

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

        # Create main frame inside scrollable frame
        main_frame = tk.Frame(scrollable_frame, bg="#ECECEC", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Add Product Section
        add_frame = tk.LabelFrame(main_frame, text="Add New Product", bg="#ECECEC", font=("Arial", 12, "bold"))
        add_frame.pack(fill="x", pady=(0, 20))

        # Product name
        tk.Label(add_frame, text="Product Name:", bg="#ECECEC").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = tk.Entry(add_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Product price
        tk.Label(add_frame, text="Price (LE):", bg="#ECECEC").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        price_entry = tk.Entry(add_frame, width=30)
        price_entry.grid(row=1, column=1, padx=5, pady=5)

        # Product quantity
        tk.Label(add_frame, text="Quantity:", bg="#ECECEC").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        quantity_entry = tk.Entry(add_frame, width=30)
        quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        # Image selection
        tk.Label(add_frame, text="Product Image:", bg="#ECECEC").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        image_frame = tk.Frame(add_frame, bg="#ECECEC")
        image_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Image preview
        preview_label = tk.Label(image_frame, bg="#ECECEC")
        preview_label.pack(side="left", padx=(0, 10))
        
        # Selected image path
        selected_image = {"path": "assets/products/default.png"}
        
        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                try:
                    # Create products directory if it doesn't exist
                    os.makedirs("assets/products", exist_ok=True)
                    
                    # Copy image to products directory
                    filename = os.path.basename(file_path)
                    new_path = os.path.join("assets/products", filename)
                    shutil.copy2(file_path, new_path)
                    
                    # Load and resize image for preview
                    img = Image.open(new_path).convert('RGBA')
                    
                    # Calculate new dimensions while maintaining aspect ratio
                    target_width = 100  # Standard width for product images
                    target_height = 100  # Standard height for product images
                    
                    # Calculate aspect ratio
                    aspect_ratio = img.width / img.height
                    
                    if aspect_ratio > 1:  # Wider than tall
                        new_width = target_width
                        new_height = int(target_width / aspect_ratio)
                    else:  # Taller than wide
                        new_height = target_height
                        new_width = int(target_height * aspect_ratio)
                    
                    # Resize image with high-quality resampling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create a new image with white background
                    background = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 255))
                    
                    # Calculate position to center the resized image
                    x = (target_width - new_width) // 2
                    y = (target_height - new_height) // 2
                    
                    # Paste the resized image onto the background
                    background.paste(img, (x, y), img)
                    
                    # Update preview
                    photo = ImageTk.PhotoImage(background)
                    preview_label.configure(image=photo)
                    preview_label.image = photo
                    
                    # Update selected image path
                    selected_image["path"] = new_path
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {str(e)}")
        
        # Select image button
        select_image_btn = tk.Button(
            image_frame,
            text="Select Image",
            command=select_image,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white"
        )
        select_image_btn.pack(side="left")

        # Add button
        add_button = tk.Button(
            add_frame,
            text="Add Product",
            command=lambda: self.add_product(name_entry, price_entry, quantity_entry, product_listbox, selected_image),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white"
        )
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Product List Section
        list_frame = tk.LabelFrame(main_frame, text="Current Products", bg="#ECECEC", font=("Arial", 12, "bold"))
        list_frame.pack(fill="both", expand=True)

        # Create listbox with scrollbar
        list_scrollbar = tk.Scrollbar(list_frame)
        list_scrollbar.pack(side="right", fill="y")

        product_listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set, width=50, height=10)
        product_listbox.pack(side="left", fill="both", expand=True)
        list_scrollbar.config(command=product_listbox.yview)

        # Remove button
        remove_button = tk.Button(
            list_frame,
            text="Remove Selected",
            command=lambda: self.remove_product(product_listbox),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            activeforeground="white"
        )
        remove_button.pack(pady=10)

        # Populate the listbox with current products
        self.refresh_product_list(product_listbox)

        # Bind mousewheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Unbind mousewheel when window is closed
        def _on_closing():
            canvas.unbind_all("<MouseWheel>")
            newWindow.destroy()
        
        newWindow.protocol("WM_DELETE_WINDOW", _on_closing)

    def update_main_interface(self):
        # Get the controller instance from the parent window
        controller = None
        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if hasattr(child, 'products'):
                        controller = child
                        break
                if controller:
                    break

        if controller:
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

    def add_product(self, name_entry, price_entry, quantity_entry, product_listbox, selected_image):
        name = name_entry.get().strip()
        price = price_entry.get().strip()
        quantity = quantity_entry.get().strip()

        # Validate inputs
        if not name or not price or not quantity:
            tk.messagebox.showerror("Error", "All fields are required!")
            return

        try:
            price = float(price)
            quantity = int(quantity)
            if price <= 0 or quantity <= 0:
                raise ValueError
        except ValueError:
            tk.messagebox.showerror("Error", "Price and quantity must be positive numbers!")
            return

        # Check if product already exists
        existing_products = productDB.search(lambda x: x["name"] == name)
        if existing_products:
            tk.messagebox.showerror("Error", "Product with this name already exists!")
            return
        
        try:
            # Add product to database
            productDB.insert({
                "name": name,
                "price": price,
                "quantity": quantity,
                "displayed": True,
                "image": selected_image["path"]
            })

            # Clear entries
            name_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            quantity_entry.delete(0, tk.END)

            # Update the main interface
            self.update_main_interface()
            
            # Show success message
            tk.messagebox.showinfo("Success", "Product added successfully! Please click the Refresh button in the vending machine interface to see the changes.")
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to add product: {str(e)}")

    def remove_product(self, product_listbox):
        selection = product_listbox.curselection()
        if not selection:
            tk.messagebox.showerror("Error", "Please select a product to remove!")
            return

        # Get the selected product name from the listbox
        selected_text = product_listbox.get(selection[0])
        # Extract the product name (everything before the first " - ")
        product_name = selected_text.split(" - ")[0]

        if tk.messagebox.askyesno("Confirm", f"Are you sure you want to remove {product_name}?"):
            try:
                # Find the product in the database
                product = productDB.get(lambda x: x["name"] == product_name)
                if product:
                    # Remove the product from database
                    productDB.remove(doc_ids=[product.doc_id])
                    
                    # Try to remove the product image if it's not the default image
                    if product.get("image") and product["image"] != "assets/products/default.png":
                        try:
                            os.remove(product["image"])
                        except:
                            pass  # Ignore errors if image deletion fails
                    
                    # Update main interface
                    self.update_main_interface()
                    
                    # Show success message
                    tk.messagebox.showinfo("Success", "Product removed successfully! Please click the Refresh button in the vending machine interface to see the changes.")
                    
                else:
                    tk.messagebox.showerror("Error", "Product not found in database!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to remove product: {str(e)}")

    def refresh_product_list(self, product_listbox):
        product_listbox.delete(0, tk.END)
        for product in productDB.all():
            product_listbox.insert(tk.END, f"{product['name']} - LE {product['price']} (Qty: {product['quantity']})")
        # Force update of the listbox
        product_listbox.update_idletasks()
        product_listbox.update()


def adminWindow(parent, c):
    newWindow = tk.Toplevel(parent)
    newWindow.title("Admin")
    newWindow.minsize(450, 270) 
    width = 450
    height = 270

    # Calculate position x, y to center the window
    screen_width = newWindow.winfo_screenwidth()
    screen_height = newWindow.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    newWindow.geometry(f"{width}x{height}+{x}+{y}")
    newWindow.configure(background="#ECECEC", pady=10, padx=20)

    image = Image.open("./assets/icons/admin 3.png")
    image = image.resize((100, 100))

    # Convert the PIL Image to a Tkinter PhotoImage
    tk_image = ImageTk.PhotoImage(image)
    
    # Create a Tkinter label and set the image
    label = tk.Label(newWindow, image=tk_image)
    label.pack()
    Toolbar(newWindow, c)

    newWindow.transient(parent)
    newWindow.grab_set()
    parent.wait_window(newWindow)