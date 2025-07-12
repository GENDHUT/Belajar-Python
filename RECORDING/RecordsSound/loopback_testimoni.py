import sounddevice as sd
import soundfile as sf
import time
import datetime
import sys
import os  # Ditambahkan untuk penanganan direktori

def find_loopback_device():
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
            return idx
    
    # Jika tidak ada VB-Cable, gunakan Stereo Mix
    for idx, dev in loopback_devices:
        if 'stereo mix' in dev['name'].lower():
            print(f"\n⚠️ VB-Cable tidak ditemukan, menggunakan Stereo Mix: [{idx}] {dev['name']}")
            return idx
    
    # Fallback ke default jika tidak ada
    print("\n❌ Perangkat loopback tidak ditemukan! Menggunakan default input device")
    return sd.default.device[0]

def record_system_audio(duration=10):
    # Generate nama file berdasarkan timestamp
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "RecordsSound"
    filename = f"{output_dir}/rec_{current_time}.wav"
    
    # Buat direktori jika belum ada
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"\n📂 Membuat direktori '{output_dir}'")
        except Exception as e:
            print(f"\n❌ Gagal membuat direktori: {str(e)}")
            filename = f"rec_{current_time}.wav"  # Fallback ke direktori saat ini
            print(f"⚠️ Menyimpan di direktori saat ini: {os.getcwd()}")

    device_idx = find_loopback_device()
    sample_rate = 48000  # Meningkatkan kualitas ke 48kHz
    
    print(f"\n⏺️ Recording dimulai selama {duration} detik...")
    print("▶ Putar audio (YouTube, Spotify, Discord, dll)")
    print(f"📁 File akan disimpan sebagai: {filename}")
    print("⎼"*50)
    
    try:
        # Rekam audio dengan buffer lebih besar
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=2,
            device=device_idx,
            dtype='float32',
            blocking=False
        )
        
        # Progress bar animasi
        start_time = time.time()
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            progress = int(elapsed / duration * 50)
            print(f"|{'█' * progress}{' ' * (50-progress)}| {elapsed:.1f}/{duration}s", end='\r')
            time.sleep(0.1)
        
        sd.wait()
        print("\n\n✅ Rekaman selesai!")
        
        # Simpan dengan kualitas tinggi
        sf.write(filename, audio, sample_rate, subtype='PCM_24')
        print(f"💾 File disimpan sebagai '{filename}'")
        print(f"📍 Path lengkap: {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"\n❌ Error selama recording: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*50)
    print("SYSTEM AUDIO RECORDER (Loopback Recording)")
    print("="*50)
    print("Fitur:")
    print("- Auto-detect VB-Cable/Stereo Mix")
    print("- Rekam semua audio sistem (Browser, Game, Discord, dll)")
    print("- Format file: WAV 48kHz/24bit")
    print("- Auto-create output folder")
    print("="*50)
    
    try:
        record_system_audio(duration=30)
    except KeyboardInterrupt:
        print("\n\n⏹️ Rekaman dihentikan pengguna!")