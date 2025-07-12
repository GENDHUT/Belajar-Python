import sounddevice as sd
import soundfile as sf
import time
import datetime
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import subprocess

class AudioRecorder:
    def __init__(self):
        self.device_idx = None
        self.sample_rate = 48000
        self.audio = None
        self.is_recording = False
        self.is_paused = False
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_duration = 0.0
        self.recording_thread = None
        self.wav_filename = ""
        self.mp3_filename = ""
        self.output_dir = "RecordsSound"
        self.stream = None
        self.current_audio = None
        
        # Buat folder output jika belum ada
        os.makedirs(self.output_dir, exist_ok=True)
        
    def find_loopback_device(self):
        """Mencari perangkat loopback (VB-Cable/Stereo Mix) secara otomatis"""
        devices = sd.query_devices()
        loopback_devices = []
        
        print("\n🔍 Scanning perangkat loopback...")
        for i, dev in enumerate(devices):
            dev_name = dev['name'].lower()
            # Cek perangkat yang didukung
            if 'cable' in dev_name or 'stereo mix' in dev_name or 'loopback' in dev_name:
                print(f"  - Ditemukan: [{i}] {dev['name']} (Input Channels: {dev['max_input_channels']})")
                loopback_devices.append((i, dev))
        
        # Prioritaskan VB-Cable jika ada
        for idx, dev in loopback_devices:
            if 'cable' in dev['name'].lower():
                print(f"\n✅ Menggunakan VB-Cable: [{idx}] {dev['name']}")
                self.device_idx = idx
                return True
        
        # Jika tidak ada VB-Cable, gunakan Stereo Mix
        for idx, dev in loopback_devices:
            if 'stereo mix' in dev['name'].lower():
                print(f"\n⚠️ VB-Cable tidak ditemukan, menggunakan Stereo Mix: [{idx}] {dev['name']}")
                self.device_idx = idx
                return True
        
        # Fallback ke default jika tidak ada
        print("\n❌ Perangkat loopback tidak ditemukan! Menggunakan default input device")
        self.device_idx = sd.default.device[0]
        return False
    
    def start_recording(self):
        """Memulai rekaman audio"""
        # Reset paused duration
        self.total_paused_duration = 0.0
        
        # Generate nama file berdasarkan timestamp
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.wav_filename = f"{self.output_dir}/rec_{current_time}.wav"
        self.mp3_filename = f"{self.output_dir}/rec_{current_time}.mp3"
        
        self.is_recording = True
        self.is_paused = False
        self.start_time = time.time()
        
        # Inisialisasi buffer audio
        self.current_audio = np.empty((0, 2), dtype='float32')
        
        # Rekam audio di thread terpisah
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def record_audio(self):
        """Fungsi untuk merekam audio di thread terpisah"""
        try:
            # Mulai stream
            self.stream = sd.InputStream(
                device=self.device_idx,
                channels=2,
                samplerate=self.sample_rate,
                dtype='float32',
                blocksize=1024
            )
            self.stream.start()
            
            while self.is_recording:
                if self.is_paused:
                    # Jika di-pause, tidur sebentar untuk menghemat CPU
                    time.sleep(0.1)
                else:
                    # Baca data audio
                    data, overflowed = self.stream.read(1024)
                    if data.size > 0:
                        # Tambahkan ke buffer audio
                        self.current_audio = np.vstack((self.current_audio, data))
            
            # Rekaman selesai, simpan file
            self.save_recording()
        
        except Exception as e:
            print(f"\n❌ Error selama recording: {str(e)}")
        finally:
            # Pastikan stream ditutup
            if self.stream:
                self.stream.stop()
                self.stream.close()
    
    def save_recording(self):
        """Menyimpan rekaman setelah selesai"""
        if self.current_audio is not None and self.current_audio.size > 0:
            # Simpan WAV dengan kualitas tinggi
            sf.write(self.wav_filename, self.current_audio, self.sample_rate, subtype='PCM_24')
            print(f"💾 File WAV disimpan sebagai '{self.wav_filename}'")
            
            # Konversi ke MP3 menggunakan FFmpeg
            self.convert_to_mp3()
    
    def convert_to_mp3(self):
        """Konversi rekaman WAV ke MP3 menggunakan FFmpeg"""
        try:
            # Pastikan file WAV ada
            if not os.path.exists(self.wav_filename):
                print(f"❌ File WAV tidak ditemukan: {self.wav_filename}")
                return
            
            # Perintah FFmpeg untuk konversi
            command = [
                "ffmpeg",
                "-y",  # Overwrite output file without asking
                "-i", self.wav_filename,
                "-codec:a", "libmp3lame",
                "-q:a", "2",  # Quality: 0-9 (0=best)
                self.mp3_filename
            ]
            
            # Jalankan FFmpeg
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Cek hasil
            if result.returncode == 0:
                print(f"💾 File MP3 disimpan sebagai '{self.mp3_filename}'")
            else:
                print(f"❌ Error konversi ke MP3: {result.stderr}")
                # Hapus file MP3 yang mungkin terbuat sebagian
                if os.path.exists(self.mp3_filename):
                    os.remove(self.mp3_filename)
                self.mp3_filename = None
            
        except Exception as e:
            print(f"\n❌ Error konversi ke MP3: {str(e)}")
            self.mp3_filename = None
    
    def pause_recording(self):
        """Menjeda rekaman"""
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            self.pause_start_time = time.time()
            print("⏸️ Rekaman dijeda")
    
    def resume_recording(self):
        """Melanjutkan rekaman"""
        if self.is_recording and self.is_paused:
            self.is_paused = False
            # Hitung durasi pause dan tambahkan ke total
            pause_duration = time.time() - self.pause_start_time
            self.total_paused_duration += pause_duration
            print("▶️ Rekaman dilanjutkan")
    
    def stop_recording(self):
        """Menghentikan rekaman"""
        if self.is_recording:
            self.is_recording = False
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            print("⏹️ Rekaman dihentikan")
            
            # Kembalikan nama file untuk ditampilkan di UI
            return self.wav_filename, self.mp3_filename
        return None, None

