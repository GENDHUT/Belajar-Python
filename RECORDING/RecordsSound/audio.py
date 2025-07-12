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

def get_audio_devices(p):
    """Mendapatkan daftar perangkat audio yang tersedia"""
    devices = []
    for i in range(p.get_device_count()):
        try:
            dev = p.get_device_info_by_index(i)
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

def find_loopback_device(p):
    """Mencari perangkat loopback yang tersedia"""
    loopback_devices = []
    devices = get_audio_devices(p)
    
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

def show_audio_devices(p):
    """Menampilkan semua perangkat audio yang tersedia"""
    devices = get_audio_devices(p)
    
    logger.info("\n===== Daftar Perangkat Audio =====")
    
    # Perangkat Input
    input_devices = [d for d in devices if d['input_channels'] > 0]
    if input_devices:
        logger.info("Perangkat Input:")
        for dev in input_devices:
            logger.info(f"  {dev['index']}: {dev['name']} (Input Channels: {dev['input_channels']}, Sample Rate: {dev['default_samplerate']} Hz)")
    else:
        logger.warning("Tidak ada perangkat input yang terdeteksi!")
    
    # Perangkat Output
    output_devices = [d for d in devices if d['output_channels'] > 0]
    if output_devices:
        logger.info("\nPerangkat Output:")
        for dev in output_devices:
            logger.info(f"  {dev['index']}: {dev['name']} (Output Channels: {dev['output_channels']}, Sample Rate: {dev['default_samplerate']} Hz)")
    else:
        logger.warning("Tidak ada perangkat output yang terdeteksi!")

def check_audio_drivers():
    """Memeriksa status driver audio di Windows"""
    if platform.system() != "Windows":
        return
    
    logger.info("\nMemeriksa driver audio...")
    try:
        result = subprocess.run(
            ['pnputil', '/enum-devices', '/class', 'AudioEndpoint'],
            capture_output=True, text=True, check=True
        )
        
        if "No devices found" in result.stdout:
            logger.error("Tidak ada perangkat audio yang terdeteksi di sistem!")
        else:
            logger.info("Driver audio terdeteksi. Detail:")
            logger.info(result.stdout[:1000] + "...")  # Tampilkan sebagian output
        
        # Periksa layanan audio
        service_result = subprocess.run(
            ['sc', 'query', 'Audiosrv'],
            capture_output=True, text=True, check=True
        )
        if "RUNNING" in service_result.stdout:
            logger.info("Layanan Windows Audio berjalan")
        else:
            logger.error("Layanan Windows Audio tidak berjalan! Coba jalankan:")
            logger.error("net start Audiosrv")
            
    except Exception as e:
        logger.error(f"Gagal memeriksa driver audio: {str(e)}")

