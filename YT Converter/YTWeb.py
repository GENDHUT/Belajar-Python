from flask import Flask, render_template_string, request, send_file, redirect, url_for
from pytube import YouTube
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

HTML_TEMPLATE = '''
<!doctype html>
<title>YT Video Downloader</title>
<h1>Download Video YouTube</h1>
<form method="POST" action="/download">
    <label>Masukkan URL Video YouTube:</label>
    <input type="text" name="url" size="50">
    <input type="submit" value="Download">
</form>
'''

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return redirect(url_for("index"))
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        file_path = stream.download(output_path=DOWNLOAD_FOLDER)
        # Mengirim file yang telah diunduh sebagai attachment
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

if __name__ == "__main__":
    app.run(debug=True)
