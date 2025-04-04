import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
from moviepy.editor import AudioFileClip

def get_available_formats(url):
    """
    Mengambil informasi video dan menyaring format mp4 yang memiliki video (dan height).
    Jika ada pilihan format dengan audio, maka lebih diprioritaskan.
    """
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = info.get("formats", [])
    
    filtered_formats = [f for f in formats if f.get("ext") == "mp4" and f.get("vcodec") != "none" and f.get("height")]
    
    unique = {}
    for f in filtered_formats:
        res = f.get("height")
        res_str = f"{res}p"
        if res_str not in unique or (unique[res_str].get("acodec") == "none" and f.get("acodec") != "none"):
            unique[res_str] = f

    resolutions = sorted(unique.keys(), key=lambda x: int(x[:-1]), reverse=True)
    return unique, resolutions

def download_video(url, format_str, output_folder):
    """
    Mendownload video dengan format_str yang dipilih.
    Jika format_str merupakan format gabungan (video+audio), yt-dlp akan mengunduh kedua stream dan menggabungkannya.
    Video disimpan di folder VIDEO.
    """
    video_folder = os.path.join(output_folder, "VIDEO")
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',  
        'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

def convert_to_mp3(video_path, output_folder):
    """
    Mengkonversi file video menjadi MP3 menggunakan moviepy dan menyimpannya di folder MP3.
    """
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    mp3_folder = os.path.join(output_folder, "MP3")
    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder)
    mp3_path = os.path.join(mp3_folder, base_name + ".mp3")
    audioclip = AudioFileClip(video_path)
    audioclip.write_audiofile(mp3_path)
    audioclip.close()
    return mp3_path

class App:
    def __init__(self, root):
        self.root = root
        root.title("YT Video Downloader & Converter")
        
        tk.Label(root, text="Masukkan Link YouTube:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        self.get_formats_btn = tk.Button(root, text="Ambil Format", command=self.get_formats)
        self.get_formats_btn.grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(root, text="Pilih Resolusi:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.format_combo = ttk.Combobox(root, values=[], state="readonly", width=10)
        self.format_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.convert_var = tk.IntVar()
        tk.Checkbutton(root, text="Konversi ke MP3", variable=self.convert_var).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.download_btn = tk.Button(root, text="Download", command=self.start_download)
        self.download_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.status_text = tk.Text(root, height=10, width=80, state="disabled")
        self.status_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        
        self.output_folder = os.getcwd()
        self.unique_formats = {}
    
    def log(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.config(state="disabled")
        self.status_text.see(tk.END)
    
    def get_formats(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Masukkan URL terlebih dahulu!")
            return
        self.log("Mengambil informasi format...")
        try:
            self.unique_formats, resolutions = get_available_formats(url)
            if not resolutions:
                messagebox.showinfo("Info", "Tidak ada format video yang cocok ditemukan.")
                return
            self.format_combo['values'] = resolutions
            self.format_combo.current(0)
            self.log("Format tersedia: " + ", ".join(resolutions))
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat mengambil info video: {e}")
    
    def start_download(self):
        thread = threading.Thread(target=self.download_process)
        thread.start()
    
    def download_process(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "Masukkan URL terlebih dahulu!")
            return
        
        selected_res = self.format_combo.get()
        if not selected_res:
            messagebox.showwarning("Peringatan", "Pilih resolusi video terlebih dahulu!")
            return
        
        chosen_format = self.unique_formats.get(selected_res)
        if chosen_format.get("acodec") == "none":
            height = chosen_format.get("height")
            format_str = f"bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/best"
        else:
            format_str = chosen_format.get("format_id")
        
        self.log(f"Mengunduh video dengan format: {format_str}...")
        try:
            video_path = download_video(url, format_str, self.output_folder)
            self.log("Video berhasil diunduh: " + video_path)
        except Exception as e:
            self.log("Terjadi kesalahan saat mengunduh video: " + str(e))
            return
        
        if self.convert_var.get() == 1:
            self.log("Mulai konversi video ke MP3...")
            try:
                mp3_path = convert_to_mp3(video_path, self.output_folder)
                self.log("Konversi selesai: " + mp3_path)
            except Exception as e:
                self.log("Terjadi kesalahan saat konversi: " + str(e))
        else:
            self.log("Proses download selesai tanpa konversi MP3.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
