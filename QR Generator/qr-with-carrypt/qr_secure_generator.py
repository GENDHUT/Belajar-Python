import os
import json
import qrcode
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

SECRET_KEY = b"MYSECRETKEY12345"  # 16 bytes AES key

def encrypt_payload(url: str):
    payload = {
        "url": url
        # Bisa tambah "expires": 123456789 jika perlu kadaluarsa
    }

    json_bytes = json.dumps(payload).encode()
    padded = pad(json_bytes, AES.block_size)

    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(padded)

    return base64.b64encode(encrypted).decode()

def generate_qr_from_url(url, output_file="qr.jpg"):
    encrypted_text = encrypt_payload(url)

    qr_folder = "qr"
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(encrypted_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    output_path = os.path.join(qr_folder, output_file)
    img.save(output_path, format="JPEG")

    return qr, output_path, img, encrypted_text

# ================= GUI =================

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure QR Code Generator")

        tk.Label(root, text="Masukkan URL:").pack(pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        tk.Button(root, text="Generate Secure QR", command=self.generate_qr).pack(pady=5)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)

    def generate_qr(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "URL tidak boleh kosong!")
            return

        qr, path, img, encrypted_data = generate_qr_from_url(url)

        print("Encrypted Data:", encrypted_data)
        print("Saved to:", path)

        tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()
