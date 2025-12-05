import os
import qrcode
import base64
from Crypto.Cipher import AES
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

SECRET_KEY = b"MYSECRETKEY12345"  # 16 bytes

def encrypt_url(url: str):
    url_bytes = url.encode()

    # Padding ke kelipatan 16 bytes
    while len(url_bytes) % 16 != 0:
        url_bytes += b" "

    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(url_bytes)

    # Convert ke base64 untuk hasil rapi
    return base64.b64encode(encrypted).decode()

def generate_qr_from_url(url, output_file="qr.jpg"):
    encrypted_text = encrypt_url(url)

    qr_folder = "qr"
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(encrypted_text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    output_path = os.path.join(qr_folder, output_file)
    img.save(output_path, format="JPEG")

    return qr, output_path, img, encrypted_text

# ---- GUI Kamu ----

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator Secure")

        tk.Label(root, text="Masukkan URL:").pack(pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)
        self.generate_btn = tk.Button(root, text="Generate Secure QR", command=self.generate_qr_code)
        self.generate_btn.pack(pady=5)
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)

    def generate_qr_code(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "URL tidak boleh kosong!")
            return

        qr, path, pil_img, encrypted_text = generate_qr_from_url(url)

        print("Encrypted Data:", encrypted_text)
        print("QR Code disimpan di:", path)

        tk_image = ImageTk.PhotoImage(pil_img)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()
