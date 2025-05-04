import threading
from time import sleep
import states as states
from lcd import loading, blink, typerwriter
from tinydb import TinyDB
from components.product import ProductList

productDB = TinyDB("database/product.json")

# Good bye messages
def goodbye(c):
    messages = ["Thank you.\n", "Come Again!"]
    typerwriter(c, messages)
    c.state = states.CODE


def processPayment(c, newBalance, paymentMethod):
    loading(c)
    sleep(0.5)
    # If payment method is cash, return changes
    if paymentMethod == "cash":
        c.state = states.PAYMENT
        c.screenMessage.set(str(f"Change: LE {round(newBalance, 2)}"))
        sleep(2)
        c.screenMessage.set("")
        blink(c, str(f"Change: LE {round(newBalance, 2)}"))

    c.screenMessage.set("")
    threading.Thread(target=goodbye, args=(c,)).start()


def finishAndPay(c, balance, paymentMethod):
    print("Entered")
    subtotal = c.subtotal.get()

    temp_dic = {
        "cart": c.basket,
        "balance": balance,
        "subtotal": float(subtotal),
        "paymentType": paymentMethod,
    }
    balance = temp_dic["balance"]
    subtotal = temp_dic["subtotal"]
    cart = temp_dic["cart"]
    paymentType = temp_dic["paymentType"]

    newBalance = balance - subtotal
    print(f"Paying with {balance} {cart} {subtotal} {paymentType}")
    # Proceed if user user has enough money
    if subtotal <= balance:
        try:
            # Decrement stock
            for product in cart.values():
                productDB.update(
                    {"quantity": product["quantity"] - product["amount"]},
                    doc_ids=[product["id"]],
                )

            data = {
                "balance": round(newBalance, 2),
                "products": productDB.all(),
            }
            response = data

            c.basket = {}
            c.subtotal.set(0)
            c.cart.set(0)
            
            # Update product quantities in the UI
            for index, product in enumerate(data["products"]):
                if index < len(c.products):
                    c.products[index].quantity.set(product["quantity"])

            # Force update of the product list display
            if hasattr(c, 'productList'):
                c.productList.destroy()
            c.productList = ProductList(c.container, c)
            c.productList.pack(side="right", expand=1, fill="both", padx=(0, 4))
            
            # Force update of the display
            c.update_idletasks()
            c.update()

            threading.Thread(
                target=processPayment,
                args=(
                    c,
                    response["balance"],
                    paymentMethod,
                ),
            ).start()
            return True
        except Exception as e:
            print(f"Error updating products: {e}")
            # Even if there's an error updating the display, still process the payment
            threading.Thread(
                target=processPayment,
                args=(
                    c,
                    newBalance,
                    paymentMethod,
                ),
            ).start()
            return True
    return False

# GET request for inventory
def getInventory():
    products = productDB.all()

    labels = []
    sizes = []
    colors = []

    for product in productDB:
        labels.append(product["name"])
        sizes.append(product["quantity"])
        if product["quantity"] < 10:
            colors.append("red")
        elif product["quantity"] in range(10, 20):
            colors.append("orange")
        else:
            colors.append("#55b70b")

    data = {}
    if products:
        data = {
            "success": True,
            "message": None,
            "labels": tuple(labels),
            "sizes": sizes,
            "colors": colors,
        }
    else:
        data = {
            "success": False,
            "message": "Can't fetch inventory",
            "labels": labels,
            "sizes": sizes,
            "colors": colors,
        }

    return data