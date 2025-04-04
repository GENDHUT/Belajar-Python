import tkinter as tk
from tkinter import messagebox

def add():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 + num2
        result_label.config(text=f"Hasil: {result}")
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid!")

def subtract():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 - num2
        result_label.config(text=f"Hasil: {result}")
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid!")

def multiply():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        result = num1 * num2
        result_label.config(text=f"Hasil: {result}")
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid!")

def divide():
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        if num2 == 0:
            messagebox.showerror("Error", "Pembagian dengan nol tidak diperbolehkan!")
            return
        result = num1 / num2
        result_label.config(text=f"Hasil: {result}")
    except ValueError:
        messagebox.showerror("Error", "Masukkan angka yang valid!")

# Membuat window utama
root = tk.Tk()
root.title("Kalkulator Sederhana")

# Label dan Entry untuk angka pertama
tk.Label(root, text="Angka Pertama:").grid(row=0, column=0, padx=10, pady=10)
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1, padx=10, pady=10)

# Label dan Entry untuk angka kedua
tk.Label(root, text="Angka Kedua:").grid(row=1, column=0, padx=10, pady=10)
entry2 = tk.Entry(root)
entry2.grid(row=1, column=1, padx=10, pady=10)

# Frame untuk tombol operasi
button_frame = tk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

btn_add = tk.Button(button_frame, text="Tambah", width=10, command=add)
btn_add.grid(row=0, column=0, padx=5, pady=5)

btn_subtract = tk.Button(button_frame, text="Kurang", width=10, command=subtract)
btn_subtract.grid(row=0, column=1, padx=5, pady=5)

btn_multiply = tk.Button(button_frame, text="Kali", width=10, command=multiply)
btn_multiply.grid(row=0, column=2, padx=5, pady=5)

btn_divide = tk.Button(button_frame, text="Bagi", width=10, command=divide)
btn_divide.grid(row=0, column=3, padx=5, pady=5)

# Label untuk menampilkan hasil
result_label = tk.Label(root, text="Hasil: ", font=("Helvetica", 14))
result_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
