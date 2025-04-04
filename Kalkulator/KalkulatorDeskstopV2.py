import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Sederhana")

        self.expression = ""
        self.input_text = tk.StringVar()

        input_frame = tk.Frame(self.root, bd=2, relief=tk.RIDGE)
        input_frame.pack(padx=10, pady=10)

        self.input_field = tk.Entry(input_frame, font=("Arial", 16), textvariable=self.input_text, width=30, bd=5, justify="right")
        self.input_field.grid(row=0, column=0)
        self.input_field.pack(ipady=10)

        btns_frame = tk.Frame(self.root)
        btns_frame.pack()

        buttons = [
            ("C",  0, 0), ("←",  0, 1), ("(",  0, 2), (")",  0, 3),
            ("7",  1, 0), ("8",  1, 1), ("9",  1, 2), ("/",  1, 3),
            ("4",  2, 0), ("5",  2, 1), ("6",  2, 2), ("*",  2, 3),
            ("1",  3, 0), ("2",  3, 1), ("3",  3, 2), ("-",  3, 3),
            ("0",  4, 0), (".",  4, 1), ("=",  4, 2), ("+",  4, 3)
        ]

        for (text, row, col) in buttons:
            button = tk.Button(btns_frame, text=text, width=7, height=2,
                               font=("Arial", 12, "bold"),
                               command=lambda t=text: self.on_button_click(t))
            button.grid(row=row, column=col, padx=5, pady=5)

    def on_button_click(self, char):
        """
        Menangani setiap tombol yang ditekan.
        """
        if char == "C":
            self.expression = ""
            self.input_text.set("")
        elif char == "←":
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif char == "=":
            try:
                result = str(eval(self.expression))
                self.input_text.set(result)
                self.expression = result  
            except:
                self.input_text.set("Error")
                self.expression = ""
        else:
            self.expression += str(char)
            self.input_text.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
