from moviepy.editor import VideoFileClip
import os

def convert_mp4_to_mp3(input_file, output_file=None):
    # Jika nama output tidak diberikan, otomatis buat .mp3
    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".mp3"

    print(f"Memproses: {input_file}")
    try:
        video = VideoFileClip(input_file)
        audio = video.audio
        audio.write_audiofile(output_file)
        audio.close()
        video.close()
        print(f"Berhasil! File MP3 disimpan di: {output_file}")
    except Exception as e:
        print("Terjadi kesalahan:", e)

if __name__ == "__main__":
    print("=== MP4 ke MP3 Converter ===")
    file_input = input("Masukkan path file MP4: ").strip()
    convert_mp4_to_mp3(file_input)