def record_loopback(duration=5, sample_rate=44100, output_folder="recordings", device_index=None):
    """Merekam audio loopback menggunakan PyAudio"""
    try:
        # Buat folder penyimpanan jika belum ada
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate nama file berdasarkan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"loopback_{timestamp}.wav"
        output_path = os.path.join(output_folder, filename)
        
        # Konfigurasi audio
        channels = 2  # Stereo
        chunk_size = 1024  # Ukuran buffer
        format = pyaudio.paInt16
        total_frames = int(sample_rate * duration)
        
        p = pyaudio.PyAudio()
        
        # Tampilkan semua perangkat audio
        show_audio_devices(p)
        
        # Cari perangkat loopback
        loopback_devices = find_loopback_device(p)
        
        if not loopback_devices:
            logger.error("\nPerangkat loopback tidak ditemukan secara otomatis!")
            logger.info("\nPanduan Aktivasi Stereo Mix:")
            logger.info("1. Klik kanan ikon speaker di taskbar -> Open Sound settings")
            logger.info("2. Pilih 'Sound Control Panel' di sisi kanan")
            logger.info("3. Buka tab 'Recording'")
            logger.info("4. Klik kanan di area kosong -> pilih 'Show Disabled Devices'")
            logger.info("5. Jika ada 'Stereo Mix', klik kanan -> Enable")
            logger.info("6. Jika tidak ada, Anda mungkin perlu menginstal driver audio yang mendukung loopback")
            
            # Periksa driver audio
            check_audio_drivers()
            return None
        
        # Jika device_index tidak ditentukan, pilih perangkat loopback pertama
        if device_index is None:
            device_index = loopback_devices[0]['index']
            logger.info(f"Menggunakan perangkat loopback: {loopback_devices[0]['name']}")
        
        # Dapatkan info perangkat untuk memastikan konfigurasi
        device_info = p.get_device_info_by_index(device_index)
        actual_sample_rate = int(device_info['defaultSampleRate'])
        
        # Gunakan sample rate perangkat jika berbeda
        if actual_sample_rate != sample_rate:
            logger.warning(f"Sample rate perangkat ({actual_sample_rate} Hz) berbeda dengan yang diminta ({sample_rate} Hz). Menggunakan {actual_sample_rate} Hz.")
            sample_rate = actual_sample_rate
            total_frames = int(sample_rate * duration)
        
        # Persiapkan stream audio
        stream = p.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=chunk_size
        )
        
        logger.info(f"Rekaman dimulai... (Durasi: {duration} detik)")
        frames = []
        start_time = time.time()
        
        # Fungsi untuk menampilkan progress
        def show_progress():
            while not stop_progress:
                elapsed = time.time() - start_time
                progress = min(100.0, (elapsed / duration) * 100)
                logger.info(f"Progress: {progress:.1f}% - Rekam {elapsed:.1f}/{duration} detik")
                time.sleep(0.5)
        
        # Mulai thread progress
        stop_progress = False
        progress_thread = threading.Thread(target=show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Rekam audio
        try:
            for i in range(0, total_frames, chunk_size):
                # Hitung frames yang tersisa
                remaining = total_frames - i
                current_chunk = min(chunk_size, remaining)
                
                # Rekam chunk audio
                data = stream.read(current_chunk)
                frames.append(data)
                
                # Periksa jika durasi tercapai
                if (time.time() - start_time) >= duration:
                    break
        except Exception as e:
            logger.error(f"Error selama rekaman: {str(e)}")
        
        # Stop progress thread
        stop_progress = True
        progress_thread.join(timeout=1.0)
        
        # Stop dan tutup stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        logger.info("Rekaman selesai. Menyimpan file...")
        
        # Simpan ke file WAV
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Hitung durasi aktual
        actual_duration = len(b''.join(frames)) / (sample_rate * channels * (p.get_sample_size(format)))
        logger.info(f"File disimpan di: {output_path}")
        logger.info(f"Durasi aktual: {actual_duration:.2f} detik")
        logger.info(f"Ukuran file: {os.path.getsize(output_path)/1024:.2f} KB")
        
        return output_path
        
    except Exception as e:
        logger.exception(f"Terjadi kesalahan: {str(e)}")
        return None

def install_virtual_cable():
    """Panduan instalasi virtual audio cable"""
    logger.info("\n===== SOLUSI: Instal Virtual Audio Cable =====")
    logger.info("Untuk merekam audio sistem, Anda perlu menginstal virtual audio cable:")
    logger.info("1. VB-Cable (Gratis): https://vb-audio.com/Cable/")
    logger.info("2. VoiceMeeter (Lebih canggih): https://vb-audio.com/Voicemeeter/")
    
    # Coba download otomatis untuk Windows
    if platform.system() == "Windows":
        logger.info("\nMencoba mendownload VB-Cable...")
        try:
            import urllib.request
            url = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip"
            save_path = "VBCABLE_Driver_Pack43.zip"
            
            logger.info(f"Download dari {url}")
            urllib.request.urlretrieve(url, save_path)
            logger.info(f"Download berhasil! File disimpan di {save_path}")
            logger.info("Silakan ekstrak dan instal driver tersebut")
        except Exception as e:
            logger.error(f"Gagal mendownload: {str(e)}")
            logger.info("Silakan download manual dari https://vb-audio.com/Cable/")

def main():
    """Fungsi utama aplikasi"""
    # Cek ketersediaan library
    try:
        import pyaudio
    except ImportError:
        logger.warning("PyAudio belum terinstall")
        if install_dependencies():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Konfigurasi rekaman
    CONFIG = {
        "duration": 10,         # Durasi rekaman (detik)
        "sample_rate": 44100,   # Sample rate (Hz)
        "output_folder": "loopback_recordings"  # Folder penyimpanan
    }
    
    logger.info("===== Audio Loopback Recorder =====")
    logger.info(f"Durasi: {CONFIG['duration']} detik")
    logger.info(f"Sample Rate: {CONFIG['sample_rate']} Hz")
    logger.info(f"Folder Output: {CONFIG['output_folder']}")
    logger.info("Tekan Ctrl+C untuk menghentikan rekaman lebih awal\n")
    
    # Coba rekaman
    result = record_loopback(**CONFIG)
    
    if not result:
        logger.error("\nRekaman gagal! Kemungkinan penyebab:")
        logger.error("1. Tidak ada perangkat input yang terdeteksi")
        logger.error("2. Perangkat loopback tidak diaktifkan")
        logger.error("3. Driver audio tidak mendukung loopback")
        logger.error("4. Tidak ada virtual audio cable terinstal")
        
        # Berikan solusi khusus
        if platform.system() == "Windows":
            install_virtual_cable()
        else:
            logger.info("\nUntuk Linux, coba gunakan perintah berikut:")
            logger.info("sudo apt-get install pavucontrol")
            logger.info("pavucontrol  # Konfigurasi audio")
        
        logger.info("\nLihat file audio_recorder.log untuk detail perangkat")
        sys.exit(1)
    else:
        logger.info("Rekaman berhasil!")
        sys.exit(0)

if __name__ == "__main__":
    main()