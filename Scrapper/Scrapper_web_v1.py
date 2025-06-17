import tkinter as tk
from tkinter import messagebox, scrolledtext
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import threading
import os
from urllib.parse import urljoin, urlparse
import time


class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper Anti-403")
        self.root.geometry("750x650")

        self.label = tk.Label(root, text="Masukkan URL:")
        self.label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=80)
        self.url_entry.pack()

        self.start_button = tk.Button(root, text="Mulai Scraping", command=self.start_scraping_thread)
        self.start_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(root, width=95, height=30)
        self.output_area.pack(padx=10, pady=10)

    def start_scraping_thread(self):
        thread = threading.Thread(target=self.scrape)
        thread.start()

    def scrape(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            url = "http://" + url

        self.output_area.delete('1.0', tk.END)
        self.output_area.insert(tk.END, f"[INFO] Membuka halaman: {url}\n")

        try:
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")

            driver = uc.Chrome(options=options)
            driver.get(url)

            # Tunggu beberapa detik agar konten termuat (jika dinamis)
            time.sleep(3)

            # Scroll agar konten dinamis muncul
            self.output_area.insert(tk.END, "[INFO] Scrolling halaman...\n")
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            driver.quit()

            # Judul
            title = soup.title.string.strip() if soup.title else "Tidak ada title"
            self.output_area.insert(tk.END, f"\n[Judul Halaman]: {title}\n")

            # Paragraf
            self.output_area.insert(tk.END, "\n[Paragraf Teks]:\n")
            paragraphs = soup.find_all("p")
            if paragraphs:
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text:
                        self.output_area.insert(tk.END, f"- {text}\n")
            else:
                self.output_area.insert(tk.END, "Tidak ditemukan paragraf.\n")

            # Link
            self.output_area.insert(tk.END, "\n[Link Ditemukan]:\n")
            links = soup.find_all("a", href=True)
            if links:
                for a in links:
                    href = urljoin(url, a['href'])
                    self.output_area.insert(tk.END, f"- {href}\n")
            else:
                self.output_area.insert(tk.END, "Tidak ada link ditemukan.\n")

            # Gambar
            self.output_area.insert(tk.END, "\n[Download Gambar]:\n")
            os.makedirs("images", exist_ok=True)
            img_count = 0
            for i, img in enumerate(soup.find_all("img")):
                src = img.get("src")
                if not src:
                    continue
                img_url = urljoin(url, src)
                try:
                    ext = os.path.splitext(urlparse(img_url).path)[1] or ".jpg"
                    filename = f"images/image_{i+1}{ext}"
                    r = uc.requests.get(img_url, timeout=10)
                    with open(filename, "wb") as f:
                        f.write(r.content)
                    self.output_area.insert(tk.END, f"✓ {filename}\n")
                    img_count += 1
                except Exception as e:
                    self.output_area.insert(tk.END, f"✗ Gagal download: {img_url}\n")

            if img_count == 0:
                self.output_area.insert(tk.END, "Tidak ada gambar yang berhasil diunduh.\n")
            else:
                self.output_area.insert(tk.END, f"\n[INFO] Total gambar berhasil diunduh: {img_count}\n")

        except Exception as e:
            self.output_area.insert(tk.END, f"\n[ERROR] {e}\n")
            messagebox.showerror("Gagal", f"Gagal scraping halaman:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
