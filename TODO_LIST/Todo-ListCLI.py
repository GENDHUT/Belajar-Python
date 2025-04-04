import os

FILE_NAME = "todoCLI.txt"

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
                            status_part = nama_status[1].strip()
                            status = status_part.replace("status=", "").strip()
                            todos.append({"nama": nama_todo, "status": status})
                    except Exception as e:
                        print("Gagal membaca baris:", line)
    return todos

def save_todos(todos):
    with open(FILE_NAME, "w") as file:
        for idx, todo in enumerate(todos, start=1):
            line = f"{idx}. {todo['nama']} , status= {todo['status']}\n"
            file.write(line)

def tampilkan_todos(todos):
    if not todos:
        print("Belum ada to-do yang tersimpan.")
    else:
        print("Daftar To-Do:")
        for idx, todo in enumerate(todos, start=1):
            print(f"{idx}. {todo['nama']} , status= {todo['status']}")

def tambah_todo(todos):
    nama = input("Masukkan nama to-do: ")
    todo_baru = {"nama": nama, "status": "belum selesai"}
    todos.append(todo_baru)
    print("To-do berhasil ditambahkan.")

def update_status(todos):
    tampilkan_todos(todos)
    try:
        pilihan = int(input("Masukkan nomor to-do yang ingin diupdate statusnya: "))
        if 1 <= pilihan <= len(todos):
            todo = todos[pilihan - 1]
            if todo["status"] == "belum selesai":
                todo["status"] = "selesai"
            else:
                todo["status"] = "belum selesai"
            print(f"Status to-do '{todo['nama']}' telah diperbarui menjadi {todo['status']}.")
        else:
            print("Nomor tidak valid.")
    except ValueError:
        print("Input harus berupa angka.")

def hapus_todo(todos):
    tampilkan_todos(todos)
    try:
        pilihan = int(input("Masukkan nomor to-do yang ingin dihapus: "))
        if 1 <= pilihan <= len(todos):
            removed = todos.pop(pilihan - 1)
            print(f"To-do '{removed['nama']}' berhasil dihapus.")
        else:
            print("Nomor tidak valid.")
    except ValueError:
        print("Input harus berupa angka.")

def main():
    todos = load_todos()

    while True:
        print("\n--- To-Do List Manager ---")
        print("1. Tampilkan To-Do")
        print("2. Tambah To-Do")
        print("3. Update Status To-Do")
        print("4. Hapus To-Do")
        print("5. Keluar")
        pilihan = input("Pilih opsi (1-5): ")

        if pilihan == "1":
            tampilkan_todos(todos)
        elif pilihan == "2":
            tambah_todo(todos)
            save_todos(todos)
        elif pilihan == "3":
            update_status(todos)
            save_todos(todos)
        elif pilihan == "4":
            hapus_todo(todos)
            save_todos(todos)
        elif pilihan == "5":
            save_todos(todos)
            print("Sampai jumpa!")
            break
        else:
            print("Opsi tidak valid. Silakan pilih antara 1-5.")

if __name__ == "__main__":
    main()
