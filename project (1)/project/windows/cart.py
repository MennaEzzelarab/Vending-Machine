import tkinter as tk
from lcd import typerwriter
from windows.receipt import receiptWindow

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

    newWindow = tk.Toplevel(parent)
    newWindow.title("Basket")
    newWindow.resizable(False, True)
    newWindow.geometry("660x470")
    newWindow.configure(background="white")

    # Sidebar
    sidebar = tk.Frame(newWindow, bg="#F3F3F3", padx=8, pady=10)
    sidebar.pack(fill="x")

    # Cart Header
    tk.Label(sidebar, fg="#191A1B", bg="#F3F3F3", text="Basket", font=("Helvetica", 18, "bold"), width=12).pack(
        pady=(0, 10))

    # Subtotal Header
    tk.Label(
        sidebar,
        fg="#191A1B",
        font="Helvetica 12 bold",
        text=str(f"Total: LE {round(c.subtotal.get(), 2)}"),
        anchor="w",
        width=12,
        bg="#F3F3F3"
    ).pack(side="top", fill="both")

    # Cart items
    if c.basket == {}:
        tk.Label(sidebar, text="Your cart is\ncurrently empty", bg="#F3F3F3", fg="#5C5C5C").pack(expand=True)
    else:
        for product in c.basket.values():
            cartItemFrame = tk.Frame(sidebar, bg="#F3F3F3")
            cartItemFrame.pack(fill="both", pady=(0, 2))

            infoFrame = tk.Frame(cartItemFrame, bg="#F3F3F3")
            infoFrame.pack(side="left")

            amountFrame = tk.Frame(cartItemFrame, bg="#F3F3F3")
            amountFrame.pack(side="right")

            tk.Label(infoFrame, bg="#F3F3F3", text=product["name"], anchor="w", font="Helvetica 10 bold").pack(
                fill="both")
            tk.Label(infoFrame, bg="#F3F3F3", text=str(f"LE {round(product['price'], 2)}"), anchor="w").pack(
                fill="both")

            tk.Label(amountFrame, text=str(f"x{product['amount']}"), bg="#F3F3F3").pack()

    # Buttons frame
    buttonsFrame = tk.Frame(newWindow, bg="white")
    buttonsFrame.pack(fill="x", expand=True)

    # Top Frame
    top = tk.Frame(buttonsFrame)
    top.pack(fill="both", expand=True)

    # Bottom Right Frame
    bottomRight = tk.Frame(buttonsFrame)
    bottomRight.pack(fill="both", side="right", expand=True)

    # Bottom Left Frame
    bottomLeft = tk.Frame(buttonsFrame)
    bottomLeft.pack(fill="both", side="left", expand=True)

    # Reset cart states on cancel
    def cancel():

        if c.cart.get() > 0:
            typerwriter(c, messages)

            c.basket = {}
            c.subtotal.set(0)
            c.cart.set(0)

        newWindow.destroy()
        newWindow.update()

    # When the user clicks the pay button, a receipt window opens
    def pay():
        receiptWindow(config, parent, c)
        newWindow.destroy()
        newWindow.update()

    # Destroy the current window and enable the user to continue shopping
    def addAnother():
        newWindow.destroy()
        newWindow.update()

    # Add another button
    CartButton(
        bottomLeft,
        text="Add Another Item",
        command=addAnother,
        bg="#00FF00",
        activebackground="#00FF00",
        image=continueIcon
    ).pack(fill="both", pady=(4, 4), expand=True)

    # Finish and Pay button
    CartButton(
        bottomLeft,
        text="Pay",
        command=pay,
        bg="#5DCB6B",
        activebackground="#66E877",
        image=payIcon
    ).pack(fill="both", pady=(4, 4), expand=True)

    # Cancel Button
    CartButton(
        bottomRight,
        command=cancel,
        text="Cancel Order",
        bg="#D83F3F",
        activebackground="#EB5151",
        image=cancelIcon
    ).pack(fill="both", pady=(4, 4), expand=True)

    newWindow.transient(parent)
    newWindow.grab_set()
