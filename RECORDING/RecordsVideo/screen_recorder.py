import mss
import cv2
import numpy as np
import pyaudio
import wave
import time
import subprocess
import pygetwindow as gw
import os
import keyboard
from datetime import datetime

def countdown(message="Mulai dalam", seconds=3):
    for i in range(seconds, 0, -1):
        print(f"{message} {i}...")
        time.sleep(1)

def choose_window():
    windows = gw.getWindowsWithTitle('')
    valid_windows = [w for w in windows if w.title and w.isVisible]

    if not valid_windows:
        print("Tidak ada jendela yang bisa direkam.")
        return None

    print("Pilih jendela untuk direkam:")
    for i, win in enumerate(valid_windows):
        print(f"{i + 1}. {win.title}")

    idx = int(input("Masukkan nomor pilihan: ") or "1") - 1
    if 0 <= idx < len(valid_windows):
        win = valid_windows[idx]
        return {
            "left": win.left,
            "top": win.top,
            "width": win.width,
            "height": win.height
        }
    else:
        print("Pilihan tidak valid.")
        return None

def resize_frame(frame, target_width, target_height):
    return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

def record_screen(monitor, output_video, fps, resolution, with_audio):
    sct = mss.mss()
    target_width, target_height = resolution
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video, fourcc, fps, (target_width, target_height))

    audio = []
    audio_rec = None
    samplerate = 44100

    if with_audio:
        try:
            audio_rec = pyaudio.PyAudio()
            stream = audio_rec.open(format=pyaudio.paInt16,
                                    channels=2,
                                    rate=samplerate,
                                    input=True,
                                    input_device_index=None,  # None untuk default
                                    frames_per_buffer=1024)
        except Exception as e:
            print(f"[PERINGATAN] Tidak bisa mengakses mikrofon: {e}")
            print("[INFO] Melanjutkan rekaman tanpa audio.")
            with_audio = False

    print("\n[INFO] Tekan 'Space' untuk pause/resume, 'Esc' untuk berhenti.")
    countdown("Mulai dalam")

    paused = False
    print("🔴 Rekaman dimulai...")

    try:
        while True:
            start_time = time.time()

            if keyboard.is_pressed("esc"):
                print("\n🛑 Mengakhiri rekaman...")
                countdown("Mengakhiri dalam")
                break

            if keyboard.is_pressed("space"):
                paused = not paused
                print("⏸️ Dijeda..." if paused else "▶️ Lanjut rekaman...")
                if not paused:
                    countdown("Lanjut dalam")
                time.sleep(1)  # debounce

            if paused:
                time.sleep(0.1)
                continue

            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            frame_resized = resize_frame(frame, target_width, target_height)
            out.write(frame_resized)

            if with_audio:
                audio_data = stream.read(1024)
                audio.append(audio_data)

            # Delay agar fps sesuai
            elapsed = time.time() - start_time
            sleep_time = max(0, (1 / fps) - elapsed)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("Rekaman dihentikan dengan CTRL+C.")
    finally:
        out.release()
        if with_audio and audio_rec:
            stream.stop_stream()
            stream.close()
            audio_rec.terminate()
            with wave.open("temp_audio.wav", 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(b''.join(audio))
        print("🛑 Rekaman selesai.")

def merge_audio_video(video_path, audio_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd)

def main():
    print("=== Aplikasi Screen Recorder CLI ===")
    print("1. Rekam seluruh layar (default)")
    print("2. Rekam jendela tertentu")
    mode = input("Pilih mode (1/2): ") or "1"

    if mode == "1":
        monitor = mss.mss().monitors[1]
    elif mode == "2":
        monitor = choose_window()
        if monitor is None:
            return
    else:
        print("Pilihan tidak valid.")
        return

    audio_mode = input("Pilih mode audio (1: dengan suara / 2: tanpa suara) [default: 1]: ") or "1"
    with_audio = audio_mode == "1"

    fps_choice = input("Pilih FPS (1: 20 / 2: 30) [default: 2]: ") or "2"
    fps = 20 if fps_choice == "1" else 30

    res_choice = input("Pilih resolusi (1: 1080p / 2: 720p / 3: 480p) [default: 1]: ") or "1"
    resolution_map = {
        "1": (1920, 1080),
        "2": (1280, 720),
        "3": (854, 480)
    }
    resolution = resolution_map.get(res_choice, (1920, 1080))

    os.makedirs("record", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_name = f"record/temp_video_{timestamp}.avi"
    final_name = f"record/hasil_recording_{timestamp}.mp4"

    record_screen(
        monitor=monitor,
        output_video=video_name,
        fps=fps,
        resolution=resolution,
        with_audio=with_audio
    )

    if with_audio and os.path.exists("temp_audio.wav"):
        merge_audio_video(video_name, "temp_audio.wav", final_name)
        time.sleep(1)  # Pastikan file tidak sedang dipakai
        try:
            os.remove(video_name)
            os.remove("temp_audio.wav")
        except PermissionError:
            print("[PERINGATAN] File masih digunakan. Tidak bisa menghapus sementara.")
    else:
        os.rename(video_name, final_name)

    print(f"✅ File tersimpan di: {final_name}")

if __name__ == "__main__":
    main()