class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Audio Recorder")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Inisialisasi recorder
        self.recorder = AudioRecorder()
        
        # Variabel UI
        self.status_var = tk.StringVar(value="Mencari perangkat loopback...")
        self.timer_var = tk.StringVar(value="00:00:00")
        self.record_button_text = tk.StringVar(value="Mulai Rekam")
        self.pause_button_text = tk.StringVar(value="Jeda")
        
        # Variabel waktu
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_duration = 0.0
        self.timer_running = False
        
        # Status warna
        self.status_color = "black"
        
        # Cari perangkat loopback
        self.check_devices()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Frame utama
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            foreground=self.status_color,
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Timer display
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, pady=10)
        
        self.timer_label = ttk.Label(
            timer_frame, 
            textvariable=self.timer_var,
            font=("Arial", 20, "bold"),
            foreground="blue"
        )
        self.timer_label.pack()
        
        # Tombol-tombol
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.record_button = ttk.Button(
            button_frame,
            textvariable=self.record_button_text,
            command=self.start_recording,
            state=tk.DISABLED
        )
        self.record_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_button = ttk.Button(
            button_frame,
            textvariable=self.pause_button_text,
            command=self.toggle_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Selesai",
            command=self.stop_recording,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Indikator status
        self.status_indicator = tk.Canvas(main_frame, width=30, height=30, bg="white", highlightthickness=0)
        self.status_indicator.pack(pady=10)
        self.indicator = self.status_indicator.create_oval(5, 5, 25, 25, fill="gray")
    
    def check_devices(self):
        """Memeriksa perangkat loopback di thread terpisah"""
        def thread_task():
            device_found = self.recorder.find_loopback_device()
            if device_found:
                self.status_var.set("Perangkat ditemukan. Siap merekam!")
                self.status_color = "green"
                self.status_label.config(foreground=self.status_color)
                self.record_button.config(state=tk.NORMAL)
                self.update_indicator("ready")
            else:
                self.status_var.set("Perangkat loopback tidak ditemukan!")
                self.status_color = "red"
                self.status_label.config(foreground=self.status_color)
                self.update_indicator("error")
                messagebox.showerror("Error", "Perangkat loopback tidak ditemukan. Pastikan VB-Cable atau Stereo Mix diaktifkan.")
        
        threading.Thread(target=thread_task, daemon=True).start()
    
    def update_indicator(self, state):
        """Memperbarui indikator status"""
        if state == "ready":
            self.status_indicator.itemconfig(self.indicator, fill="gray")
        elif state == "countdown":
            self.status_indicator.itemconfig(self.indicator, fill="orange")
        elif state == "recording":
            self.status_indicator.itemconfig(self.indicator, fill="green")
            self.flash_indicator()
        elif state == "paused":
            self.status_indicator.itemconfig(self.indicator, fill="red")
        elif state == "error":
            self.status_indicator.itemconfig(self.indicator, fill="red")
    
    def flash_indicator(self):
        """Membuat indikator berkedip saat merekam"""
        if self.recorder.is_recording and not self.recorder.is_paused:
            current_color = self.status_indicator.itemcget(self.indicator, "fill")
            new_color = "dark green" if current_color == "green" else "green"
            self.status_indicator.itemconfig(self.indicator, fill=new_color)
            self.root.after(500, self.flash_indicator)
    
    def start_recording(self):
        """Memulai rekaman dengan hitung mundur"""
        # Reset timer variables
        self.start_time = None
        self.pause_start_time = None
        self.total_paused_duration = 0.0
        
        self.record_button.config(state=tk.DISABLED)
        self.status_var.set("Bersiap merekam...")
        self.update_indicator("countdown")
        self.countdown(3)
    
    def countdown(self, seconds):
        """Hitung mundur sebelum mulai rekaman"""
        if seconds > 0:
            self.status_var.set(f"Mulai dalam {seconds}...")
            self.timer_var.set(str(seconds))
            self.root.after(1000, lambda: self.countdown(seconds-1))
        else:
            self.status_var.set("Sedang merekam...")
            self.status_color = "blue"
            self.status_label.config(foreground=self.status_color)
            
            # Mulai rekaman
            self.recorder.start_recording()
            self.record_button_text.set("🔴 Rekaman")
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            
            # Mulai timer
            self.start_time = time.time()
            self.update_timer()
            self.update_indicator("recording")
    
    def update_timer(self):
        """Memperbarui timer setiap detik"""
        if self.recorder.is_recording:
            # Hitung waktu rekaman aktual (dikurangi waktu pause)
            if self.recorder.is_paused:
                # Jika sedang pause, gunakan waktu terakhir sebelum pause
                elapsed = self.pause_start_time - self.start_time - self.total_paused_duration
            else:
                elapsed = time.time() - self.start_time - self.total_paused_duration
            
            # Format ke HH:MM:SS
            hours, remainder = divmod(int(elapsed), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def resume_countdown(self, seconds):
        """Hitung mundur sebelum melanjutkan rekaman"""
        if seconds > 0:
            self.status_var.set(f"Melanjutkan dalam {seconds}...")
            self.timer_var.set(str(seconds))
            self.root.after(1000, lambda: self.resume_countdown(seconds-1))
        else:
            # Lanjutkan rekaman setelah hitung mundur
            self.recorder.resume_recording()
            self.pause_button_text.set("⏸ Jeda")
            self.status_var.set("Sedang merekam...")
            self.status_color = "blue"
            self.status_label.config(foreground=self.status_color)
            self.update_indicator("recording")
            
            # Aktifkan tombol
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            
            # Lanjutkan timer
            self.update_timer()
    
    def toggle_pause(self):
        """Menjeda atau melanjutkan rekaman"""
        if self.recorder.is_recording:
            if not self.recorder.is_paused:
                # Jeda rekaman
                self.recorder.pause_recording()
                self.pause_button_text.set("▶ Lanjut")
                self.status_var.set("Rekaman dijeda")
                self.status_color = "orange"
                self.status_label.config(foreground=self.status_color)
                self.update_indicator("paused")
                
                # Catat waktu mulai pause untuk timer
                self.pause_start_time = time.time()
            else:
                # Nonaktifkan tombol selama hitung mundur
                self.pause_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                
                # Mulai hitung mundur untuk melanjutkan
                self.status_var.set("Bersiap melanjutkan...")
                self.status_color = "orange"
                self.status_label.config(foreground=self.status_color)
                self.update_indicator("countdown")
                
                # Mulai hitung mundur 3 detik
                self.resume_countdown(3)
    
    def stop_recording(self):
        """Menghentikan rekaman"""
        wav_file, mp3_file = self.recorder.stop_recording()
        self.record_button_text.set("Mulai Rekam")
        self.pause_button_text.set("⏸ Jeda")
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.record_button.config(state=tk.NORMAL)
        self.status_var.set("Rekaman selesai. Siap merekam lagi.")
        self.status_color = "green"
        self.status_label.config(foreground=self.status_color)
        self.timer_var.set("00:00:00")
        self.update_indicator("ready")
        
        # Tampilkan pesan sukses
        if wav_file:
            if mp3_file:
                messagebox.showinfo("Sukses", 
                                   f"Rekaman disimpan sebagai:\n\n"
                                   f"WAV: {wav_file}\n"
                                   f"MP3: {mp3_file}")
            else:
                messagebox.showinfo("Sukses", 
                                   f"Rekaman disimpan sebagai:\n\n"
                                   f"WAV: {wav_file}\n"
                                   f"MP3: Tidak dibuat (konversi gagal)")

def check_ffmpeg():
    """Memeriksa apakah FFmpeg terinstal"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if "ffmpeg version" in result.stdout or "ffmpeg version" in result.stderr:
            return True
        return False
    except:
        return False

def main():
    # Beri tahu jika FFmpeg tidak terinstal
    if not check_ffmpeg():
        messagebox.showwarning(
            "Peringatan", 
            "FFmpeg tidak ditemukan! Konversi ke MP3 tidak akan berfungsi.\n\n"
            "Silakan instal FFmpeg dari: https://ffmpeg.org/\n"
            "Dan tambahkan ke PATH sistem Anda."
        )
    
    root = tk.Tk()
    app = RecorderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()