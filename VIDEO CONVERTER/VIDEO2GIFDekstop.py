import os
from tkinter import Tk, Label, Button, filedialog, messagebox, Toplevel
from moviepy.editor import VideoFileClip


class MP4ToGIFApp:
    def __init__(self, master):
        self.master = master
        self.setup_main_window()

    def setup_main_window(self):
        self.master.title("MP4 to GIF Converter")
        self.master.geometry("400x200")
        self.master.resizable(False, False)

        self.label = Label(self.master, text="MP4 to GIF Converter", font=("Arial", 16))
        self.label.pack(pady=10)

        self.select_button = Button(self.master, text="📂 Pilih Video MP4", command=self.select_video, width=30)
        self.select_button.pack(pady=5)

        self.convert_button = Button(self.master, text="🎬 Convert ke GIF", command=self.convert_to_gif, width=30, state="disabled")
        self.convert_button.pack(pady=5)

        self.status_label = Label(self.master, text="", fg="green")
        self.status_label.pack(pady=10)

        self.video_path = None

    def reset(self):
        """Reset aplikasi ke awal."""
        self.video_path = None
        self.convert_button.config(state="disabled")
        self.status_label.config(text="")

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
            self.status_label.config(text="⏳ Mengonversi video...")
            self.master.update()

            clip.write_gif(gif_path)
            self.status_label.config(text="✅ GIF berhasil dibuat!")
            os.startfile(os.path.dirname(gif_path))

            self.ask_to_continue()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengonversi video:\n{e}")
            self.status_label.config(text="❌ Terjadi kesalahan.")

    def ask_to_continue(self):
        """Tampilkan popup untuk memilih lanjut atau keluar"""
        popup = Toplevel(self.master)
        popup.title("Selesai")
        popup.geometry("300x120")
        popup.resizable(False, False)
        Label(popup, text="🎉 Konversi selesai!\nLanjut?", font=("Arial", 12)).pack(pady=10)

        def lanjut():
            popup.destroy()
            self.reset()

        def keluar():
            popup.destroy()
            self.master.quit()

        Button(popup, text="🔁 Lanjut", width=12, command=lanjut).pack(pady=5)
        Button(popup, text="❌ Keluar", width=12, command=keluar).pack(pady=5)


if __name__ == "__main__":
    root = Tk()
    app = MP4ToGIFApp(root)
    root.mainloop()
