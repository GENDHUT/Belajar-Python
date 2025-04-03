import os
import yt_dlp
from moviepy.editor import AudioFileClip

def get_available_formats(url):
    """
    Mengambil informasi video dan menyaring format mp4 yang memiliki video (dan height).
    Jika ada pilihan format dengan audio, maka lebih diprioritaskan.
    """
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = info.get("formats", [])
    
    # Filter untuk format mp4 yang memiliki video dan informasi resolusi (height)
    filtered_formats = [f for f in formats if f.get("ext") == "mp4" and f.get("vcodec") != "none" and f.get("height")]
    
    # Buat dictionary unik berdasarkan resolusi (misal "720p")
    unique = {}
    for f in filtered_formats:
        res = f.get("height")
        res_str = f"{res}p"
        # Jika belum ada atau jika format sebelumnya tidak memiliki audio (acodec == "none")
        if res_str not in unique or (unique[res_str].get("acodec") == "none" and f.get("acodec") != "none"):
            unique[res_str] = f

    # Urutkan resolusi dari tinggi ke rendah
    resolutions = sorted(unique.keys(), key=lambda x: int(x[:-1]), reverse=True)
    return unique, resolutions

def download_video(url, format_str):
    """
    Mendownload video dengan format_str yang dipilih.
    Jika format_str merupakan format gabungan (video+audio), yt-dlp akan mengunduh kedua stream dan menggabungkannya.
    Video disimpan di folder VIDEO.
    """
    video_folder = os.path.join(os.getcwd(), "VIDEO")
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',  # pastikan hasilnya dalam format mp4 jika perlu digabungkan
        'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    print("Video berhasil diunduh:", filename)
    return filename

def convert_to_mp3(video_path):
    """
    Mengkonversi file video menjadi MP3 menggunakan moviepy dan menyimpannya di folder MP3.
    """
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    mp3_folder = os.path.join(os.getcwd(), "MP3")
    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder)
    mp3_path = os.path.join(mp3_folder, base_name + ".mp3")
    print("Mengkonversi video ke MP3...")
    audioclip = AudioFileClip(video_path)
    audioclip.write_audiofile(mp3_path)
    audioclip.close()
    print("Konversi selesai:", mp3_path)
    return mp3_path

def main():
    while True:  # Menambahkan loop untuk mengulang proses
        url = input("Masukan Link Youtube (atau ketik 'exit' untuk keluar): ").strip()
        if url.lower() == "exit":  # Menambahkan opsi untuk keluar dari loop
            print("Program dihentikan.")
            break  # Keluar dari loop jika pengguna mengetik 'exit'
        
        if not url:
            print("URL tidak diberikan. Silakan coba lagi.")
            continue  # Kembali ke awal loop jika URL kosong

        try:
            unique_formats, resolutions = get_available_formats(url)
        except Exception as e:
            print("Terjadi kesalahan saat mengambil info video:", str(e))
            continue  # Kembali ke awal loop jika ada error saat mengambil info video

        if not resolutions:
            print("Tidak ada format video yang cocok ditemukan.")
            continue  # Kembali ke awal loop jika tidak ada format yang tersedia

        print("Pilih resolusi video:")
        for i, res in enumerate(resolutions, start=1):
            print(f"{i}. {res}")
        choice = input("Masukan pilihan (default 1): ").strip()
        if choice == "":
            choice = "1"
        try:
            index = int(choice) - 1
            if index < 0 or index >= len(resolutions):
                print("Pilihan tidak valid, menggunakan resolusi tertinggi secara default.")
                selected_res = resolutions[0]
            else:
                selected_res = resolutions[index]
        except ValueError:
            print("Pilihan tidak valid, menggunakan resolusi tertinggi secara default.")
            selected_res = resolutions[0]

        chosen_format = unique_formats[selected_res]
        # Jika format yang dipilih tidak memiliki audio, maka gunakan format gabungan video+audio
        if chosen_format.get("acodec") == "none":
            height = chosen_format.get("height")
            format_str = f"bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/best"
        else:
            format_str = chosen_format.get("format_id")

        video_path = download_video(url, format_str)

        convert = input("Apakah anda ingin mengkonversi video ke MP3? (y/n, default n): ").strip().lower()
        if convert == "y":
            convert_to_mp3(video_path)
        else:
            print("Proses download selesai.")

        # Tanyakan apakah pengguna ingin mengunduh video lain
        continue_choice = input("Apakah anda ingin mengunduh video lain? (y/n): ").strip().lower()
        if continue_choice != "y":
            print("Program dihentikan.")
            break  # Jika jawabannya bukan 'y', keluar dari loop


if __name__ == "__main__":
    main()
