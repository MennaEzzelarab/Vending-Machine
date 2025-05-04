from Controller import Controller

#  ------- Controller -------

def main():
    root = Controller()
    root.title("Vending Machine")
    root.resizable(False, False)
    root.configure(bg="#0d1137")
    root.configure(pady=8, padx=8)
    root.mainloop()


if __name__ == "__main__":
    main()