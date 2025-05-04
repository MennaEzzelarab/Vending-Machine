import tkinter as tk
import states as states
from PIL import Image, ImageTk, ImageDraw

class ProductList(tk.Frame):
    def __init__(self, parent, c):
        tk.Frame.__init__(self, parent, bg="white", width=375, height=600)
        
        # Create top frame for refresh button
        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Add refresh button
        refresh_btn = tk.Button(
            top_frame,
            text="Refresh",
            command=self.refresh_products,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            font=("Helvetica", 10)
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg="white", width=375, height=600, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Store controller reference
        self.controller = c
        
        # Create product grid inside scrollable frame
        self.productGrid = tk.Frame(self.scrollable_frame, bg="white", width=375)
        self.productGrid.pack(fill="both", expand=True)

        # Bind mousewheel to scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind mousewheel when widget is destroyed
        def _on_destroy(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.bind("<Destroy>", _on_destroy)
        
        # Initial display of products
        self.display_products()
    
    def refresh_products(self):
        # Clear existing products
        self.controller.products.clear()
        
        # Reload products from database
        from database.database import productDB
        for product in productDB.all():
            try:
                self.controller.products.append(
                    ProductItem(
                        self.controller,
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
        
        # Clear and redisplay products
        for widget in self.productGrid.winfo_children():
            widget.destroy()
        self.display_products()
    
    def display_products(self):
        # Display products in a grid
        row = 0
        col = 0
        for index, product in enumerate(self.controller.products, start=1):
            try:
                # Product image
                tk.Label(self.productGrid, image=product.image, bd=0).grid(row=row, column=col, padx=5, pady=5)

                # Product code (using index instead of product.id)
                tk.Label(
                    self.productGrid,
                    bg="white",
                    text=str(index),
                    font="Helvetica 11 bold"
                ).grid(row=row, column=col, sticky="s", pady=(0,55))

                # Price / Label frame
                tk.Frame(self.productGrid, width=125, height=50, bg="#ECECEC").grid(row=row, column=col, sticky="s")

                # Price
                priceFrame = tk.Frame(self.productGrid, bg="#ECECEC", width=70, height=20)
                priceFrame.grid(row=row, column=col, sticky="sw", pady=(0, 22), padx=10)
                tk.Label(priceFrame, text="£", font=("Helvetica", 12, "bold"), bg="#ECECEC").grid(row=0, column=0, sticky="w")
                price = tk.Label(priceFrame, textvariable=product.price, fg="#191A1B", font=("Helvetica", 12, "bold"), bg="#ECECEC")
                price.grid(row=0, column=1, sticky="e", padx=(12, 0))

                # Label
                name = tk.Label(self.productGrid, bg="#ECECEC", textvariable=product.name, font=("Helvetica 9"))
                name.grid(row=row, column=col, sticky="sw", pady=(0, 6), padx=10)

                # Quantity Frame
                quantityFrame = tk.Frame(self.productGrid, bg="white", width=70, height=20)
                quantityFrame.grid(row=row, column=col, sticky="nw", pady=(8, 0), padx=10)

                # Quantity
                tk.Label(quantityFrame, text="Qty:", bg="white").grid(row=0, column=0, sticky="w")
                quantity = tk.Label(quantityFrame, bg="white", textvariable=product.quantity)
                quantity.grid(row=0, column=1, sticky="e", padx=32)

                # Update grid position
                col += 1
                if col >= 3:  # 3 products per row
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error displaying product {index}: {e}")
                continue


class ProductItem:
    def __init__(self, root, id_, name, path, quantity=0, price=0):
        self.id = id_
        self.name = tk.StringVar(root, str(name))
        self.price = tk.DoubleVar(root, price)
        self.quantity = tk.IntVar(root, int(quantity))
        
        # Load and resize image
        try:
            # Open the image and convert to RGBA
            img = Image.open(path).convert('RGBA')
            
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
            
            # Convert to PhotoImage
            self.image = ImageTk.PhotoImage(background)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            # Create a default image if loading fails
            default_img = Image.new('RGBA', (100, 100), (128, 128, 128, 255))
            d = ImageDraw.Draw(default_img)
            d.text((10, 40), "Product", fill='white')
            self.image = ImageTk.PhotoImage(default_img)
