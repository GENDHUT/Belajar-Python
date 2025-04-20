from moviepy.editor import VideoFileClip
from tkinter import Tk, filedialog
import os

def mp4_to_gif():
    root = Tk()
    root.withdraw()

    video_path = filedialog.askopenfilename(
        title="Pilih file MP4",
        filetypes=[("Video files", "*.mp4")]
    )
    if not video_path:
        print("❌ Tidak ada file video yang dipilih.")
        return

    gif_path = filedialog.asksaveasfilename(
        defaultextension=".gif",
        filetypes=[("GIF files", "*.gif")],
        title="Simpan sebagai file GIF"
    )
    if not gif_path:
        print("❌ Penyimpanan dibatalkan.")
        return

    clip = VideoFileClip(video_path)
    # clip = clip.subclip(0, min(clip.duration, 10))  # batas 10 detik bila ingin
    clip.write_gif(gif_path)

    print(f"✅ GIF berhasil dibuat: {gif_path}")
    os.startfile(os.path.dirname(gif_path))

if __name__ == '__main__':
    mp4_to_gif()
