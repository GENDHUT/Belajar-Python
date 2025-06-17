import tkinter as tk
from tkinter import ttk, messagebox, Listbox
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
from PIL import Image, ImageTk

class ScreenRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Screen Recorder")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # State variables
        self.recording = False
        self.paused = False
        self.control_window = None
        self.preview_window = None
        self.monitor = None
        self.sources = []
        
        # UI variables
        self.mode_var = tk.StringVar(value="screen")
        self.audio_var = tk.BooleanVar(value=True)  # Checkbox audio
        self.fps_var = tk.StringVar(value="30")
        self.res_var = tk.StringVar(value="1080p")
        self.status_var = tk.StringVar(value="Status: Siap")
        self.selected_window = tk.StringVar()
        self.window_options = []
        
        # Preview variables
        self.preview_queue = []
        self.preview_width = 640
        self.preview_height = 360
        
        # Audio variables
        self.audio_frames = []
        self.audio_stream = None
        self.audio = None
        
        # Build the UI
        self.build_ui()
        
        # Start preview update
        self.update_preview()

    def build_ui(self):
        # Main frames
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - source selection
        left_frame = tk.LabelFrame(main_frame, text="Sumber Rekaman", width=200)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(left_frame, text="Tambah Sumber:").pack(pady=5, anchor="w")
        tk.Button(left_frame, text="Layar Penuh", command=lambda: self.add_source("screen")).pack(fill="x", pady=2)
        tk.Button(left_frame, text="Jendela Tertentu", command=self.add_window_source).pack(fill="x", pady=2)
        tk.Button(left_frame, text="Mikrofon", command=lambda: self.add_source("audio")).pack(fill="x", pady=2)
        
        tk.Label(left_frame, text="Sumber Terpilih:").pack(pady=5, anchor="w")
        self.source_listbox = Listbox(left_frame, height=5)
        self.source_listbox.pack(fill="both", pady=5, expand=True)
        
        # Right panel - settings and preview
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Settings
        settings_frame = tk.LabelFrame(right_frame, text="Pengaturan")
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Mode selection
        mode_frame = tk.Frame(settings_frame)
        mode_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(mode_frame, text="Mode:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(mode_frame, textvariable=self.mode_var, 
                    values=["screen", "window"], state="readonly", width=15).grid(row=0, column=1, sticky="w", padx=5)
        
        # Window selection
        window_frame = tk.Frame(settings_frame)
        window_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(window_frame, text="Jendela:").grid(row=0, column=0, sticky="w")
        self.window_dropdown = ttk.Combobox(window_frame, textvariable=self.selected_window, 
                                          state="readonly", width=30)
        self.window_dropdown.grid(row=0, column=1, sticky="w", padx=5)
        
        # Audio selection
        audio_frame = tk.Frame(settings_frame)
        audio_frame.pack(fill="x", padx=5, pady=5)
        tk.Checkbutton(audio_frame, text="Sertakan Audio", variable=self.audio_var).grid(row=0, column=0, sticky="w")
        
        # FPS and resolution
        grid_frame = tk.Frame(settings_frame)
        grid_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(grid_frame, text="FPS:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Combobox(grid_frame, textvariable=self.fps_var, values=["20", "30", "60"], 
                   state="readonly", width=8).grid(row=0, column=1, padx=5)
        
        tk.Label(grid_frame, text="Resolusi:").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Combobox(grid_frame, textvariable=self.res_var, values=["1080p", "720p", "480p"], 
                   state="readonly", width=8).grid(row=1, column=1, padx=5, pady=5)
        
        # Preview area
        preview_frame = tk.LabelFrame(right_frame, text="Pratinjau")
        preview_frame.pack(fill="both", expand=True)
        self.preview_label = tk.Label(preview_frame, text="Pratinjau akan muncul di sini", 
                                    bg="black", fg="white", height=15)
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status and controls
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, fg="blue", anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        control_frame = tk.Frame(status_frame)
        control_frame.pack(side="right")
        
        self.start_btn = tk.Button(control_frame, text="▶ Mulai", bg="green", fg="white", 
                                 width=10, command=self.toggle_recording)
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = tk.Button(control_frame, text="⏸ Jeda", state="disabled", 
                                 width=10, command=self.toggle_pause)
        self.pause_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹ Selesai", bg="red", fg="white", 
                                state="disabled", width=10, command=self.stop_recording)
        self.stop_btn.pack(side="left", padx=5)
        
        # Initialize UI state
        self.update_window_dropdown()

    def add_source(self, source_type):
        if source_type == "screen" and "screen" not in self.sources:
            self.sources.append("screen")
            self.source_listbox.insert(tk.END, "📺 Layar Penuh")
        elif source_type == "audio" and "audio" not in self.sources:
            self.sources.append("audio")
            self.source_listbox.insert(tk.END, "🎙 Mikrofon")

    def add_window_source(self):
        windows = gw.getWindowsWithTitle('')
        valid_windows = [w for w in windows if w.title and w.visible]
        if valid_windows:
            title = valid_windows[0].title
            source_id = f"window:{title}"
            if source_id not in self.sources:
                self.sources.append(source_id)
                self.source_listbox.insert(tk.END, f"🪟 {title[:40]}{'...' if len(title) > 40 else ''}")
        else:
            messagebox.showerror("Error", "Tidak ada jendela yang tersedia")

    def update_window_dropdown(self):
        windows = gw.getWindowsWithTitle('')
        valid_windows = [w for w in windows if w.title and w.visible and w.width > 100 and w.height > 100]
        self.window_options = [w.title for w in valid_windows]
        self.window_dropdown['values'] = self.window_options
        if self.window_options:
            self.selected_window.set(self.window_options[0])
        else:
            self.selected_window.set('')

    def get_resolution(self):
        res_map = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}
        return res_map[self.res_var.get()]

    def toggle_recording(self):
        if not self.recording:
            # Validate sources
            if not any(s for s in self.sources if s.startswith("screen") or s.startswith("window")):
                messagebox.showerror("Error", "Tambahkan sumber video terlebih dahulu")
                return
                
            # Prepare recording
            self.recording = True
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
            self.status_var.set("Status: Mempersiapkan rekaman...")
            
            # Hide main window
            self.root.withdraw()
            
            # Start recording in a separate thread
            threading.Thread(target=self.record_thread, daemon=True).start()
            
            # Show control window
            self.show_control_window()
        else:
            self.toggle_pause()

    def toggle_pause(self):
        if self.recording:
            self.paused = not self.paused
            if self.paused:
                self.pause_btn.config(text="▶ Lanjutkan")
                self.status_var.set("Status: Dijeda")
            else:
                self.pause_btn.config(text="⏸ Jeda")
                self.status_var.set("Status: Merekam")

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.status_var.set("Status: Menyelesaikan rekaman...")
            if self.control_window:
                self.control_window.destroy()

    def show_control_window(self):
        self.control_window = tk.Toplevel()
        self.control_window.title("Kontrol Rekaman")
        self.control_window.geometry("800x600")
        self.control_window.resizable(True, True)
        self.control_window.attributes("-topmost", True)
        
        # Preview in control window
        preview_frame = tk.Frame(self.control_window)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.control_preview_label = tk.Label(preview_frame, bg="black")
        self.control_preview_label.pack(fill="both", expand=True)
        
        # Control buttons
        btn_frame = tk.Frame(self.control_window)
        btn_frame.pack(pady=10)
        
        pause_btn = tk.Button(btn_frame, text="⏸ Jeda", width=10, command=self.toggle_pause)
        pause_btn.pack(side="left", padx=5)
        
        stop_btn = tk.Button(btn_frame, text="⏹ Selesai", bg="red", fg="white", 
                           width=10, command=self.stop_recording)
        stop_btn.pack(side="left", padx=5)
        
        # Handle window close
        self.control_window.protocol("WM_DELETE_WINDOW", self.stop_recording)
        
        # Start preview update
        self.update_control_preview()

    def update_preview(self):
        # Update main window preview
        if self.preview_queue:
            frame = self.preview_queue.pop(0)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.preview_label.configure(image=imgtk)
            self.preview_label.image = imgtk
        
        if not self.recording:
            self.root.after(100, self.update_preview)

    def update_control_preview(self):
        # Update control window preview
        if self.preview_queue:
            frame = self.preview_queue.pop(0)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.control_preview_label.configure(image=imgtk)
            self.control_preview_label.image = imgtk
        
        if self.recording and self.control_window:
            self.control_window.after(50, self.update_control_preview)

    def record_thread(self):
        sct = mss.mss()
        resolution = self.get_resolution()
        fps = int(self.fps_var.get())
        samplerate = 44100
        
        # Reset audio frames
        self.audio_frames = []
        
        # Determine video source
        video_source = next((s for s in self.sources if s.startswith("screen") or s.startswith("window")), None)
        
        if video_source == "screen":
            mon = sct.monitors[1]
            monitor = {"left": mon["left"], "top": mon["top"], "width": mon["width"], "height": mon["height"]}
        elif video_source.startswith("window:"):
            title = video_source.split(":", 1)[1]
            win = next((w for w in gw.getWindowsWithTitle(title) if w.title == title and w.visible), None)
            if win:
                # Ensure window is restored if minimized
                if win.isMinimized:
                    win.restore()
                    time.sleep(0.5)
                
                monitor = {"left": win.left, "top": win.top, "width": win.width, "height": win.height}
            else:
                messagebox.showerror("Error", "Jendela tidak ditemukan")
                self.stop_recording()
                return
        
        # Setup audio if needed
        self.audio = None
        self.audio_stream = None
        with_audio = "audio" in self.sources and self.audio_var.get()
        
        if with_audio:
            try:
                self.audio = pyaudio.PyAudio()
                self.audio_stream = self.audio.open(
                    format=pyaudio.paInt16, 
                    channels=2,
                    rate=samplerate,
                    input=True,
                    frames_per_buffer=1024
                )
                self.status_var.set("Status: Audio diaktifkan...")
            except Exception as e:
                messagebox.showwarning("Audio Error", f"Gagal mengakses mikrofon:\n{e}")
                with_audio = False
        
        # Create output directory
        os.makedirs("recordings", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_file = f"recordings/temp_video_{timestamp}.avi"
        final_file = f"recordings/recording_{timestamp}.mp4"
        
        # Initialize video writer with better codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_file, fourcc, fps, resolution)
        
        self.status_var.set("Status: Merekam...")
        last_frame_time = time.time()
        frame_count = 0
        
        try:
            while self.recording:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                start_time = time.time()
                
                # Capture screen
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, resolution)
                out.write(frame)
                
                # Capture audio
                if with_audio and self.audio_stream:
                    try:
                        data = self.audio_stream.read(1024, exception_on_overflow=False)
                        self.audio_frames.append(data)
                    except Exception as e:
                        print(f"Audio read error: {e}")
                
                # Update preview
                preview_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                preview_frame = cv2.resize(preview_frame, (self.preview_width, self.preview_height))
                
                if len(self.preview_queue) < 3:  # Limit queue size
                    self.preview_queue.append(preview_frame)
                
                # Maintain accurate FPS
                frame_time = time.time() - start_time
                sleep_time = max(0, (1.0 / fps) - frame_time)
                time.sleep(sleep_time)
                
                # Calculate actual FPS
                frame_count += 1
                if time.time() - last_frame_time >= 1.0:
                    actual_fps = frame_count / (time.time() - last_frame_time)
                    self.status_var.set(f"Status: Merekam... ({actual_fps:.1f} FPS)")
                    frame_count = 0
                    last_frame_time = time.time()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat rekaman:\n{e}")
            self.status_var.set(f"Error: {str(e)}")
        finally:
            # Release video resources
            out.release()
            
            # Release audio resources
            if with_audio and self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                if self.audio:
                    self.audio.terminate()
            
            # Save audio if available
            wav_file = None
            if with_audio and self.audio_frames:
                try:
                    wav_file = f"temp_audio_{timestamp}.wav"
                    with wave.open(wav_file, 'wb') as wf:
                        wf.setnchannels(2)
                        wf.setsampwidth(2)
                        wf.setframerate(samplerate)
                        wf.writeframes(b''.join(self.audio_frames))
                    self.status_var.set("Status: Menyimpan audio...")
                except Exception as e:
                    messagebox.showerror("Audio Error", f"Gagal menyimpan audio: {e}")
                    wav_file = None
            
            # Process final output
            self.status_var.set("Status: Memproses video...")
            
            try:
                if wav_file and os.path.exists(wav_file):
                    # Combine video and audio
                    self.status_var.set("Status: Menggabungkan audio...")
                    subprocess.run([
                        "ffmpeg", "-y",
                        "-i", video_file,
                        "-i", wav_file,
                        "-c:v", "copy",  # Keep original video codec
                        "-c:a", "aac",
                        "-b:a", "192k",
                        "-shortest",  # Match video duration
                        final_file
                    ], check=True)
                    os.remove(video_file)
                    os.remove(wav_file)
                else:
                    # Convert to MP4 without audio
                    self.status_var.set("Status: Mengkonversi video...")
                    subprocess.run([
                        "ffmpeg", "-y",
                        "-i", video_file,
                        "-c:v", "libx264",
                        "-preset", "medium",
                        "-crf", "23",
                        final_file
                    ], check=True)
                    os.remove(video_file)
                    
                self.status_var.set(f"✅ Rekaman tersimpan di: {final_file}")
                
            except subprocess.CalledProcessError as e:
                messagebox.showerror("FFmpeg Error", f"Gagal memproses video:\n{e}")
                self.status_var.set("Status: Gagal memproses video")
            except Exception as e:
                messagebox.showerror("Error", f"Kesalahan umum: {e}")
                self.status_var.set("Status: Gagal memproses video")
            
            # Reset UI and show main window
            self.recording = False
            self.paused = False
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled", text="⏸ Jeda")
            self.stop_btn.config(state="disabled")
            
            # Show main window again
            self.root.deiconify()

    def on_closing(self):
        if self.recording:
            self.stop_recording()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()