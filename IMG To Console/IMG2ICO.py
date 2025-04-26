import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def convert_image_to_ico():
    # Sembunyikan window utama Tkinter
    root = tk.Tk()
    root.withdraw()

    # Step 1: Pilih file gambar
    input_path = filedialog.askopenfilename(
        title="Pilih gambar yang akan dikonversi",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )

    if not input_path:
        messagebox.showinfo("Info", "Tidak ada gambar yang dipilih.")
        return

    # Step 2: Pilih lokasi dan nama file hasil .ico
    output_path = filedialog.asksaveasfilename(
        defaultextension=".ico",
        filetypes=[("Icon files", "*.ico")],
        title="Simpan sebagai"
    )

    if not output_path:
        messagebox.showinfo("Info", "Penyimpanan dibatalkan.")
        return

    try:
        img = Image.open(input_path)
        img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
        messagebox.showinfo("Berhasil", f"Berhasil dikonversi ke: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal konversi: {e}")

if __name__ == "__main__":
    convert_image_to_ico()
