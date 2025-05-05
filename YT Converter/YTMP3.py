import os
import yt_dlp

def download_mp3(url):
    """
    Mendownload audio dari YouTube dan menyimpannya sebagai file MP3 ke dalam folder MP3.
    """
    mp3_folder = os.path.join(os.getcwd(), "MP3")
    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(mp3_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'audio')
        print(f"Audio '{title}' berhasil diunduh dan disimpan di folder MP3.")

def main():
    while True:
        url = input("Masukkan Link YouTube (atau ketik 'exit' untuk keluar): ").strip()
        if url.lower() == 'exit':
            print("Program dihentikan.")
            break

        if not url:
            print("URL tidak diberikan. Silakan coba lagi.")
            continue

        try:
            download_mp3(url)
        except Exception as e:
            print("Terjadi kesalahan saat mengunduh audio:", str(e))

        again = input("Ingin unduh MP3 lain? (y/n): ").strip().lower()
        if again == '' or again == 'y':
            continue
        else:
            print("Program dihentikan.")
            break


if __name__ == "__main__":
    main()
