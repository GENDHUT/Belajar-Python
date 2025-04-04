import os
import qrcode
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

def generate_qr(link, output_file="qr.jpg"):
    qr_folder = "qr"
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)
    
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
    
    output_path = os.path.join(qr_folder, output_file)
    img.save(output_path, format="JPEG")
    
    return qr, output_path, img

def print_qr_in_console(qr):
    """Cetak QR Code dalam bentuk ASCII dengan satu karakter per modul."""
    matrix = qr.get_matrix()
    for row in matrix:
        line = "".join("█" if col else " " for col in row)
        print(line)

class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        
        tk.Label(root, text="Masukkan link:").pack(pady=5)
        self.link_entry = tk.Entry(root, width=50)
        self.link_entry.pack(pady=5)
        self.generate_btn = tk.Button(root, text="Generate QR", command=self.generate_qr_code)
        self.generate_btn.pack(pady=5)
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)
    
    def generate_qr_code(self):
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showerror("Error", "Link tidak boleh kosong!")
            return
        qr, path, pil_img = generate_qr(link)
        print("QR Code disimpan di:", path)
        print("\nQR Code dalam bentuk ASCII:")
        print_qr_in_console(qr)
        tk_image = ImageTk.PhotoImage(pil_img)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()
