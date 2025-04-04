import os
from flask import Flask, request, render_template_string, redirect, url_for, send_file, flash
import yt_dlp
from moviepy.editor import AudioFileClip

app = Flask(__name__)
app.secret_key = "secret-key"  # diperlukan untuk flash messages

# Tentukan folder download (akan dibuat jika belum ada)
BASE_DIR = os.getcwd()
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

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
    Mengunduh video dengan format_str yang dipilih.
    Video disimpan di folder DOWNLOAD_FOLDER/VIDEO.
    """
    video_folder = os.path.join(DOWNLOAD_FOLDER, "VIDEO")
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)
    
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

def convert_to_mp3(video_path):
    """
    Mengkonversi file video menjadi MP3 menggunakan moviepy dan menyimpannya di folder DOWNLOAD_FOLDER/MP3.
    """
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    mp3_folder = os.path.join(DOWNLOAD_FOLDER, "MP3")
    if not os.path.exists(mp3_folder):
        os.makedirs(mp3_folder)
    mp3_path = os.path.join(mp3_folder, base_name + ".mp3")
    audioclip = AudioFileClip(video_path)
    audioclip.write_audiofile(mp3_path)
    audioclip.close()
    return mp3_path

# Template halaman index: input URL
INDEX_HTML = """
<!doctype html>
<title>YouTube Converter</title>
<h1>YouTube Converter</h1>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul style="color: red;">
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
<form action="{{ url_for('formats') }}" method="post">
  <label>Masukkan URL YouTube:</label>
  <input type="text" name="url" size="60" required>
  <input type="submit" value="Ambil Format">
</form>
"""

# Template halaman format: memilih resolusi dan opsi konversi
FORMATS_HTML = """
<!doctype html>
<title>Pilih Format</title>
<h1>Pilih Resolusi Video</h1>
<p>Judul Video: {{ title }}</p>
<form action="{{ url_for('download') }}" method="post">
  <input type="hidden" name="url" value="{{ url }}">
  <label>Pilih Resolusi:</label>
  <select name="resolution">
    {% for res in resolutions %}
      <option value="{{ res }}">{{ res }}</option>
    {% endfor %}
  </select>
  <br><br>
  <label>
    <input type="checkbox" name="convert" value="1">
    Konversi ke MP3
  </label>
  <br><br>
  <input type="submit" value="Download">
</form>
"""

# Template halaman selesai: menampilkan link download
RESULT_HTML = """
<!doctype html>
<title>Download Selesai</title>
<h1>Proses Selesai</h1>
<p>{{ message }}</p>
{% if file_url %}
  <p><a href="{{ file_url }}" download>Unduh file</a></p>
{% endif %}
<p><a href="{{ url_for('index') }}">Kembali ke awal</a></p>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)

@app.route("/formats", methods=["POST"])
def formats():
    url = request.form.get("url").strip()
    if not url:
        flash("URL harus diisi.")
        return redirect(url_for("index"))
    try:
        # Ambil info video untuk mendapatkan title dan format
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown Title")
        unique_formats, resolutions = get_available_formats(url)
        if not resolutions:
            flash("Tidak ada format video yang cocok ditemukan.")
            return redirect(url_for("index"))
        # Simpan unique_formats dalam session atau lewat form tersembunyi (di sini kita tidak menyimpan, 
        # tapi akan re-ekstrak di route download)
        return render_template_string(FORMATS_HTML, url=url, title=title, resolutions=resolutions)
    except Exception as e:
        flash("Terjadi kesalahan saat mengambil info video: " + str(e))
        return redirect(url_for("index"))

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url").strip()
    selected_res = request.form.get("resolution")
    convert_option = request.form.get("convert")
    if not url or not selected_res:
        flash("URL atau resolusi tidak valid.")
        return redirect(url_for("index"))
    try:
        unique_formats, resolutions = get_available_formats(url)
        chosen_format = unique_formats.get(selected_res)
        if not chosen_format:
            flash("Format tidak ditemukan untuk resolusi yang dipilih.")
            return redirect(url_for("index"))
        if chosen_format.get("acodec") == "none":
            height = chosen_format.get("height")
            format_str = f"bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/best"
        else:
            format_str = chosen_format.get("format_id")
        video_path = download_video(url, format_str)
    except Exception as e:
        return render_template_string(RESULT_HTML, message="Gagal mengunduh video: " + str(e), file_url=None)
    
    message = "Video berhasil diunduh: " + video_path
    file_to_download = video_path
    if convert_option == "1":
        try:
            mp3_path = convert_to_mp3(video_path)
            message += "<br>Video berhasil dikonversi ke MP3: " + mp3_path
            file_to_download = mp3_path
        except Exception as e:
            message += "<br>Gagal mengonversi video ke MP3: " + str(e)
    
    # Berikan link untuk mengunduh file
    # Gunakan send_file dengan path file_to_download; di sini kita kembalikan link download
    # Misalnya, buat route /download_file/<filename>
    # Untuk kesederhanaan, kita pindahkan file ke folder DOWNLOAD_FOLDER dan kembalikan link
    filename = os.path.basename(file_to_download)
    return render_template_string(RESULT_HTML, message=message, file_url=url_for("download_file", filename=filename))

@app.route("/download_file/<filename>")
def download_file(filename):
    # Cari file di folder DOWNLOAD_FOLDER (bisa di folder VIDEO atau MP3)
    # Kita cari di seluruh folder downloads
    for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
        if filename in files:
            return send_file(os.path.join(root, filename), as_attachment=True)
    return "File tidak ditemukan.", 404

if __name__ == "__main__":
    app.run(debug=True)
