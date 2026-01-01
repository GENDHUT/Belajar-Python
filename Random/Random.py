import random
angka = random.random()
Tangan = ["Batu", "Gunting", "Kertas"]
pilihan = random.choice(Tangan)
score = 0

while True:
    User_input = input("1=Batu, 2=Gunting, 3=Kertas: ").strip()
    
    if User_input == "":
        print("Masukkan angka 1-3!")
        continue

    try:
        User = int(User_input)
    except ValueError:
        print("Masukkan angka saja!")
        continue

    if User < 1 or User > 3:
        print("Masukkan angka 1-3!")
        continue

    Komputer = random.randint(1, 3)

    print("Kamu Memilih:", Tangan[User - 1])
    print("Komputer Memilih:", Tangan[Komputer - 1])

    if User == Komputer:
        print("Seri")
    elif (User == 1 and Komputer == 2) or \
         (User == 2 and Komputer == 3) or \
         (User == 3 and Komputer == 1):
        print("Kamu Menang ")
        score += 1
    else:
        print("Kamu Kalah ")
    # ulang = input("Tekan R untuk ulang:").strip().upper()
    # if ulang != "R" :
    # print("Terimakasih")
    Keluar = input("Tekan K untuk keluar, tekan Enter untuk lanjut: ").strip().upper()
    if Keluar == "K":
        print("Terimakasih sudah bermain!")
        break

                    
print("score menang kamu", score)
               