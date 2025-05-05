from Controller import Controller

#  ------- Controller -------

def main():
    root = Controller()
    root.title("Vending Machine")
    root.geometry("1000x600")  # Increased width to 1200
    root.minsize(1000, 600)    # Increased minimum width to 1200
    root.resizable(True, True)  # Allow resizing in both directions
    root.configure(bg="#0d1137")
    root.configure(pady=8, padx=8)
    root.mainloop()


if __name__ == "__main__":
    main()