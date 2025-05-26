import os
import yt_dlp

def progress_hook(d):
    if d['status'] == 'downloading':
        filename = d.get('filename', '...')
        total_bytes = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = downloaded_bytes / total_bytes * 100 if total_bytes else 0
        print(f"\r⬇️  Mengunduh: {os.path.basename(filename)} - {percent:.1f}% ", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\n✅ Selesai: {os.path.basename(d['filename'])}")

def download_single_video(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'noplaylist': True,
        'progress_hooks': [progress_hook],
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        print(f"🎵 Audio '{info.get('title', 'unknown')}' berhasil diunduh.")

def download_playlist(url, base_dir):
    print("📥 Mengambil daftar video dari playlist...")

    flat_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(flat_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get('entries', [])
        playlist_title = info.get('title', 'playlist')

    playlist_folder = os.path.join(base_dir, playlist_title)
    os.makedirs(playlist_folder, exist_ok=True)

    print(f"\n🎶 Playlist: {playlist_title} ({len(entries)} video)\n")

    for index, entry in enumerate(entries, start=1):
        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
        print(f"\n🔹 [{index}/{len(entries)}] Mendownload: {entry['title']}")
        try:
            download_single_video(video_url, playlist_folder)
        except Exception as e:
            print(f"❌ Gagal download {entry['title']}: {e}")

    print(f"\n✅ Playlist '{playlist_title}' selesai diunduh ke folder MP3/{playlist_title}")

def main():
    base_dir = os.path.join(os.getcwd(), "MP3")
    os.makedirs(base_dir, exist_ok=True)

    while True:
        url = input("\nMasukkan Link YouTube (atau ketik 'exit' untuk keluar): ").strip()
        if url.lower() == 'exit':
            print("👋 Program dihentikan.")
            break

        if not url:
            print("⚠️  URL tidak diberikan. Silakan coba lagi.")
            continue

        # Deteksi otomatis apakah link adalah playlist
        try:
            test_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }

            with yt_dlp.YoutubeDL(test_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    download_playlist(url, base_dir)
                else:
                    download_single_video(url, base_dir)

        except Exception as e:
            print(f"❌ Terjadi kesalahan: {e}")

        again = input("Ingin unduh MP3 lain? (y/n): ").strip().lower()
        if again not in ('y', ''):
            print("👋 Program dihentikan.")
            break

if __name__ == "__main__":
    main()
