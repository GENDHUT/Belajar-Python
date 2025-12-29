papan = [" "] * 9
Pemain1 = "X"
Pemain2 = "O"
Pemain_sekarang = Pemain1

def tampilkan(papan):
    print(f" {papan[0]} | {papan[1]} | {papan[2]} ")
    print("-------------")
    print(f" {papan[3]} | {papan[4]} | {papan[5]} ")
    print("-------------")
    print(f" {papan[6]} | {papan[7]} | {papan[8]} ")

def cek_menang(papan, pemain):
    kombinasi_menang = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for combo in kombinasi_menang:
        if papan[combo[0]] == papan[combo[1]] == papan[combo[2]] == pemain:
            return True
    return False

while True:
    tampilkan(papan)
    print("Sekarang Giliran Pemain:", Pemain_sekarang)
    
    try:
        Posisi = int(input("Ketik Angka 1-9 :"))

        if Posisi < 1 or Posisi > 9:
            print("Masukkan angka 1 sampai 9 saja")
            continue

        if papan[Posisi - 1] != " ":
            print("Block sudah terisi")
            continue

        papan[Posisi - 1] = Pemain_sekarang


        if cek_menang(papan, Pemain_sekarang):
            tampilkan(papan)
            print(f"Pemain {Pemain_sekarang} MENANG! 🎉")
            ulang = input("Tekan R untuk main lagi, atau apapun untuk keluar: ").upper()
            if ulang == "R":
                papan = [" "] * 9
                Pemain_sekarang = Pemain1
                continue
            else:
                print("Terimakasih")
                break

        if " " not in papan:
            tampilkan(papan)
            print("Permainan SERI! 🤝")
            ulang = input("Tekan R untuk main lagi, atau apapun untuk keluar: ").upper()
            if ulang == "R":
                papan = [" "] * 9
                Pemain_sekarang = Pemain1
                continue
            else:
                print("Terimakasih")
                break

        # ganti pemain
        Pemain_sekarang = Pemain2 if Pemain_sekarang == Pemain1 else Pemain1

    except ValueError:
        print("Harus angka!")


# cara aplikasi bekerja
# 1.buat papan dulu
# 2.buat pemain bisa masukin ke 
# 3.logic game
# 4.cara ganti Pemain
# 5.looping 
# 6.menangin game nya


#  ini testing ---------------
# cara AI

# def tampilkan_papan(papan):
#     print("     |     |     ")
#     print(f"  {papan[0]}  |  {papan[1]}  |  {papan[2]}  ")
#     print("     |     |     ")
#     print("-----+-----+-----")
#     print("     |     |     ")
#     print(f"  {papan[3]}  |  {papan[4]}  |  {papan[5]}  ")
#     print("     |     |     ")
#     print("-----+-----+-----")
#     print("     |     |     ")
#     print(f"  {papan[6]}  |  {papan[7]}  |  {papan[8]}  ")
#     print("     |     |     ")

# tampilkan_papan(papan)


# cara 1
# print("",papan[0],"|","",papan[1],"|","",papan[2],"|",)
# print("-------------")
# print(papan[3],"|",papan[4],"|",papan[5],"|",)
# print("-------------")
# print(papan[6],"|",papan[7],"|",papan[8],"|",)


# print(papan) 


# cara akhir
# papan = [" "] * 9
# Pemain1 = "X"
# Pemain2 = "O"

# def tampilkan(papan) :
#     print(f" {papan[0]} | {papan[1]} | {papan[2]} ")
#     print("-------------")
#     print(f" {papan[3]} | {papan[4]} | {papan[5]} ")
#     print("-------------")
#     print(f" {papan[6]} | {papan[7]} | {papan[8]} ")

# tampilkan(papan)
# while True:
#     try:
#         Posisi = int(input("Ketik Angka 1-9 :"))

#         if Posisi < 1 or Posisi > 9:
#             print ("masukan angak 1 sampai 9 saja")
#             continue
#         if papan[Posisi - 1] != " ":
#             print("Block sudah ter isi")
#             continue
#         papan[Posisi - 1] = Pemain1
#         break

#     except ValueError:
#         print("Harus Angka")


# tampilkan(papan)


