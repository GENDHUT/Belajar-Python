import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import cv2
import numpy as np
import mss
import sounddevice as sd
import soundfile as sf
from datetime import datetime
import subprocess
import sys

# Konfigurasi dasar
VIDEO_DIR = "video"
FPS = 30  # Meningkatkan FPS menjadi 30
SCREEN_WIDTH = 1920  # Resolusi 1080p
SCREEN_HEIGHT = 1080
AUDIO_RATE = 44100

# Buat folder video jika belum ada
os.makedirs(VIDEO_DIR, exist_ok=True)

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.audio_frames = []
        self.video_thread = None
        self.audio_thread = None
        self.stop_event = threading.Event()
        self.countdown_event = threading.Event()
        self.audio_enabled = True
        self.sct = mss.mss()
        
        # Gunakan monitor utama
        self.monitor = self.get_scaled_monitor()
        
    def get_scaled_monitor(self):
        """Dapatkan monitor dengan penyesuaian untuk resolusi 1080p"""
        monitors = self.sct.monitors
        primary_monitor = monitors[1]
        
        # Jika resolusi layar lebih besar dari 1080p, ambil bagian tengah
        if primary_monitor["width"] > SCREEN_WIDTH or primary_monitor["height"] > SCREEN_HEIGHT:
            x = (primary_monitor["width"] - SCREEN_WIDTH) // 2
            y = (primary_monitor["height"] - SCREEN_HEIGHT) // 2
            return {
                "top": y,
                "left": x,
                "width": SCREEN_WIDTH,
                "height": SCREEN_HEIGHT
            }
        
        # Jika resolusi lebih kecil, gunakan seluruh layar (akan di-scaling nanti)
        return primary_monitor
    
    def countdown(self, seconds, callback):
        """Hitung mundur dengan update UI"""
        def _countdown():
            for i in range(seconds, 0, -1):
                if self.stop_event.is_set():
                    return
                callback(i)
                time.sleep(1)
            callback(0)
            self.countdown_event.set()
        
        threading.Thread(target=_countdown, daemon=True).start()
    
    def start_recording(self, countdown_callback):
        """Mulai proses rekaman setelah hitung mundur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_file = os.path.join(VIDEO_DIR, f"temp_video_{timestamp}.avi")
        self.audio_file = os.path.join(VIDEO_DIR, f"temp_audio_{timestamp}.wav")
        self.output_file = os.path.join(VIDEO_DIR, f"recording_{timestamp}.mp4")
        
        # Inisialisasi video writer untuk 1080p
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            self.video_file, fourcc, FPS, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        
        # Inisialisasi audio recorder
        self.audio_frames = []
        self.audio_enabled = True
        
        # Mulai thread rekaman
        self.recording = True
        self.stop_event.clear()
        self.countdown_event.clear()
        
        # Video recording thread
        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()
        
        # Audio recording thread
        try:
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        except Exception as e:
            print(f"Audio recording failed: {e}")
            self.audio_enabled = False
        
        # Hitung mundur 3 detik
        self.countdown(3, countdown_callback)
    
    def record_video(self):
        """Tangkap screenshot dan tulis ke video dengan resolusi 1080p"""
        while not self.countdown_event.is_set():
            time.sleep(0.1)  # Tunggu hitung mundur selesai
        
        while self.recording:
            # Ambil screenshot dengan mss
            sct_img = self.sct.grab(self.monitor)
            
            # Konversi ke array numpy
            img = np.array(sct_img)
            
            # Konversi warna dari BGRA ke BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Resize ke 1080p jika diperlukan
            if img.shape[1] != SCREEN_WIDTH or img.shape[0] != SCREEN_HEIGHT:
                img = cv2.resize(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            self.video_writer.write(img)
            time.sleep(1/FPS)
    
    def record_audio(self):
        """Rekam audio sistem menggunakan loopback"""
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_frames.append(indata.copy())
        
        # Coba gunakan loopback untuk audio output sistem
        try:
            with sd.InputStream(
                samplerate=AUDIO_RATE,
                channels=2,
                callback=audio_callback,
                device=None,  # Default output device
                dtype='float32'
            ):
                while not self.countdown_event.is_set():
                    time.sleep(0.1)  # Tunggu hitung mundur selesai
                
                while self.recording:
                    time.sleep(0.1)
        except sd.PortAudioError as e:
            print(f"Audio error: {e}")
            self.audio_enabled = False
            # Coba metode alternatif jika sounddevice gagal
            self.try_alternative_audio()
    
    def try_alternative_audio(self):
        """Coba metode rekaman audio alternatif"""
        try:
            import pyaudio
            import wave
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            
            p = pyaudio.PyAudio()
            
            # Cari perangkat loopback
            loopback_device = None
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if "loopback" in dev["name"].lower() and dev["maxInputChannels"] > 0:
                    loopback_device = dev["index"]
                    break
            
            if loopback_device is None:
                print("No loopback device found, audio disabled")
                self.audio_enabled = False
                return
            
            self.audio_stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=loopback_device
            )
            
            while not self.countdown_event.is_set():
                time.sleep(0.1)
            
            while self.recording:
                data = self.audio_stream.read(CHUNK)
                self.audio_frames.append(data)
            
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            p.terminate()
            self.audio_enabled = True
        except:
            self.audio_enabled = False
    
    def stop_recording(self, countdown_callback):
        """Hentikan rekaman dan gabungkan video+audio"""
        # Hitung mundur 3 detik untuk stop
        self.countdown(3, countdown_callback)
        time.sleep(3)  # Tunggu hitung mundur selesai
        
        # Hentikan rekaman
        self.recording = False
        self.stop_event.set()
        
        # Tunggu thread selesai
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
        if self.audio_enabled and self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()
        
        # Hentikan perekam video
        if self.video_writer:
            self.video_writer.release()
        
        # Simpan audio jika ada
        if self.audio_enabled and self.audio_frames:
            self.save_audio()
        
        # Gabungkan video dan audio
        self.merge_audio_video()
        
        # Hapus file temporary
        if os.path.exists(self.video_file):
            os.remove(self.video_file)
        if self.audio_enabled and self.audio_frames and os.path.exists(self.audio_file):
            os.remove(self.audio_file)
    
    def save_audio(self):
        """Simpan rekaman audio ke file WAV"""
        if not self.audio_frames:
            return
        
        # Handle different audio frame formats
        if isinstance(self.audio_frames[0], np.ndarray):
            audio_data = np.concatenate(self.audio_frames, axis=0)
            sf.write(self.audio_file, audio_data, AUDIO_RATE)
        else:  # Assume it's byte data from PyAudio
            wf = wave.open(self.audio_file, 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(AUDIO_RATE)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
    
    def merge_audio_video(self):
        """Gabungkan video dan audio menggunakan FFmpeg dengan kualitas tinggi"""
        if self.audio_enabled and self.audio_frames:
            command = [
                'ffmpeg',
                '-i', self.video_file,
                '-i', self.audio_file,
                '-c:v', 'libx264',  # Codec video modern
                '-preset', 'fast',  # Balance between speed and compression
                '-crf', '23',       # Quality level (0-51, lower is better)
                '-c:a', 'aac',
                '-b:a', '192k',     # Bitrate audio
                '-strict', 'experimental',
                '-s', f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}',  # Pastikan output 1080p
                self.output_file
            ]
        else:
            # Jika audio tidak diaktifkan, hanya konversi video
            command = [
                'ffmpeg',
                '-i', self.video_file,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-s', f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}',
                self.output_file
            ]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Error", "FFmpeg not found! Please install FFmpeg and add to PATH")

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HD Screen Recorder")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Set icon
        try:
            self.root.iconbitmap("recorder.ico")
        except:
            pass
        
        self.recorder = ScreenRecorder()
        self.setup_ui()
    
    def setup_ui(self):
        # Style configuration
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 10), anchor="center")
        style.configure("Header.TLabel", font=("Arial", 11, "bold"))
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            main_frame, 
            text="HD Screen Recorder (1080p @ 30FPS)",
            style="Header.TLabel"
        )
        header.pack(pady=(0, 10))
        
        # Countdown label
        self.countdown_label = ttk.Label(main_frame, text="")
        self.countdown_label.pack(pady=5)
        
        # Record button
        self.record_btn = ttk.Button(
            main_frame,
            text="Start Recording",
            command=self.toggle_recording,
            width=20
        )
        self.record_btn.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to record", wraplength=350)
        self.status_label.pack(pady=5)
        
        # Audio status
        self.audio_status = ttk.Label(main_frame, text="Audio: System output", foreground="green")
        self.audio_status.pack(pady=2)
    
    def toggle_recording(self):
        if not self.recorder.recording:
            self.record_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Preparing recording...")
            self.recorder.start_recording(self.update_countdown)
        else:
            self.record_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Finishing recording...")
            self.recorder.stop_recording(self.update_countdown)
    
    def update_countdown(self, seconds):
        if seconds > 0:
            self.countdown_label.config(text=f"Starting in: {seconds}...")
        else:
            if self.recorder.recording:
                self.countdown_label.config(text="Recording...")
                self.record_btn.config(state=tk.NORMAL, text="Stop Recording")
                self.status_label.config(text="Recording in progress - 1080p @ 30FPS")
                
                # Update audio status
                if self.recorder.audio_enabled:
                    self.audio_status.config(text="Audio: System output", foreground="green")
                else:
                    self.audio_status.config(text="Audio: Disabled", foreground="red")
            else:
                self.countdown_label.config(text="Recording saved successfully!")
                self.record_btn.config(state=tk.NORMAL, text="Start Recording")
                self.status_label.config(text=f"Saved to: {os.path.basename(self.recorder.output_file)}")
                self.audio_status.config(text="Audio: System output", foreground="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()