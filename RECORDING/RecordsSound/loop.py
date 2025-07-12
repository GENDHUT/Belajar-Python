import pyaudio
import wave
import numpy as np
from datetime import datetime
import os
import logging
import sys
import time
import threading
import platform
import subprocess
from pydub import AudioSegment
import tkinter as tk
from tkinter import ttk, messagebox
import math

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("audio_recorder.log")
    ]
)
logger = logging.getLogger()

class AudioRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.is_paused = False
        self.output_folder = "loopback_recordings"
        self.wav_filename = ""
        self.start_time = None
        self.device_index = None
        self.sample_rate = 44100
        self.channels = 2
        self.format = pyaudio.paInt16
        self.chunk_size = 1024

    def get_audio_devices(self):
        """Mendapatkan daftar perangkat audio yang tersedia"""
        devices = []
        for i in range(self.p.get_device_count()):
            try:
                dev = self.p.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': dev['name'],
                    'input_channels': dev['maxInputChannels'],
                    'output_channels': dev['maxOutputChannels'],
                    'default_samplerate': dev['defaultSampleRate']
                })
            except Exception as e:
                logger.error(f"Error mendapatkan info perangkat {i}: {str(e)}")
        return devices

    def find_loopback_device(self):
        """Mencari perangkat loopback yang tersedia"""
        loopback_devices = []
        devices = self.get_audio_devices()
        
        logger.info("Mencari perangkat loopback...")
        
        # Daftar nama umum untuk perangkat loopback
        loopback_names = [
            'Stereo Mix', 'What U Hear', 'Waveout Mix',
            'Loopback', 'Virtual Cable', 'CABLE Output',
            'VB-Audio', 'VoiceMeeter', 'CABLE Input'
        ]
        
        for dev in devices:
            if dev['input_channels'] > 0:
                # Cek apakah nama perangkat mengandung salah satu nama loopback
                if any(name.lower() in dev['name'].lower() for name in loopback_names):
                    loopback_devices.append(dev)
                    logger.info(f"Perangkat loopback ditemukan: {dev['name']} (Index: {dev['index']})")
        
        return loopback_devices

    def select_loopback_device(self):
        """Memilih perangkat loopback, return device index jika ditemukan, None jika tidak"""
        loopback_devices = self.find_loopback_device()
        if loopback_devices:
            # Pilih perangkat pertama
            self.device_index = loopback_devices[0]['index']
            logger.info(f"Menggunakan perangkat loopback: {loopback_devices[0]['name']}")
            return self.device_index
        else:
            logger.error("Tidak ada perangkat loopback yang ditemukan!")
            return None

    def start_recording(self):
        """Memulai rekaman"""
        if self.device_index is None:
            logger.error("Perangkat loopback tidak tersedia!")
            return False

        # Generate nama file WAV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wav_filename = os.path.join(self.output_folder, f"loopback_{timestamp}.wav")
        
        # Buat folder jika belum ada
        os.makedirs(self.output_folder, exist_ok=True)

        # Dapatkan sample rate perangkat
        device_info = self.p.get_device_info_by_index(self.device_index)
        actual_sample_rate = int(device_info['defaultSampleRate'])
        if actual_sample_rate != self.sample_rate:
            logger.warning(f"Sample rate perangkat ({actual_sample_rate} Hz) berbeda dengan yang diminta ({self.sample_rate} Hz). Menggunakan {actual_sample_rate} Hz.")
            self.sample_rate = actual_sample_rate

        # Buka stream
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )

        self.frames = []
        self.is_recording = True
        self.is_paused = False
        self.start_time = time.time()

        # Thread untuk rekaman
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.daemon = True
        self.recording_thread.start()

        logger.info("Rekaman dimulai...")
        return True

    def record(self):
        """Thread untuk merekam audio"""
        while self.is_recording:
            if not self.is_paused:
                try:
                    data = self.stream.read(self.chunk_size)
                    self.frames.append(data)
                except Exception as e:
                    logger.error(f"Error membaca audio: {str(e)}")
                    break
            else:
                time.sleep(0.1)  # Tunggu jika pause

    def pause(self):
        """Jeda rekaman"""
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            logger.info("Rekaman dijeda")

    def unpause(self):
        """Lanjutkan rekaman"""
        if self.is_recording and self.is_paused:
            self.is_paused = False
            logger.info("Rekaman dilanjutkan")

    def stop_recording(self):
        """Menghentikan rekaman dan menyimpan file"""
        if self.is_recording:
            self.is_recording = False
            # Tunggu thread rekaman selesai
            self.recording_thread.join(timeout=1.0)
            
            # Stop stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            
            logger.info("Rekaman dihentikan. Menyimpan file...")
            
            # Simpan ke WAV
            wf = wave.open(self.wav_filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            
            # Konversi ke MP3
            mp3_filename = self.wav_filename.replace('.wav', '.mp3')
            try:
                sound = AudioSegment.from_wav(self.wav_filename)
                sound.export(mp3_filename, format="mp3", bitrate="192k")
                logger.info(f"File MP3 disimpan: {mp3_filename}")
            except Exception as e:
                logger.error(f"Gagal konversi ke MP3: {str(e)}")
            
            # Hitung durasi
            duration = time.time() - self.start_time
            logger.info(f"Durasi rekaman: {duration:.2f} detik")
            logger.info(f"File WAV: {self.wav_filename}")
            
            return self.wav_filename, mp3_filename
        return None, None

    def close(self):
        """Bersihkan resources"""
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loopback Audio Recorder")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Inisialisasi recorder
        self.recorder = AudioRecorder()
        
        # Variabel UI
        self.status_var = tk.StringVar(value="Mencari perangkat loopback...")
        self.timer_var = tk.StringVar(value="00:00:00")
        self.record_button_text = tk.StringVar(value="Record")
        self.pause_button_text = tk.StringVar(value="Pause")
        
        # Warna status
        self.status_color = "black"
        
        # Cari perangkat loopback
        self.check_devices()
        
        # Layout
        self.setup_ui()
        
    def setup_ui(self):
        # Frame utama
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_label = ttk.Label(status_frame, text="Status:")
        status_label.pack(side=tk.LEFT)
        
        self.status_display = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            foreground=self.status_color
        )
        self.status_display.pack(side=tk.LEFT, padx=5)
        
        # Timer
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, pady=10)
        
        timer_label = ttk.Label(timer_frame, text="Durasi:")
        timer_label.pack(side=tk.LEFT)
        
        self.timer_display = ttk.Label(
            timer_frame, 
            textvariable=self.timer_var,
            font=("Arial", 14, "bold")
        )
        self.timer_display.pack(side=tk.LEFT, padx=5)
        
        # Canvas untuk indikator status
        self.canvas = tk.Canvas(main_frame, width=50, height=50, bg="white", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.indicator = self.canvas.create_oval(10, 10, 40, 40, fill="gray")
        
        # Tombol Record
        self.record_button = ttk.Button(
            main_frame, 
            textvariable=self.record_button_text,
            command=self.toggle_record,
            state=tk.DISABLED
        )
        self.record_button.pack(fill=tk.X, pady=5)
        
        # Tombol Pause
        self.pause_button = ttk.Button(
            main_frame, 
            textvariable=self.pause_button_text,
            command=self.toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(fill=tk.X, pady=5)
        
        # Tombol Stop
        self.stop_button = ttk.Button(
            main_frame, 
            text="Stop Recording",
            command=self.stop_recording,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=5)
        
        # Timer update
        self.timer_running = False
        
    def check_devices(self):
        """Cari perangkat loopback di thread terpisah agar tidak freeze UI"""
        def thread_check():
            device_index = self.recorder.select_loopback_device()
            if device_index is not None:
                self.status_var.set("Perangkat loopback ditemukan. Siap merekam.")
                self.status_color = "green"
                self.status_display.config(foreground=self.status_color)
                self.record_button.config(state=tk.NORMAL)
                self.update_indicator("ready")
            else:
                self.status_var.set("Perangkat loopback tidak ditemukan!")
                self.status_color = "red"
                self.status_display.config(foreground=self.status_color)
                self.update_indicator("error")
                messagebox.showerror("Error", "Perangkat loopback tidak ditemukan. Pastikan Stereo Mix atau VB-Cable diaktifkan.")
        
        threading.Thread(target=thread_check, daemon=True).start()
    
    def update_indicator(self, state):
        """Update indikator status"""
        if state == "ready":
            self.canvas.itemconfig(self.indicator, fill="green")
        elif state == "recording":
            self.canvas.itemconfig(self.indicator, fill="green")
            self.flash_indicator()
        elif state == "paused":
            self.canvas.itemconfig(self.indicator, fill="red")
        elif state == "error":
            self.canvas.itemconfig(self.indicator, fill="red")
    
    def flash_indicator(self):
        """Buat indikator berkedip saat merekam"""
        if self.recorder.is_recording and not self.recorder.is_paused:
            current_color = self.canvas.itemcget(self.indicator, "fill")
            new_color = "dark green" if current_color == "green" else "green"
            self.canvas.itemconfig(self.indicator, fill=new_color)
            self.root.after(500, self.flash_indicator)
    
    def toggle_record(self):
        """Mulai rekaman dengan hitung mundur"""
        self.record_button.config(state=tk.DISABLED)
        self.countdown(3)
    
    def countdown(self, seconds):
        """Hitung mundur sebelum mulai rekaman"""
        if seconds > 0:
            self.status_var.set(f"Mulai rekaman dalam {seconds}...")
            self.root.after(1000, lambda: self.countdown(seconds-1))
        else:
            self.status_var.set("Sedang merekam...")
            self.status_color = "blue"
            self.status_display.config(foreground=self.status_color)
            # Mulai rekaman
            if self.recorder.start_recording():
                self.record_button_text.set("Recording...")
                self.pause_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.NORMAL)
                # Mulai timer
                self.start_timer()
                self.update_indicator("recording")
            else:
                self.status_var.set("Gagal memulai rekaman!")
                self.record_button.config(state=tk.NORMAL)
    
    def start_timer(self):
        """Mulai menghitung durasi rekaman"""
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update timer setiap detik"""
        if self.timer_running:
            elapsed = time.time() - self.start_time
            # Format ke HH:MM:SS
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        self.timer_running = False
    
    def toggle_pause(self):
        """Jeda atau lanjutkan rekaman"""
        if self.recorder.is_recording:
            if not self.recorder.is_paused:
                self.recorder.pause()
                self.pause_button_text.set("Unpause")
                self.status_var.set("Rekaman dijeda")
                self.status_color = "red"
                self.status_display.config(foreground=self.status_color)
                # Timer dihentikan sementara
                self.stop_timer()
                self.update_indicator("paused")
            else:
                self.recorder.unpause()
                self.pause_button_text.set("Pause")
                self.status_var.set("Sedang merekam...")
                self.status_color = "blue"
                self.status_display.config(foreground=self.status_color)
                # Timer dilanjutkan
                self.start_timer()
                self.update_indicator("recording")
    
    def stop_recording(self):
        """Stop rekaman"""
        wav_file, mp3_file = self.recorder.stop_recording()
        self.record_button_text.set("Record")
        self.pause_button_text.set("Pause")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.NORMAL)
        self.status_var.set("Rekaman selesai. Siap merekam lagi.")
        self.status_color = "green"
        self.status_display.config(foreground=self.status_color)
        self.stop_timer()
        self.timer_var.set("00:00:00")
        self.update_indicator("ready")
        
        if wav_file and mp3_file:
            messagebox.showinfo("Sukses", f"Rekaman berhasil disimpan:\nWAV: {wav_file}\nMP3: {mp3_file}")
    
    def on_closing(self):
        """Tutup aplikasi"""
        if hasattr(self.recorder, 'is_recording') and self.recorder.is_recording:
            self.recorder.stop_recording()
        self.recorder.close()
        self.root.destroy()

def install_pydub():
    """Instal pydub jika belum ada"""
    try:
        import pydub
    except ImportError:
        import subprocess
        import sys
        logger.info("Menginstal pydub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
        logger.info("pydub berhasil diinstal!")

def main():
    # Pastikan pydub terinstal untuk konversi MP3
    install_pydub()
    
    root = tk.Tk()
    app = RecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()