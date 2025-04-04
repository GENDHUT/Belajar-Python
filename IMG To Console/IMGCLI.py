import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=80):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)  
    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = "".join(ASCII_CHARS[pixel * (len(ASCII_CHARS) - 1) // 255] for pixel in pixels)
    return ascii_str

def image_to_ascii(image_path, new_width=80):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print("Tidak dapat membuka gambar:", e)
        return None

    image = resize_image(image, new_width)
    image = grayify(image)

    ascii_str = pixels_to_ascii(image)
    ascii_img = "\n".join(ascii_str[i:i+new_width] for i in range(0, len(ascii_str), new_width))
    return ascii_img

def main():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Pilih Gambar",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        print("Tidak ada file yang dipilih!")
        return

    ascii_image = image_to_ascii(file_path)
    if ascii_image:
        print("QR Code dalam bentuk ASCII:")
        print(ascii_image)

if __name__ == "__main__":
    main()
