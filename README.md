
# 🐍 Python Simple App Collection ｜パイソンのシンプルなアプリ集 🎌

Welcome to my small collection of useful and fun **Python-based applications**. These apps are designed to run inside a virtual environment (`venv`) and can be compiled into `.exe` files for distribution.This is my practice material when learning python as a beginner programmer.

Whether you're a learner or just looking for a quick tool — ようこそ！✨

---

## 📦 Quick Setup ｜セットアップ方法

```bash
# ① Create a virtual environment
python -m venv .venv

# ② Activate the virtual environment
.\.venv\Scripts\ctivate

# ③ Install required dependencies
pip install -r requirements.txt

# 📝 Or install manually:
py -m pip install <package-name>
```

---

## 🏗️ Build to .EXE ｜.EXE ファイルに変換する方法

```bash
# ① Activate the virtual environment
.\.venv\Scripts\ctivate

# ② Install PyInstaller if not yet installed
pip install pyinstaller

# ③ Build your .py file to .exe
pyinstaller --noconfirm --onefile NAMA_FILE_KAMU.py
```

📁 The executable will be generated in the `dist/` folder.  
🔥 Great for sharing apps without requiring Python installation!

---

## 📌 Freeze Dependencies ｜依存関係を書き出す

```bash
# Inside venv:
pip freeze > requirements.txt
```

Then on another system, just:

```bash
pip install -r requirements.txt
```

📦 100% environment replication! 🧪

---

## 🚀 PyInstaller Tips ｜ビルドのコツ

- 🖥️ For terminal-based apps:
  ```bash
  pyinstaller --noconfirm --onefile --console your_app.py
  ```

- 🪟 For GUI-based apps (like Tkinter):
  ```bash
  pyinstaller --noconfirm --onefile --windowed your_app.py
  ```

---
---

## ✨ Final Notes ｜最後に…

- Keep your `requirements.txt` updated!
- Make `.exe` builds for easy sharing with non-developers
- Keep learning and improving — 応援しています！💪

---

## 🙏 Thank You ｜ありがとうございます！

> Made with ❤️ using **Python** by GENDHUT  
> 頑張ってください！🚀
