import tkinter as tk
from PIL import Image, ImageTk
from windows.admin import adminWindow

def loginWindow(parent, c):
    newWindow = tk.Toplevel(parent)
    newWindow.title("Admin")
    newWindow.configure(bg="#ECECEC")  # Set window bg
    width = 400
    height = 300
    newWindow.geometry(f"{width}x{height}")
    newWindow.minsize(500, 500)  # Prevent window from being resized smaller

    newWindow.update_idletasks()  # Force geometry calculation
    actual_width = newWindow.winfo_width()
    actual_height = newWindow.winfo_height()
    x = (newWindow.winfo_screenwidth() // 2) - (actual_width // 2)
    y = (newWindow.winfo_screenheight() // 2) - (actual_height // 2)
    newWindow.geometry(f"{width}x{height}+{x}+{y}")
    
    frame = tk.Frame(newWindow, bg="#ECECEC")
    frame.pack(fill="both", expand=True, pady=20)  # Fill entire window

    # Center the frame content if you want
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Center the frame
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    try:
        logo_img = Image.open("assets/icons/vending.png")
        logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        newWindow.logo_photo = logo_photo  
        logo_label = tk.Label(frame, image=logo_photo, bg="#ECECEC")
        logo_label.image = logo_photo
        logo_label.pack(pady=(0, 10))   
    except Exception as e:
        print(f"Error loading image: {e}")
        logo_label = tk.Label(frame, text="Logo", bg="#ECECEC")
        logo_label.pack(pady=(0, 10))     
    

    # Login form
    tk.Label(frame, text="Vending Machine\nAdmin Login", bg="#ECECEC", font=("Helvetica", 20, "bold"), justify="center").pack(pady=15)

    username = tk.StringVar()
    password = tk.StringVar()

    label_style = {"bg": "#ECECEC", "font": ("Helvetica", 12)}
    entry_style = {"bd": 2, "relief": "groove", "font": ("Helvetica", 12)}

    tk.Label(frame, text="Username", **label_style).pack(anchor="w", padx=20)
    tk.Entry(frame, textvariable=username, **entry_style).pack(fill="x", padx=20, pady=(0,10))

    tk.Label(frame, text="Password", **label_style).pack(anchor="w", padx=20)
    tk.Entry(frame, textvariable=password, show="#", **entry_style).pack(fill="x", padx=20, pady=(0,10))


    error_var = tk.StringVar()
    error_label = tk.Label(
    frame,
    textvariable=error_var,
    fg="red",
    bg="#ECECEC",
    font=("Helvetica", 11),
    wraplength=280,       # Wrap text at ~280 pixels width
    justify="center",     # Center multi-line text
    anchor="center"       # Center text horizontally in label
)
    error_label.pack(pady=(0, 5))

    def login():
        user = username.get().strip()
        pwd = password.get().strip()
        # Empty field validation
        if not user or not pwd:
            error_var.set("Please enter both username and password.")
            return
        # Username/password check
        if user == "admin" and pwd == "1234":
            error_var.set("")  # Clear any previous error
            print("Logging in")
            adminWindow(newWindow, c)
            newWindow.destroy()
        else:
            error_var.set("Invalid username or password.")



    #tk.Button(frame, text="Login",bg="#0d1137",fg="white" ,command=login).pack(pady=10)
    login_button = tk.Button(frame, text="Login", bg="#0d1137", fg="white", font=("Helvetica", 14, "bold"), command=login)
    login_button.pack(pady=20, ipadx=10, ipady=5)

    # Optional: add hover effect
    def on_enter(e):
        login_button['bg'] = '#1a237e'  # Darker blue

    def on_leave(e):
        login_button['bg'] = '#0d1137'  # Original color

    login_button.bind("<Enter>", on_enter)
    login_button.bind("<Leave>", on_leave)
    newWindow.bind('<Return>', lambda event: login())

    newWindow.transient(parent)
    newWindow.grab_set()
    parent.wait_window(newWindow)