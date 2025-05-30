import threading
import tkinter as tk
from tkinter import ttk
from functools import partial
from payment import finishAndPay
from components.display import Display
from windows.cart import cartWindow
import states as states
from lcd import blink, loading
from windows.receipt import receiptWindow

button_codes = {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
}

def processCode(c, code):
    products = c.products
    loading(c)
    
    try:
        # Convert code to integer and get the product (adjusting for 0-based index)
        code_int = int(code)
        if 1 <= code_int <= len(products):
            selected = products[code_int - 1]  # Subtract 1 because we use 1-based codes but 0-based list indices
            # Confirmation text
            c.screenMessage.set(selected.name.get() + "\n" + "Continue?")
            c.setSelected(selected)
            c.state = states.CONFIRM
        else:
            raise ValueError("Invalid product code")
    except (ValueError, IndexError) as e:
        print(f"Error processing code {code}: {e}")
        threading.Thread(
            target=errorMessageResolver,
            args=(c, "Invalid Code"),
        ).start()

def lockerWrapper(func):
    def checkIfLocked(controller, *args, **kwargs):
        if not controller.locked:
            func(controller, *args, **kwargs)
    return checkIfLocked

@lockerWrapper
def pressKey(c, button):
    subtotal = c.subtotal.get()
    charge = round(subtotal, 2)

    if button == "CLR":
        if c.screenMessage.get() == "Enter Amount":
            c.screenMessage.set("Enter Item Code")
            c.state = states.CODE
        elif c.state == states.AMOUNT:
            c.screenMessage.set("Enter Amount")
        elif c.state == states.PAY_CASH:
            c.screenMessage.set(f"Enter cash manually\nLE {str(charge)}")
        else:
            c.screenMessage.set("Enter Item Code")
            c.state = states.CODE
        c.toggleLock(False)
    else:
        previous = c.screenMessage.get()
        messages = (
            "Enter Item Code",
            "Enter Amount",
            f"Enter cash manually\nLE {str(charge)}",
        )
        if previous in messages:
            c.screenMessage.set(button)
        else:
            if c.state == states.PAY_CASH:
                if "Enter cash manually" in previous:
                    c.screenMessage.set(button)
                else:
                    c.screenMessage.set(previous + button)
            else:
                c.screenMessage.set((previous + button))

def getButtonColor(button):
    if button == "CLR":
        return "#FF6B6B"  # Softer red for CLR
    else:
        return "#3A3F5E"  # Smooth blue-gray for number buttons

def getButtonHover(button):
    if button == "CLR":
        return "#FF8787"  # Lighter red on hover
    else:
        return "#565B7F"  # Lighter blue-gray on hover

def errorMessageResolver(c, message):
    subtotal = c.subtotal.get()
    charge = round(subtotal, 2)
    blink(c, message)
    if c.state == states.CODE:
        c.screenMessage.set("Enter Item Code")
    if c.state == states.AMOUNT:
        c.screenMessage.set("Enter Amount")
    if c.state == states.PAY_CASH:
        c.screenMessage.set(f"Enter cash manually\nLE {str(charge)}")

