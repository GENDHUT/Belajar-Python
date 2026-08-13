import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os


def convert_webp_to_png():
    # Buka File Explorer untuk memilih file
    file_path = filedialog.askopenfilename(
        title="Pilih gambar WebP",
        filetypes=[
            ("WebP Image", "*.webp"),
            ("All Files", "*.*")
        ]
    )

    # Jika user membatalkan
    if not file_path:
        return

    try:
        # Buka gambar
        image = Image.open(file_path)

        # Nama output otomatis
        output_path = os.path.splitext(file_path)[0] + ".png"

        # Pastikan transparansi tetap terjaga
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        # Simpan sebagai PNG
        image.save(output_path, "PNG")

        messagebox.showinfo(
            "Berhasil",
            f"WebP berhasil dikonversi!\n\n"
            f"Input:\n{file_path}\n\n"
            f"Output:\n{output_path}"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Gagal mengkonversi gambar:\n\n{e}"
        )


# Membuat window
root = tk.Tk()
root.title("WebP to PNG Converter")
root.geometry("400x200")
root.resizable(False, False)

# Judul
title = tk.Label(
    root,
    text="WebP → PNG Converter",
    font=("Arial", 18, "bold")
)
title.pack(pady=30)

# Tombol
button = tk.Button(
    root,
    text="Pilih File WebP",
    command=convert_webp_to_png,
    font=("Arial", 12),
    width=20,
    height=2
)
button.pack()

root.mainloop()