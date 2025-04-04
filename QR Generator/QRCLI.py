import os
import qrcode

def generate_qr(link, output_file="qr.jpg"):
    qr_folder = "qr"
    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)
    
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_L,  
        box_size=10,  
        border=4 
    )
    qr.add_data(link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    base_filename, ext = os.path.splitext(output_file)
    if ext.lower() not in [".jpg", ".jpeg"]:
        output_file = base_filename + ".jpg"
    
    output_path = os.path.join(qr_folder, output_file)
    img.save(output_path, format="JPEG")
    
    return qr, output_path

def print_qr_in_console(qr):
    """
    Cetak QR Code dalam bentuk ASCII di konsol.
    Menggunakan karakter '█' untuk modul hitam dan spasi untuk modul putih.
    """
    matrix = qr.get_matrix()  
    for row in matrix:
        line = ""
        for col in row:
            if col:
                line += "██"  
            else:
                line += "  "  
        print(line)

def main():
    link = input("Masukkan link untuk QR Code: ").strip()
    if not link:
        print("Link tidak boleh kosong!")
        return
    
    output_file = input("Masukkan nama file output (default: qr.jpg): ").strip()
    if not output_file:
        output_file = "qr.jpg"
    
    qr, path = generate_qr(link, output_file)
    print("QR Code berhasil dibuat dan disimpan di:", path)
    print("\nQR Code dalam bentuk ASCII:")
    print_qr_in_console(qr)

if __name__ == "__main__":
    main()