class Keypad(tk.Frame):
    def __init__(self, parent, c):
        tk.Frame.__init__(self, parent, bg="#EDEFF5")  # Smooth light gray background
        self.code = ""
        self.buttons = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            [".", "0", "CLR"],
        ]
        self.products = c.products

        # Configure ttk style for rounded buttons
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Keypad.TButton",
            font=("Helvetica", 14, "bold"),
            foreground="#FFFFFF",
            background="#3A3F5E",
            padding=8,
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Keypad.TButton",
            background=[("active", "#565B7F")],
            foreground=[("active", "#FFFFFF")]
        )
        style.configure(
            "Clear.TButton",
            background="#FF6B6B",
            foreground="#FFFFFF",
        )
        style.map(
            "Clear.TButton",
            background=[("active", "#FF8787")],
            foreground=[("active", "#FFFFFF")]
        )
        style.configure(
            "Next.TButton",
            font=("Helvetica", 12, "bold"),
            foreground="#FFFFFF",
            background="#1A73E8",
            padding=8,
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "Next.TButton",
            background=[("active", "#1557B0")],
            foreground=[("active", "#FFFFFF")]
        )

        # Display with vertical padding
        Display(self, c).pack(fill="x", pady=10)

        # Frame for calculator buttons
        self.calculatorView = tk.Frame(self, bg="#EDEFF5")
        self.calculatorGrid = tk.Frame(self.calculatorView, bg="#EDEFF5")
        self.calculatorView.pack(pady=8)
        self.calculatorGrid.grid()

        config = {
            "parent": parent,
            "controller": c,
            "continueIcon": tk.PhotoImage(file="assets/icons/continue.png"),
            "checkImage": tk.PhotoImage(file="assets/icons/tick.png"),
            "payIcon": tk.PhotoImage(file="assets/icons/payIcon.png"),
            "payCashIcon": tk.PhotoImage(file="assets/icons/payCash.png"),
            "payCardIcon": tk.PhotoImage(file="assets/icons/payCard.png"),
            "cancelIcon": tk.PhotoImage(file="assets/icons/cancel.png"),
        }

        @lockerWrapper
        def onSubmit(c):
            if c.screenMessage.get() == "Enter Item Code" and c.state == states.CODE:
                cartWindow(config)
                return

            # ***** state 1: CODE *****
            if c.state == states.CODE:
                code = c.screenMessage.get()
                try:
                    code_int = int(code)
                    if 1 <= code_int <= len(c.products):
                        self.code = code
                        c.screenMessage.set("Enter Amount")
                        c.state = states.AMOUNT
                        c.toggleLock(False)
                    else:
                        raise ValueError("Invalid product code")
                except (ValueError, KeyError):
                    print(f"Invalid product code: {code}")
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(c, "Invalid Code"),
                    ).start()

            # ***** state 2: AMOUNT *****
            elif c.state == states.AMOUNT:
                amount = c.screenMessage.get()
                if amount.isdigit():
                    c.setAmount(int(amount))
                    threading.Thread(
                        target=processCode,
                        args=(c, self.code),
                    ).start()
                else:
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(c, "Invalid Amount"),
                    ).start()

            elif c.state == states.CONFIRM:
                if c.amount <= 0:
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(c, "Invalid Amount"),
                    ).start()
                    c.state = states.CODE
                    c.screenMessage.set("Enter Item Code")
                    c.toggleLock(False)
                    return
                    
                if c.selected.quantity.get() - c.amount >= 0:
                    try:
                        if c.basket[c.selected.id]:
                            # Get the previous amount and price
                            previous_amount = c.basket[c.selected.id]["amount"]
                            previous_price = c.basket[c.selected.id]["price"]
                            
                            # Calculate new total amount
                            new_amount = previous_amount + c.amount
                            
                            # Update subtotal by removing previous item total and adding new total
                            c.updateSubtotal(previous_price * previous_amount * -1)  # Remove old total
                            c.updateSubtotal(previous_price * new_amount)  # Add new total
                            
                            # Update cart count
                            c.cart.set(c.cart.get() + c.amount)  # Just add the new amount
                            
                            # Update basket with new total amount
                            c.basket[c.selected.id] = {
                                "id": c.selected.id,
                                "name": c.selected.name.get(),
                                "price": c.selected.price.get(),
                                "quantity": c.selected.quantity.get(),
                                "amount": new_amount,
                            }
                    except KeyError:
                        # If item not in basket, add it normally
                        c.updateSubtotal(c.selected.price.get() * c.amount)
                        c.cart.set(c.cart.get() + c.amount)
                        c.basket[c.selected.id] = {
                            "id": c.selected.id,
                            "name": c.selected.name.get(),
                            "price": c.selected.price.get(),
                            "quantity": c.selected.quantity.get(),
                            "amount": c.amount,
                        }
                    
                    c.setAmount(0)
                    cartWindow(config)
                    c.screenMessage.set("Enter Item Code")
                    c.toggleLock(False)
                else:
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(c, "Out of Stock"),
                    ).start()
                    c.toggleLock(False)
                c.state = states.CODE

            elif c.state == states.PAYMENT:
                print("Payment in process")

        # Create smaller, rounded keypad buttons closer together
        for row in range(len(self.buttons)):
            for col in range(3):
                button = self.buttons[row][col]
                ttk.Button(
                    self.calculatorGrid,
                    command=partial(pressKey, c, button),
                    text=button,
                    style="Clear.TButton" if button == "CLR" else "Keypad.TButton",
                    state="disabled" if button == "" else "normal",
                    cursor="arrow" if button == "" else "hand2",
                    width=3,
                ).grid(row=row, column=col, sticky="news", padx=4, pady=4)  # Closer spacing

        # Next button with rounded, smooth styling
        self.calculator_button = ttk.Button(
            self,
            cursor="hand2",
            command=partial(onSubmit, c),
            text="Next",
            style="Next.TButton",
        )
        self.calculator_button.pack(fill="x", pady=10, padx=8)  # Adjusted padding