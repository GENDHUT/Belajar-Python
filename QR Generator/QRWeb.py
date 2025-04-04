import os
from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, flash
import qrcode

app = Flask(__name__)
app.secret_key = "secret-key"  

BASE_DIR = os.getcwd()
QR_FOLDER = os.path.join(BASE_DIR, "qr")
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

def generate_qr(link, output_file="qr.jpg"):
    """Buat QR Code dari link dan simpan sebagai JPG di folder QR."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    base_filename, ext = os.path.splitext(output_file)
    if ext.lower() not in [".jpg", ".jpeg"]:
        output_file = base_filename + ".jpg"
    output_path = os.path.join(QR_FOLDER, output_file)
    img.save(output_path, format="JPEG")
    return qr, output_file, img

def print_qr_in_console(qr):
    """Cetak QR Code dalam bentuk ASCII ke konsol."""
    matrix = qr.get_matrix()
    ascii_qr = "\n".join("".join("█" if col else " " for col in row) for row in matrix)
    print(ascii_qr)

INDEX_HTML = """
<!doctype html>
<html>
<head>
    <title>QR Code Generator</title>
    <style>
      body { font-family: Arial, sans-serif; }
      .container { width: 500px; margin: 50px auto; text-align: center; }
      input[type="text"] { width: 80%; padding: 8px; }
      input[type="submit"] { padding: 8px 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>QR Code Generator</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul style="color: red;">
              {% for msg in messages %}
                <li>{{ msg }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form method="post" action="{{ url_for('generate_qr_code') }}">
            <label>Masukkan link:</label><br>
            <input type="text" name="link" required><br><br>
            <input type="submit" value="Generate QR">
        </form>
        {% if qr_image %}
          <h2>QR Code:</h2>
          <img src="{{ url_for('serve_qr', filename=qr_image) }}" alt="QR Code">
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def generate_qr_code():
    qr_image = None
    if request.method == "POST":
        link = request.form.get("link", "").strip()
        if not link:
            flash("Link tidak boleh kosong!")
            return redirect(url_for("generate_qr_code"))
        try:
            qr, output_file, img = generate_qr(link)
            print("QR Code disimpan di:", os.path.join(QR_FOLDER, output_file))
            print("\nQR Code dalam bentuk ASCII:")
            print_qr_in_console(qr)
            qr_image = output_file
        except Exception as e:
            flash("Terjadi kesalahan: " + str(e))
    return render_template_string(INDEX_HTML, qr_image=qr_image)

@app.route("/qr/<filename>")
def serve_qr(filename):
    return send_from_directory(QR_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
