import tkinter as tk

class ToolbarButton(tk.Button):
    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(
            self,
            parent,
            border=0,
            cursor="hand1",
            pady=8,
            fg="white",
            activeforeground="white",
            compound="left",
            *args,
            **kwargs
        )