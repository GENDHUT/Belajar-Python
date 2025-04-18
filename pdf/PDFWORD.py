from pdf2docx import Converter
from docx2pdf import convert as docx_to_pdf
from tkinter import Tk, filedialog, messagebox
from pathlib import Path
import os

def pdf_to_word():
    pdf_file = filedialog.askopenfilename(
        title="Pilih file PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_file:
        print("❌ Tidak ada file PDF yang dipilih.")
        return

    docx_file = filedialog.asksaveasfilename(
        title="Simpan sebagai file Word",
        defaultextension=".docx",
        filetypes=[("Word files", "*.docx")]
    )
    if not docx_file:
        print("❌ Penyimpanan dibatalkan.")
        return

    cv = Converter(pdf_file)
    cv.convert(docx_file, start=0, end=None)
    cv.close()

    print(f"✅ PDF berhasil dikonversi ke Word: {docx_file}")
    os.startfile(os.path.dirname(docx_file))


def word_to_pdf():
    docx_file = filedialog.askopenfilename(
        title="Pilih file Word",
        filetypes=[("Word files", "*.docx")]
    )
    if not docx_file:
        print("❌ Tidak ada file Word yang dipilih.")
        return

    pdf_file = filedialog.asksaveasfilename(
        title="Simpan sebagai file PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_file:
        print("❌ Penyimpanan dibatalkan.")
        return

    docx_to_pdf(docx_file, pdf_file)
    print(f"✅ Word berhasil dikonversi ke PDF: {pdf_file}")
    os.startfile(os.path.dirname(pdf_file))


if __name__ == '__main__':
    root = Tk()
    root.withdraw()

    print("1. PDF ke Word")
    print("2. Word ke PDF")
    choice = input("Pilih opsi (1/2): ")

    if choice == '1':
        pdf_to_word()
    elif choice == '2':
        word_to_pdf()
    else:
        print("❌ Pilihan tidak valid.")
