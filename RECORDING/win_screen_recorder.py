import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import cv2
import numpy as np
import mss
import wave
import pyaudio
import subprocess
import pygetwindow as gw
from datetime import datetime

class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder GUI")
        self.root.geometry("420x400")
        self.root.resizable(False, False)

        self.recording = False
        self.paused = False
        self.preview_window = None
        self.monitor = None

        self.mode_var = tk.StringVar(value="1")
        self.audio_var = tk.BooleanVar(value=True)
        self.fps_var = tk.StringVar(value="30")
        self.res_var = tk.StringVar(value="1080p")
        self.status_var = tk.StringVar(value="Status: Siap")
        self.window_options = []
        self.selected_window = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        pad = {'padx': 10, 'pady': 5}

        tk.Label(self.root, text="Mode Rekam:").pack(**pad)
        tk.Radiobutton(self.root, text="Seluruh Layar", variable=self.mode_var, value="1", command=self.update_window_dropdown).pack()
        tk.Radiobutton(self.root, text="Jendela Tertentu", variable=self.mode_var, value="2", command=self.update_window_dropdown).pack()

        self.window_dropdown = ttk.Combobox(self.root, textvariable=self.selected_window, state="readonly")
        self.window_dropdown.pack(pady=5)

        ttk.Separator(self.root).pack(fill="x", pady=10)

        tk.Checkbutton(self.root, text="Dengan Suara", variable=self.audio_var).pack()

        tk.Label(self.root, text="FPS:").pack(**pad)
        ttk.Combobox(self.root, textvariable=self.fps_var, values=["20", "30"], state="readonly").pack()

        tk.Label(self.root, text="Resolusi:").pack(**pad)
        ttk.Combobox(self.root, textvariable=self.res_var, values=["1080p", "720p", "480p"], state="readonly").pack()

        ttk.Separator(self.root).pack(fill="x", pady=10)

        self.start_btn = tk.Button(self.root, text="Mulai Rekam", command=self.toggle_recording, bg="#4CAF50", fg="white")
        self.start_btn.pack(pady=10)

        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=5)

        self.update_window_dropdown()

    def update_window_dropdown(self):
        if self.mode_var.get() == "2":
            windows = gw.getWindowsWithTitle('')
            valid_windows = [w for w in windows if w.title and w.isVisible]
            self.window_options = [w.title for w in valid_windows]
            self.window_dropdown['values'] = self.window_options
            if self.window_options:
                self.selected_window.set(self.window_options[0])
            else:
                self.selected_window.set('')
        else:
            self.window_dropdown['values'] = []
            self.selected_window.set('')

    def toggle_recording(self):
        if not self.recording:
            self.start_btn.config(state="disabled")
            threading.Thread(target=self.start_recording).start()
        else:
            pass  # handled in UI window

    def start_recording(self):
        self.recording = True
        self.status_var.set("Mempersiapkan rekaman...")

        if self.mode_var.get() == "1":
            self.monitor = mss.mss().monitors[1]
        else:
            title = self.selected_window.get()
            if not title:
                messagebox.showerror("Error", "Tidak ada jendela yang dipilih.")
                self.reset_ui()
                return
            win = next((w for w in gw.getWindowsWithTitle(title) if w.title == title), None)
            if not win:
                messagebox.showerror("Error", "Jendela tidak ditemukan.")
                self.reset_ui()
                return
            self.monitor = {"left": win.left, "top": win.top, "width": win.width, "height": win.height}

        with_audio = self.audio_var.get()
        fps = int(self.fps_var.get())
        resolution_map = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}
        resolution = resolution_map[self.res_var.get()]
        samplerate = 44100

        os.makedirs("record", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = f"record/temp_video_{timestamp}.avi"
        final_name = f"record/hasil_recording_{timestamp}.mp4"

        sct = mss.mss()
        out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'XVID'), fps, resolution)

        audio_frames = []
        audio = None

        if with_audio:
            try:
                audio = pyaudio.PyAudio()
                stream = audio.open(format=pyaudio.paInt16, channels=2, rate=samplerate, input=True, frames_per_buffer=1024)
            except Exception as e:
                messagebox.showwarning("Audio Error", f"Gagal mengakses mikrofon:\n{e}")
                with_audio = False

        self.show_recording_ui(video_name, final_name)

        try:
            while self.recording:
                if self.paused:
                    time.sleep(0.1)
                    continue
                img = np.array(sct.grab(self.monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame_resized = cv2.resize(frame, resolution)
                out.write(frame_resized)
                if with_audio:
                    audio_frames.append(stream.read(1024))
                time.sleep(1 / fps)
        finally:
            out.release()
            if with_audio:
                stream.stop_stream()
                stream.close()
                audio.terminate()
                with wave.open("temp_audio.wav", 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(samplerate)
                    wf.writeframes(b''.join(audio_frames))

            if with_audio and os.path.exists("temp_audio.wav"):
                subprocess.run(["ffmpeg", "-y", "-i", video_name, "-i", "temp_audio.wav", "-c:v", "libx264",
                                "-preset", "ultrafast", "-crf", "28", "-c:a", "aac", final_name])
                os.remove(video_name)
                os.remove("temp_audio.wav")
            else:
                os.rename(video_name, final_name)

            self.status_var.set(f"✅ Tersimpan: {final_name}")
            self.recording_window.destroy()
            self.reset_ui()

    def show_recording_ui(self, video_name, final_name):
        self.recording_window = tk.Toplevel(self.root)
        self.recording_window.title("Sedang Merekam")
        self.recording_window.geometry("200x100")
        self.recording_window.attributes('-topmost', True)
        self.recording_window.protocol("WM_DELETE_WINDOW", lambda: None)  # prevent close

        tk.Button(self.recording_window, text="⏸ Pause", command=self.toggle_pause).pack(pady=5)
        tk.Button(self.recording_window, text="🛑 Selesai", command=self.stop_recording).pack(pady=5)

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.status_var.set("Status: Dijeda")
        else:
            self.status_var.set("Status: Merekam")

    def stop_recording(self):
        self.recording = False

    def reset_ui(self):
        self.recording = False
        self.paused = False
        self.start_btn.config(state="normal")
        self.status_var.set("Status: Siap")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.mainloop()
