import os
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def download_single_video(entry, mp3_folder):
    """
    Mengunduh satu video dari data playlist (entry) ke file MP3.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(mp3_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(entry['url'], download=True)
            return info.get('title', 'audio')
    except Exception as e:
        return f"[Gagal] {entry['url']} ({str(e)})"


def download_mp3(url):
    """
    Mengunduh audio dari YouTube video tunggal atau playlist.
    Menggunakan multi-threading dan progress bar.
    """
    mp3_folder = os.path.join(os.getcwd(), "MP3")
    os.makedirs(mp3_folder, exist_ok=True)

    # Ekstrak info awal tanpa download
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)

    if 'entries' in info:  # Playlist
        entries = info['entries']
        print(f"Playlist ditemukan: {info.get('title', 'Tanpa Judul')} ({len(entries)} video)")

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(download_single_video, entry, mp3_folder): entry for entry in entries}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Mengunduh playlist", unit="video"):
                result = future.result()
                tqdm.write(f"Selesai: {result}")

    else:  # Single video
        print("Video tunggal ditemukan, memulai unduhan...")
        title = download_single_video(info, mp3_folder)
        print(f"Audio '{title}' berhasil diunduh.")


def main():
    while True:
        url = input("Masukkan Link YouTube (video/playlist) [atau ketik 'exit']: ").strip()
        if url.lower() == 'exit':
            print("Program dihentikan.")
            break

        if not url:
            print("URL tidak boleh kosong.")
            continue

        try:
            download_mp3(url)
        except Exception as e:
            print("Terjadi kesalahan saat mengunduh:", str(e))

        again = input("Ingin mengunduh lagi? (y/n): ").strip().lower()
        if again not in ['y', 'yes', '']:
            print("Program dihentikan.")
            break


if __name__ == "__main__":
    main()
