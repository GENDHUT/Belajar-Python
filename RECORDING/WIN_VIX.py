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
        self.monitor = None
        self.sources = []
        self.preview_running = True
        self.last_frame = None  # Untuk menyimpan frame terakhir
        
        # UI variables
        self.mode_var = tk.StringVar(value="screen")
        self.audio_var = tk.BooleanVar(value=True)
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
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - source selection
        left_panel = tk.LabelFrame(main_container, text="Sumber Rekaman")
        left_panel.pack(side="left", fill="both", padx=(0, 10), pady=5)
        
        # Source controls
        source_controls_frame = tk.Frame(left_panel)
        source_controls_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(source_controls_frame, text="Tambah Sumber:").pack(anchor="w", pady=(0, 5))
        
        # Buttons for source types
        self.screen_btn = tk.Button(
            source_controls_frame, text="Layar Penuh", 
            command=lambda: self.select_source_mode("screen")
        )
        self.screen_btn.pack(fill="x", pady=2)
        
        self.window_btn = tk.Button(
            source_controls_frame, text="Jendela Tertentu", 
            command=lambda: self.select_source_mode("window")
        )
        self.window_btn.pack(fill="x", pady=2)
        
        self.audio_btn = tk.Button(
            source_controls_frame, text="Mikrofon", 
            command=lambda: self.add_source("audio")
        )
        self.audio_btn.pack(fill="x", pady=2)
        
        # Selected sources list
        tk.Label(left_panel, text="Sumber Terpilih:").pack(anchor="w", padx=5, pady=(5, 0))
        self.source_listbox = Listbox(left_panel, height=5)
        self.source_listbox.pack(fill="both", padx=5, pady=(0, 5), expand=True)
        
        # Back button - initially hidden
        self.back_btn = tk.Button(
            left_panel, text="⬅ Kembali", 
            command=self.reset_sources
        )
        
        # Right panel - settings and preview
        right_panel = tk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Settings frame
        settings_frame = tk.LabelFrame(right_panel, text="Pengaturan")
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Mode selection
        mode_frame = tk.Frame(settings_frame)
        mode_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(mode_frame, text="Mode: ").grid(row=0, column=0, sticky="w")
        self.mode_dropdown = ttk.Combobox(
            mode_frame, textvariable=self.mode_var, 
            values=["screen", "window"], state="readonly", width=15
        )
        self.mode_dropdown.grid(row=0, column=1, sticky="w", padx=5)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self.on_mode_change)
        
        # Window selection
        window_frame = tk.Frame(settings_frame)
        window_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(window_frame, text="Jendela:").grid(row=0, column=0, sticky="w")
        self.window_dropdown = ttk.Combobox(
            window_frame, textvariable=self.selected_window, 
            state="readonly", width=30
        )
        self.window_dropdown.grid(row=0, column=1, sticky="w", padx=5)
        self.window_dropdown.bind("<Button-1>", lambda e: self.update_window_dropdown())
        self.window_dropdown.bind("<<ComboboxSelected>>", lambda e: self.select_window_from_dropdown())
        
        # Audio settings
        audio_frame = tk.Frame(settings_frame)
        audio_frame.pack(fill="x", padx=5, pady=5)
        tk.Checkbutton(
            audio_frame, text="Sertakan Audio", 
            variable=self.audio_var
        ).grid(row=0, column=0, sticky="w")
        
        # Quality settings
        quality_frame = tk.Frame(settings_frame)
        quality_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(quality_frame, text="FPS: ").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Combobox(
            quality_frame, textvariable=self.fps_var, 
            values=["20", "30", "60"], state="readonly", width=8
        ).grid(row=0, column=1, padx=5)
        
        tk.Label(quality_frame, text="Resolusi:").grid(row=0, column=2, sticky="w", padx=(15, 5))
        ttk.Combobox(
            quality_frame, textvariable=self.res_var, 
            values=["1080p", "720p", "480p"], state="readonly", width=8
        ).grid(row=0, column=3, padx=5)
        
        # Tombol Mulai di samping pengaturan (di atas preview)
        start_frame = tk.Frame(right_panel)
        start_frame.pack(fill="x", pady=(5, 10))
        
        self.start_btn = tk.Button(
            start_frame, text="▶ Mulai Rekaman", bg="#4CAF50", fg="white", 
            width=15, command=self.start_recording, font=("Arial", 10, "bold")
        )
        self.start_btn.pack(side="right", padx=5)
        
        # Status label di sebelah tombol mulai
        self.status_label = tk.Label(
            start_frame, textvariable=self.status_var, 
            fg="blue", anchor="w"
        )
        self.status_label.pack(side="right", fill="x", expand=True, padx=5)
        
        # Preview frame
        preview_frame = tk.LabelFrame(right_panel, text="Pratinjau")
        preview_frame.pack(fill="both", expand=True)
        
        self.preview_label = tk.Label(preview_frame, bg="black", fg="white")
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize UI state
        self.update_window_dropdown()

    def on_mode_change(self, event):
        """Handle mode change event"""
        mode = self.mode_var.get()
        if mode == "window":
            self.update_window_dropdown()

    def select_source_mode(self, mode):
        """Select recording source mode (screen or window)"""
        self.sources.clear()
        self.source_listbox.delete(0, tk.END)
        
        if mode == "screen":
            self.sources.append("screen")
            self.source_listbox.insert(tk.END, "📺 Layar Penuh")
        elif mode == "window":
            self.update_window_dropdown()
            title = self.selected_window.get()
            if title:
                self.sources.append(f"window:{title}")
                self.source_listbox.insert(tk.END, f"🪟 {title[:40]}{'...' if len(title) > 40 else ''}")

        # Hide source buttons and show back button
        self.screen_btn.pack_forget()
        self.window_btn.pack_forget()
        self.audio_btn.pack_forget()
        self.back_btn.pack(fill="x", pady=5)

    def select_window_from_dropdown(self):
        """Select window from dropdown menu"""
        if self.mode_var.get() == "window":
            self.sources = [f"window:{self.selected_window.get()}"]
            self.source_listbox.delete(0, tk.END)
            title = self.selected_window.get()
            self.source_listbox.insert(tk.END, f"🪟 {title[:40]}{'...' if len(title) > 40 else ''}")

    def reset_sources(self):
        """Reset selected sources"""
        self.sources.clear()
        self.source_listbox.delete(0, tk.END)
        self.back_btn.pack_forget()
        
        # Show source buttons again
        self.screen_btn.pack(fill="x", pady=2)
        self.window_btn.pack(fill="x", pady=2)
        self.audio_btn.pack(fill="x", pady=2)

    def add_source(self, source_type):
        """Add audio source"""
        if source_type == "audio" and "audio" not in self.sources:
            self.sources.append("audio")
            self.source_listbox.insert(tk.END, "🎙 Mikrofon")

    def update_window_dropdown(self):
        """Update the list of available windows"""
        try:
            windows = gw.getWindowsWithTitle('')
            valid = [w for w in windows if w.title and w.visible and 
                    w.width > 100 and w.height > 100 and 
                    "Advanced Screen Recorder" not in w.title]
            self.window_options = [w.title for w in valid]
            self.window_dropdown['values'] = self.window_options
            
            if self.window_options:
                self.selected_window.set(self.window_options[0])
            else:
                self.selected_window.set('')
                messagebox.showwarning("Tidak Ada Jendela", "Tidak ditemukan jendela yang sesuai")
        except Exception as e:
            print(f"Error updating window list: {e}")
            self.window_options = []
            self.window_dropdown['values'] = []
            self.selected_window.set('')

    def get_resolution(self):
        """Get resolution from selection"""
        res_map = {"1080p": (1920, 1080), "720p": (1280, 720), "480p": (854, 480)}
        return res_map[self.res_var.get()]

    def update_preview(self):
        """Update the preview window"""
        if not self.preview_running:
            return
            
        try:
            if self.sources and not self.recording:
                sct = mss.mss()
                monitor = sct.monitors[1] if "screen" in self.sources else None
                
                if any(s.startswith("window:") for s in self.sources):
                    title = self.sources[0].split(":", 1)[1]
                    win = next((w for w in gw.getWindowsWithTitle(title) if w.title == title and w.visible), None)
                    if win:
                        monitor = {"left": win.left, "top": win.top, "width": win.width, "height": win.height}
                
                if monitor:
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                    frame = cv2.resize(frame, (self.preview_width, self.preview_height))
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.preview_label.configure(image=imgtk)
                    self.preview_label.image = imgtk
            else:
                # Show black screen when not capturing
                img = Image.new('RGB', (self.preview_width, self.preview_height), (0, 0, 0))
                imgtk = ImageTk.PhotoImage(image=img)
                self.preview_label.configure(image=imgtk)
                self.preview_label.image = imgtk
        except Exception as e:
            print(f"Preview error: {e}")
            # Show error placeholder
            img = Image.new('RGB', (self.preview_width, self.preview_height), (40, 40, 40))
            imgtk = ImageTk.PhotoImage(image=img)
            self.preview_label.configure(image=imgtk)
            self.preview_label.image = imgtk
            
        self.root.after(150, self.update_preview)

    def start_recording(self):
        """Start recording with countdown"""
        # Validate sources
        if not any(s for s in self.sources if s.startswith("screen") or s.startswith("window")):
            messagebox.showerror("Error", "Tambahkan sumber video terlebih dahulu")
            return
            
        self.status_var.set("Status: Mulai dalam 5 detik...")
        self.start_btn.config(state="disabled")
        self.preview_running = False
        
        # Create countdown thread
        threading.Thread(target=self._start_recording_with_delay, daemon=True).start()

    def _start_recording_with_delay(self):
        """Countdown before starting recording"""
        # Show countdown
        for i in range(5, 0, -1):
            self.status_var.set(f"Status: Mulai dalam {i} detik...")
            time.sleep(1)
            
        # Hide main window
        self.root.withdraw()
            
        # Start recording
        self.status_var.set("Status: Merekam...")
        self.recording = True
        
        # Show control window
        self.show_control_window()
        
        # Start recording thread
        threading.Thread(target=self.record_thread, daemon=True).start()

    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.pause_btn.config(text="▶ Lanjutkan" if self.paused else "⏸ Jeda")
        self.status_var.set("Status: Dijeda" if self.paused else "Status: Merekam")

    def stop_recording(self):
        """Stop recording with countdown"""
        if self.recording:
            self.status_var.set("Status: Mengakhiri dalam 5 detik...")
            
            # Create stop thread
            threading.Thread(target=self._stop_recording_with_delay, daemon=True).start()

    def _stop_recording_with_delay(self):
        """Countdown before stopping recording"""
        # Show countdown
        for i in range(5, 0, -1):
            self.status_var.set(f"Status: Mengakhiri dalam {i} detik...")
            time.sleep(1)
            
        # Stop recording
        self.recording = False
        self.paused = False
        
        # Close control window
        if self.control_window:
            self.control_window.destroy()
            self.control_window = None
            
        # Show main window again
        self.root.deiconify()
        self.preview_running = True
        self.update_preview()
        
        # Re-enable start button
        self.start_btn.config(state="normal")

    def take_screenshot(self):
        """Take screenshot of current frame"""
        if self.last_frame is None:
            messagebox.showwarning("Peringatan", "Tidak ada frame yang tersedia untuk screenshot")
            return
            
        try:
            # Create screenshots directory if not exists
            os.makedirs("screenshots", exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/screenshot_{timestamp}.png"
            
            # Convert frame to RGB for saving
            screenshot = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
            
            # Save the screenshot
            cv2.imwrite(filename, screenshot)
            
            # Show success message
            messagebox.showinfo("Screenshot Berhasil", f"Screenshot disimpan di:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengambil screenshot:\n{e}")

    def show_control_window(self):
        """Show recording control window"""
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
        
        # Tombol Screenshot
        self.screenshot_btn = tk.Button(
            btn_frame, text="📸 Screenshot", bg="#2196F3", fg="white",
            width=15, command=self.take_screenshot
        )
        self.screenshot_btn.pack(side="left", padx=5)
        
        # Tombol Jeda
        self.pause_btn = tk.Button(
            btn_frame, text="⏸ Jeda", width=10, 
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=5)
        
        # Tombol Selesai
        self.stop_btn = tk.Button(
            btn_frame, text="⏹ Selesai", bg="#F44336", fg="white", 
            width=10, command=self.stop_recording
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Handle window close
        self.control_window.protocol("WM_DELETE_WINDOW", self.stop_recording)
        
        # Start preview update for control window
        self.update_control_preview()

    def update_control_preview(self):
        """Update preview in control window"""
        if self.preview_queue and self.control_window:
            frame = self.preview_queue.pop(0)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.control_preview_label.configure(image=imgtk)
            self.control_preview_label.image = imgtk
        
        if self.recording and self.control_window:
            self.control_window.after(50, self.update_control_preview)

    def record_thread(self):
        """Main recording thread"""
        sct = mss.mss()
        resolution = self.get_resolution()
        fps = int(self.fps_var.get())
        samplerate = 44100
        
        # Reset audio frames
        self.audio_frames = []
        
        # Determine video source
        video_source = next(
            (s for s in self.sources if s.startswith("screen") or s.startswith("window")), 
            None
        )
        
        if video_source == "screen":
            mon = sct.monitors[1]
            monitor = {
                "left": mon["left"], 
                "top": mon["top"], 
                "width": mon["width"], 
                "height": mon["height"]
            }
        elif video_source.startswith("window:"):
            title = video_source.split(":", 1)[1]
            win = next(
                (w for w in gw.getWindowsWithTitle(title) 
                if w.title == title and w.visible), None
            )
            if win:
                # Ensure window is restored if minimized
                if win.isMinimized:
                    win.restore()
                    time.sleep(0.5)
                
                monitor = {
                    "left": win.left, 
                    "top": win.top, 
                    "width": win.width, 
                    "height": win.height
                }
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
        
        # Initialize video writer
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
                
                # Save the original frame for potential screenshot
                self.last_frame = frame.copy()
                
                # Resize for video output
                resized_frame = cv2.resize(frame, resolution)
                out.write(resized_frame)
                
                # Capture audio
                if with_audio and self.audio_stream:
                    try:
                        data = self.audio_stream.read(1024, exception_on_overflow=False)
                        self.audio_frames.append(data)
                    except Exception as e:
                        print(f"Audio read error: {e}")
                
                # Prepare preview frame
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
                    wav_file = f"recordings/temp_audio_{timestamp}.wav"
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
            
            # Reset UI
            self.recording = False
            self.paused = False
            
            # Show main window again
            self.root.deiconify()
            
            # Re-enable start button
            self.root.after(100, lambda: self.start_btn.config(state="normal"))

    def on_closing(self):
        """Handle window closing event"""
        if self.recording:
            if messagebox.askokcancel("Keluar", "Rekaman sedang berlangsung. Apakah Anda yakin ingin keluar?"):
                self.stop_recording()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()