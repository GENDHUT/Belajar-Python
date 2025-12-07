import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import os

def pilih_file():
    # Pilih banyak file MP4
    file_paths = filedialog.askopenfilenames(
        filetypes=[("MP4 Files", "*.mp4")]
    )
    
    if file_paths:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, ";".join(file_paths))  # Simpan dalam format string

def convert():
    input_files = entry_file.get()

    if not input_files:
        messagebox.showerror("Error", "Silakan pilih file MP4 dulu.")
        return

    file_list = input_files.split(";")

    # Buat folder output mp3 jika belum ada
    output_folder = "mp3"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        for file in file_list:
            file = file.strip()
            if file == "":
                continue

            # Nama file output
            filename = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(output_folder, filename + ".mp3")

            video = VideoFileClip(file)
            audio = video.audio
            audio.write_audiofile(output_file)

            audio.close()
            video.close()

        messagebox.showinfo("Sukses", f"Semua file berhasil dikonversi!\nDisimpan di folder: {output_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"Gagal mengonversi:\n{e}")

# GUI Setup
app = tk.Tk()
app.title("MP4 ke MP3 Converter (Multiple)")
app.geometry("450x180")

label = tk.Label(app, text="Pilih beberapa file MP4:")
label.pack(pady=5)

entry_file = tk.Entry(app, width=55)
entry_file.pack()

btn_browse = tk.Button(app, text="Browse", command=pilih_file)
btn_browse.pack(pady=5)

btn_convert = tk.Button(app, text="Convert Semua ke MP3", command=convert)
btn_convert.pack(pady=10)

app.mainloop()
