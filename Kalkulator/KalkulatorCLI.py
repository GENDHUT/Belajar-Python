def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        print("Error: Pembagian dengan nol tidak diperbolehkan!")
        return None
    return x / y

def main():
    while True:
        print("\n=== Kalkulator Sederhana ===")
        print("1. Tambah")
        print("2. Kurang")
        print("3. Kali")
        print("4. Bagi")
        print("5. Keluar")
        choice = input("Pilih operasi (1-5): ").strip()

        if choice == '5':
            print("Keluar dari program. Terima kasih!")
            break

        if choice not in ['1', '2', '3', '4']:
            print("Pilihan tidak valid. Silakan coba lagi.")
            continue

        try:
            num1 = float(input("Masukkan angka pertama: "))
            num2 = float(input("Masukkan angka kedua: "))
        except ValueError:
            print("Input tidak valid. Harap masukkan angka!")
            continue

        if choice == '1':
            result = add(num1, num2)
            operator = '+'
        elif choice == '2':
            result = subtract(num1, num2)
            operator = '-'
        elif choice == '3':
            result = multiply(num1, num2)
            operator = '*'
        elif choice == '4':
            result = divide(num1, num2)
            operator = '/'
        
        if result is not None:
            print(f"Hasil: {num1} {operator} {num2} = {result}")

if __name__ == "__main__":
    main()
