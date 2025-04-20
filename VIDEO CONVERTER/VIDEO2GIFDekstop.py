import os
from tkinter import Tk, Label, Button, filedialog, messagebox
from moviepy.editor import VideoFileClip

class MP4ToGIFApp:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to GIF Converter")
        master.geometry("400x200")
        master.resizable(False, False)

        self.label = Label(master, text="MP4 to GIF Converter", font=("Arial", 16))
        self.label.pack(pady=10)

        self.select_button = Button(master, text="📂 Pilih Video MP4", command=self.select_video, width=30)
        self.select_button.pack(pady=5)

        self.convert_button = Button(master, text="🎬 Convert ke GIF", command=self.convert_to_gif, width=30, state="disabled")
        self.convert_button.pack(pady=5)

        self.status_label = Label(master, text="", fg="green")
        self.status_label.pack(pady=10)

        self.video_path = None

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            title="Pilih file MP4",
            filetypes=[("Video files", "*.mp4")]
        )
        if self.video_path:
            self.status_label.config(text=f"Video dipilih:\n{os.path.basename(self.video_path)}")
            self.convert_button.config(state="normal")

    def convert_to_gif(self):
        if not self.video_path:
            messagebox.showerror("Error", "Tidak ada file video yang dipilih.")
            return

        gif_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif")],
            title="Simpan sebagai file GIF"
        )
        if not gif_path:
            self.status_label.config(text="❌ Penyimpanan dibatalkan.")
            return

        try:
            clip = VideoFileClip(self.video_path)
            # clip = clip.subclip(0, min(clip.duration, 10))  # Uncomment untuk potong durasi
            self.status_label.config(text="⏳ Mengonversi video...")
            self.master.update()

            clip.write_gif(gif_path)
            self.status_label.config(text="✅ GIF berhasil dibuat!")
            os.startfile(os.path.dirname(gif_path))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengonversi video:\n{e}")
            self.status_label.config(text="❌ Terjadi kesalahan.")

if __name__ == "__main__":
    root = Tk()
    app = MP4ToGIFApp(root)
    root.mainloop()
