from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)
FILE_NAME = "todoWeb.txt"

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

HTML_TEMPLATE = '''
<!doctype html>
<title>To-Do List</title>
<h1>To-Do List</h1>
<ul>
  {% for todo in todos %}
    <li>{{ loop.index }}. {{ todo['nama'] }} , status= {{ todo['status'] }}
        - <a href="{{ url_for('update', index=loop.index0) }}">Toggle Status</a>
        - <a href="{{ url_for('delete', index=loop.index0) }}">Hapus</a>
    </li>
  {% endfor %}
</ul>
<form method="POST" action="{{ url_for('add') }}">
    <input type="text" name="nama" placeholder="Nama To-Do">
    <input type="submit" value="Tambah">
</form>
'''

@app.route("/")
def index():
    todos = load_todos()
    return render_template_string(HTML_TEMPLATE, todos=todos)

@app.route("/add", methods=["POST"])
def add():
    nama = request.form.get("nama", "").strip()
    todos = load_todos()
    if nama:
        todos.append({"nama": nama, "status": "belum selesai"})
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/update/<int:index>")
def update(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        todo = todos[index]
        todo["status"] = "selesai" if todo["status"] == "belum selesai" else "belum selesai"
        save_todos(todos)
    return redirect(url_for("index"))

@app.route("/delete/<int:index>")
def delete(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        todos.pop(index)
        save_todos(todos)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
