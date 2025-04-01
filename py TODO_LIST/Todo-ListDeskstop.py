import tkinter as tk
from tkinter import messagebox
import os

FILE_NAME = "todoDeskstop.txt"

def load_todos():
    todos = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        nomor_part, rest = line.split(".", 1)
                        nama_status = rest.strip().split(" , ")
                        if len(nama_status) == 2:
                            nama_todo = nama_status[0].strip()
                            status = nama_status[1].replace("status=", "").strip()
                            todos.append({"nama": nama_todo, "status": status})
                    except Exception as e:
                        print("Gagal membaca baris:", line)
    return todos

def save_todos(todos):
    with open(FILE_NAME, "w") as file:
        for idx, todo in enumerate(todos, start=1):
            file.write(f"{idx}. {todo['nama']} , status= {todo['status']}\n")

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.todos = load_todos()
        
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)
        
        self.listbox = tk.Listbox(self.frame, width=50)
        self.listbox.pack()
        self.refresh_listbox()
        
        self.entry = tk.Entry(self.frame, width=50)
        self.entry.pack(pady=5)
        
        self.btn_add = tk.Button(self.frame, text="Tambah To-Do", command=self.tambah_todo)
        self.btn_add.pack(pady=5)
        
        self.btn_update = tk.Button(self.frame, text="Update Status", command=self.update_status)
        self.btn_update.pack(pady=5)
        
        self.btn_delete = tk.Button(self.frame, text="Hapus To-Do", command=self.hapus_todo)
        self.btn_delete.pack(pady=5)
    
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for idx, todo in enumerate(self.todos, start=1):
            self.listbox.insert(tk.END, f"{idx}. {todo['nama']} , status= {todo['status']}")
    
    def tambah_todo(self):
        nama = self.entry.get().strip()
        if nama:
            self.todos.append({"nama": nama, "status": "belum selesai"})
            self.entry.delete(0, tk.END)
            self.refresh_listbox()
            save_todos(self.todos)
        else:
            messagebox.showwarning("Peringatan", "Masukkan nama to-do!")
    
    def update_status(self):
        try:
            idx = self.listbox.curselection()[0]
            todo = self.todos[idx]
            todo["status"] = "selesai" if todo["status"] == "belum selesai" else "belum selesai"
            self.refresh_listbox()
            save_todos(self.todos)
        except IndexError:
            messagebox.showwarning("Peringatan", "Pilih to-do yang akan diupdate!")
    
    def hapus_todo(self):
        try:
            idx = self.listbox.curselection()[0]
            self.todos.pop(idx)
            self.refresh_listbox()
            save_todos(self.todos)
        except IndexError:
            messagebox.showwarning("Peringatan", "Pilih to-do yang akan dihapus!")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
