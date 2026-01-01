import random

score = 0

while True :
    user_input = input("Tebak Angka 1-10: ").strip()
    if user_input == "":
        print("masukan Angka 1-10")
        continue
    try:
        User = int(user_input)
    except ValueError:
        print("Masukan Angka Saja")
        continue
    if User < 1 or User > 10:
        print("Masukan Angka 1-10")
        continue
    komputer = random.randint(1,10)
    print("Komputer Memilih: ", komputer)
    if User == komputer:
        print("Kamu Benar")
        score += 1

    else:
        print("Kamu Salah")
    Keluar = input("Tekan K untuk keluar, tekan Enter untuk lanjut: ").strip().upper()
    if Keluar == "K":
        print("Terimakasih sudah bermain!")
        break

                    
print("score menang kamu", score)
