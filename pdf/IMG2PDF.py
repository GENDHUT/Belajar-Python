import img2pdf
from tkinter import Tk, filedialog
import os

root = Tk()
root.withdraw()

file_paths = filedialog.askopenfilenames(
    title="Pilih gambar yang ingin dikonversi ke PDF",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

if not file_paths:
    print("Tidak ada gambar yang dipilih.")
    exit()

output_path = filedialog.asksaveasfilename(
    defaultextension=".pdf",
    filetypes=[("PDF files", "*.pdf")],
    title="Simpan sebagai"
)

if not output_path:
    print("Penyimpanan dibatalkan.")
    exit()

with open(output_path, "wb") as f:
    f.write(img2pdf.convert(list(file_paths)))

print(f"PDF berhasil dibuat: {output_path}")
os.startfile(os.path.dirname(output_path))  