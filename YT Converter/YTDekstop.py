import tkinter as tk
from tkinter import messagebox, filedialog
from pytube import YouTube

def download_video():
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("Peringatan", "Masukkan URL video YouTube!")
        return
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        folder = filedialog.askdirectory(title="Pilih Folder Tujuan")
        if folder:
            stream.download(output_path=folder)
            messagebox.showinfo("Sukses", "Download selesai!")
    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

root = tk.Tk()
root.title("YT Video Downloader")

tk.Label(root, text="Masukkan URL Video YouTube:").pack(pady=10)
entry_url = tk.Entry(root, width=50)
entry_url.pack(pady=5)

btn_download = tk.Button(root, text="Download", command=download_video)
btn_download.pack(pady=10)

root.mainloop()
