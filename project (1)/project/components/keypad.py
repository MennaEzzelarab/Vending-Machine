import threading
import tkinter as tk
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
        print("Elsing")
        previous = c.screenMessage.get()
        messages = (
            "Enter Item Code",
            "Enter Amount",
            f"Enter cash manually\nLE {str(charge)}",
        )
        print(f"Enter cash manually\nLE {str(charge)}")
        print(c.screenMessage.get())
        if previous in messages:
            c.screenMessage.set(button)
        else:
            # For cash input, build up the number
            if c.state == states.PAY_CASH:
                # If we have a prompt message, start fresh with the button
                if "Enter cash manually" in previous:
                    c.screenMessage.set(button)
                else:
                    # Otherwise append to existing number
                    c.screenMessage.set(previous + button)
            else:
                c.screenMessage.set((previous + button))

def getButtonColor(button):
    if button == "CLR":
        return "#C73B2D"
    else:
        return "#0d1137"


def getButtonHover(button):
    if button == "CLR":
        return "#C73B2D"
    else:
        return "#393E42"


def errorMessageResolver(c, message):
    subtotal = c.subtotal.get()
    charge = round(subtotal, 2)
    blink(c, message)
    if c.state == states.CODE:
        print("Enter code state")
        c.screenMessage.set("Enter Item Code")
    if c.state == states.AMOUNT:
        c.screenMessage.set("Enter Amount")
    if c.state == states.PAY_CASH:
        c.screenMessage.set(f"Enter cash manually\nLE {str(charge)}")


class Keypad(tk.Frame):
    def __init__(self, parent, c):
        tk.Frame.__init__(self, parent, bg="white")
        self.code = ""
        self.buttons = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            [".", "0", "CLR"],
        ]
        self.products = c.products

        Display(self, c).pack(fill="x")

        self.calculatorView = tk.Frame(self)
        self.calculatorGrid = tk.Frame(self.calculatorView)
        self.calculatorView.pack()
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
                    # Convert code to integer and check if it's a valid product index
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
                        args=(
                            c,
                            "Invalid Code",
                        ),
                    ).start()

            # ***** state 2: AMOUNT *****
            elif c.state == states.AMOUNT:
                amount = c.screenMessage.get()
                if amount.isdigit():
                    c.setAmount(int(amount))
                    threading.Thread(
                        target=processCode,
                        args=(
                            c,
                            self.code,
                        ),
                    ).start()
                else:
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(
                            c,
                            "Invalid Amount",
                        ),
                    ).start()

            elif c.state == states.CONFIRM:
                if c.selected.quantity.get() - c.amount >= 0:
                    try:
                        if c.basket[c.selected.id]:
                            previous = (
                                c.basket[c.selected.id]["price"]
                                * c.basket[c.selected.id]["amount"]
                            )
                            c.updateSubtotal(previous * -1)
                            c.updateSubtotal(c.selected.price.get() * c.amount)

                            previousCart = c.basket[c.selected.id]["amount"]
                            c.cart.set((c.cart.get() - previousCart) + c.amount)
                    except KeyError:
                        c.updateSubtotal(c.selected.price.get() * c.amount)
                        c.cart.set(c.cart.get() + c.amount)

                    # Add product to basket
                    c.basket[c.selected.id] = {
                        "id": c.selected.id,
                        "name": c.selected.name.get(),
                        "price": c.selected.price.get(),
                        "quantity": c.selected.quantity.get(),
                        "amount": c.amount,
                    }

                    # Reset amount for next purchase
                    c.setAmount(0)
                    cartWindow(config)
                    c.screenMessage.set("Enter Item Code")

                    c.toggleLock(False)
                else:
                    # When there is insufficient inventory, display an out of stock message
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(
                            c,
                            "Out of Stock",
                        ),
                    ).start()
                    c.toggleLock(False)
                c.state = states.CODE

            elif c.state == states.PAY_CASH:
                c.toggleLock(True)
                cash = c.screenMessage.get()
                print(f"The cash {cash}")
                try:
                    print("Trying")
                    # For cash input, we just need to convert the entered number
                    cash_amount = float(cash)
                    if cash_amount < c.subtotal.get():
                        raise ValueError("Insufficient cash amount")
                    success = finishAndPay(c, cash_amount, "cash")
                    print(f"Finished trying {success}")
                    if success:
                        print("Success")
                    else:
                        raise Exception("Invalid cash")
                except Exception as e:
                    print(f"Errorrr {e}")
                    threading.Thread(
                        target=errorMessageResolver,
                        args=(
                            c,
                            "Invalid Cash",
                        ),
                    ).start()
            elif c.state == states.PAYMENT:
                print("Payment in process")
        
        for row in range(len(self.buttons)):
            for col in range(3):
                button = self.buttons[row][col]
                tk.Button(
                    self.calculatorGrid,
                    command=partial(pressKey, c, button),
                    bg=getButtonColor(button),
                    fg="#D8D0C5",
                    font=("DS-Digital", 16, "bold"),
                    activebackground=getButtonHover(button),
                    activeforeground="#D8D0C5",
                    state="disabled" if button == "" else "normal",
                    width=3,
                    height=2,
                    text=button,
                    cursor="arrow" if button == "" else "hand1",
                    padx=10,
                    pady=4,
                ).grid(row=row, column=col, sticky="news")

        self.calculator_button = tk.Button(
            self,
            cursor="hand1",
            command=partial(onSubmit, c),
            bg="#22bf2f",
            font=("Helvetica", 10, "bold"),
            activebackground="#DD5D1D",
            activeforeground="white",
            text="Next",
            height=2,
            fg="white",
        )
        self.calculator_button.pack(fill="x")