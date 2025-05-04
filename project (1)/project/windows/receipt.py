
import tkinter as tk

import states as states


def receiptWindow(config, parent, c):
    basket = c.basket
    subtotal = c.subtotal.get()
    payCashIcon = config["payCashIcon"]

    newWindow = tk.Toplevel(parent)
    newWindow.title("Receipt")
    newWindow.resizable(False, False)
    newWindow.configure(background="white", pady=20, padx=10)

    # Parent Frame
    infoFrame = tk.Frame(newWindow, bg="white")
    infoFrame.pack()

    # Receipt header
    tk.Label(
        infoFrame, text="Vending Machine", bg="white", font=("Helvetica", 12, "bold")
    ).pack()
    tk.Label(infoFrame, text="*" * 43, bg="white").pack()

    # Table Frames
    nameFrame = tk.Frame(infoFrame, bg="white")
    nameFrame.pack(side="left")

    priceFrame = tk.Frame(infoFrame, bg="white")
    priceFrame.pack(side="right")

    tk.Label(
        nameFrame, text="Name", bg="white", anchor="w", font=("Helvetica", 12, "bold")
    ).pack(fill="x", expand=True)
    tk.Label(
        priceFrame, text="Price", bg="white", anchor="w", font=("Helvetica", 12, "bold")
    ).pack(fill="x", expand=True)

    for item in basket.values():
        # Item name
        tk.Label(nameFrame, text=str(f"{item['name']}"), bg="white", anchor="w").pack(
            fill="x", expand=True
        )
        # Item price * amount
        amountPaid = round(item["amount"] * float(item["price"]), 2)
        tk.Label(
            priceFrame,
            text=str(f"${amountPaid} (x{item['amount']})"),
            bg="white",
            anchor="w",
        ).pack(fill="x", expand=True)

        # Subtotal
        tk.Label(nameFrame, text="Subtotal", bg="white", anchor="w").pack(
            fill="x", expand=True, pady=(12, 0)
        )
        tk.Label(
            priceFrame, text=str(f"${round(subtotal, 2)}"), bg="white", anchor="w"
        ).pack(fill="x", expand=True, pady=(8, 0))

        # Total
        tk.Label(
            nameFrame, text="Total", bg="white", anchor="w", font=("Helvetica", 12, "bold")
        ).pack(fill="x", expand=True, pady=(12, 0))
        tk.Label(
            priceFrame,
            text=str(f"LE {round(subtotal, 2)}"),
            bg="white",
            anchor="w",
        ).pack(fill="x", expand=True, pady=(12, 0))


    # Pay with cash method
    def payWithCash():
        charge = round(subtotal, 2)
        c.screenMessage.set(f"Enter cash manually\nLE {str(charge)}")
        c.state = states.PAY_CASH
        newWindow.destroy()
        newWindow.update()

    tk.Label(
        newWindow, text="Payment Method", bg="white", font="Helvetica 12 bold"
    ).pack(fill="x", pady=(20, 0))

    # Cash payment button
    tk.Button(
        newWindow,
        command=payWithCash,
        bg="#48AD46",
        activebackground="#5BCC58",
        fg="#F0F0F0",
        activeforeground="#F0F0F0",
        text="Insert Cash Amount",
        image=payCashIcon,
        font=("Helvetica", 12, "bold"),
        compound="left",
        cursor="hand1",
        bd=0,
        relief="flat",
        borderwidth=0,
        pady=8,
        padx=10,
    ).pack(fill="x", pady=(0, 5))

    newWindow.transient(parent)
    newWindow.grab_set()
