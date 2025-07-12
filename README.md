
# 🐍 Kumpulan Aplikasi Python Sederhana

Beberapa aplikasi sederhana yang saya buat menggunakan Python. Aplikasi-aplikasi ini bisa berjalan secara langsung melalui virtual environment (`venv`) dan bisa dikompilasi menjadi `.exe` agar mudah dibagikan ke orang lain.

---

## 📦 Langkah Awal (Setup Environment)

```bash
# 1. Buat virtual environment
python -m venv .venv

# 2. Aktifkan venv
.\.venv\Scripts\activate

# 3. Install semua dependensi
pip install -r requirements.txt
// atau bisa kalian install 1 per 1
py -m pip install


🏗️ Build ke File .EXE
# 1. Aktifkan venv
.\.venv\Scripts\activate

# 2. Install PyInstaller
pip install pyinstaller

# 3. Build .exe dari file Python
pyinstaller --noconfirm --onefile NAMA_FILE_KAMU.py
// lihat tips untuk lebih membantu


📌 Buat freeze requirements.txt
# 1. Aktifkan venv
.\.venv\Scripts\activate

# 2. buat daftar dependency
pip freeze > requirements.txt

🚀 Tips
# Gunakan --console jika ingin output terminal:
pyinstaller --noconfirm --onefile --console your_app.py


# Gunakan --windowed jika aplikasi menggunakan GUI:
pyinstaller --noconfirm --onefile --windowed your_app.py


    🔥 Written with **Python** by GENDHUT ❤️   


🙌 Terima Kasih!