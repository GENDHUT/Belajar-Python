import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import threading
import time
import requests
import os
from urllib.parse import urljoin, urlparse
from queue import Queue


class WebScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper Sederhana")
        self.root.geometry("600x500")

        self.label = tk.Label(root, text="Masukkan URL:")
        self.label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.pack()

        self.start_button = tk.Button(root, text="Mulai Scraping", command=self.start_scraping_thread)
        self.start_button.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(root, width=70, height=20)
        self.output_area.pack(pady=10)

    def start_scraping_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "URL tidak boleh kosong!")
            return

        self.queue = Queue()
        thread = threading.Thread(target=self.scrape, args=(url,))
        thread.start()
        self.root.after(100, self.process_queue)

    def process_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                self.output_area.insert(tk.END, message)
        except self.queue.Empty:
            self.root.after(100, self.process_queue)

    def scrape(self, url):
        driver = None  # Inisialisasi driver di awal untuk menangani error lebih baik
        if not url.startswith("http"):
            url = "http://" + url

        self.queue.put(f"[INFO] Membuka browser ke: {url}\n")

        try:
            # Setup browser options
            options = webdriver.ChromeOptions()
            options.add_experimental_option("detach", True)
            options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Sesuaikan path browser

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)

            # Tunggu sampai body halaman dimuat
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            self.queue.put("[INFO] Halaman dimuat\n")

            # Scroll halaman
            self.queue.put("[INFO] Melakukan scroll halaman...\n")
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Ambil halaman dan parse dengan BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Judul halaman
            title = soup.title.string if soup.title else "Tidak ada title"
            self.queue.put(f"\n[Judul Halaman]: {title}\n")

            # Paragraf artikel
            self.queue.put("\n[Isi Artikel / Paragraf]:\n")
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    self.queue.put(f"- {text}\n")

            # Gambar
            self.queue.put("\n[Gambar Ditemukan & Diunduh]:\n")
            images = soup.find_all('img')

            # Buat folder image
            image_folder = "images"
            os.makedirs(image_folder, exist_ok=True)

            for idx, img in enumerate(images):
                src = img.get('src')
                if not src:
                    continue

                # Buat link absolut
                img_url = urljoin(url, src)

                # Ambil ekstensi file
                parsed = urlparse(img_url)
                file_ext = os.path.splitext(parsed.path)[-1]
                if not file_ext:
                    file_ext = ".jpg"

                filename = os.path.join(image_folder, f"image_{idx+1}{file_ext}")
                try:
                    r = requests.get(img_url, timeout=10)
                    if r.status_code == 200:
                        with open(filename, "wb") as f:
                            f.write(r.content)
                        self.queue.put(f"- {filename}\n")
                    else:
                        self.queue.put(f"- Gagal mengunduh {img_url}: Status Code {r.status_code}\n")
                except Exception as e:
                    self.queue.put(f"- Gagal mengunduh {img_url}: {e}\n")

            # Semua link
            self.queue.put("\n[Daftar Link]:\n")
            links = soup.find_all('a', href=True)
            for a_tag in links:
                self.queue.put(f"- {a_tag['href']}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")
            self.queue.put(f"Error: {e}\n")
        finally:
            if driver:
                driver.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
