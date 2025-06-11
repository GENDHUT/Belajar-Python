#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <limits>

#ifdef _WIN32
    #define CLEAR "cls"
#else
    #define CLEAR "clear"
#endif

using namespace std;

// Konstanta
const string PIN = "123456";
const int SALDO_MINIMAL = 50000;
const int NOMINAL_TUNAI = 50000;

// Struktur untuk mencatat transaksi
vector<string> riwayatTransaksi;

// Fungsi verifikasi PIN
bool verifikasiPIN() {
    string inputPin;

    for (int percobaan = 1; percobaan <= 3; ++percobaan) {
        cout << "Masukkan PIN Anda (6 digit) atau ketik 'batal' untuk keluar: ";
        cin >> inputPin;

        if (inputPin == "batal" || inputPin == "BATAL") {
            cout << "\nOperasi dibatalkan oleh pengguna.\n";
            return false;
        }

        if (inputPin == PIN) {
            cout << "PIN benar. Selamat datang!\n" << endl;
            return true;
        } else {
            cout << "PIN salah! Kesempatan tersisa: " << (3 - percobaan) << endl;
        }
    }

    cout << "\nAkses ditolak. Anda telah salah memasukkan PIN sebanyak 3 kali." << endl;
    return false;
}

// Fungsi untuk mencetak struk
void cetakStruk(const string &jenis, int jumlah, int saldo) {
    cout << "\n===== STRUK TRANSAKSI =====" << endl;
    cout << "Jenis Transaksi : " << jenis << endl;
    cout << "Jumlah          : Rp " << jumlah << endl;
    cout << "Saldo Saat Ini  : Rp " << saldo << endl;
    cout << "============================\n" << endl;

    // Simpan ke riwayat
    string struk = "Transaksi: " + jenis + " | Jumlah: Rp " + to_string(jumlah) + " | Saldo: Rp " + to_string(saldo);
    riwayatTransaksi.push_back(struk);

    system("pause");  // Tunggu user tekan tombol
}

// Fungsi tarik tunai
void tarikTunai(int &saldo) {
    int jumlah;
    cout << "\n--- Menu Tarik Tunai ---" << endl;
    cout << "Masukkan jumlah (kelipatan Rp 50.000), atau ketik 0 untuk batal: Rp ";
    cin >> jumlah;

    if (jumlah == 0) {
        cout << "🔁 Operasi penarikan dibatalkan.\n";
        system("pause");
        return;
    }

    if (jumlah <= 0) {
        cout << "❌ Jumlah tidak valid.\n";
    } else if (jumlah % NOMINAL_TUNAI != 0) {
        cout << "❌ Jumlah harus kelipatan Rp " << NOMINAL_TUNAI << ".\n";
    } else if (jumlah > saldo - SALDO_MINIMAL) {
        cout << "❌ Saldo tidak mencukupi setelah mempertahankan saldo minimal Rp " << SALDO_MINIMAL << ".\n";
        cout << "Saldo Anda saat ini: Rp " << saldo << endl;
    } else {
        saldo -= jumlah;
        cout << "✅ Penarikan berhasil.\n";
        cetakStruk("Tarik Tunai", jumlah, saldo);
        return;
    }

    system("pause");
}

// Fungsi setor tunai
void setorTunai(int &saldo) {
    int jumlah;
    cout << "\n--- Menu Setor Tunai ---" << endl;
    cout << "Masukkan jumlah yang ingin disetor, atau ketik 0 untuk batal: Rp ";
    cin >> jumlah;

    if (jumlah == 0) {
        cout << "🔁 Operasi setor dibatalkan.\n";
        system("pause");
        return;
    }

    if (jumlah <= 0) {
        cout << "❌ Jumlah tidak valid.\n";
    } else {
        saldo += jumlah;
        cout << "✅ Setor tunai berhasil.\n";
        cetakStruk("Setor Tunai", jumlah, saldo);
        return;
    }

    system("pause");
}

// Fungsi cek saldo
void cekSaldo(int saldo) {
    cout << "\n--- Menu Cek Saldo ---" << endl;
    cout << "Saldo Anda saat ini: Rp " << saldo << endl;
    cetakStruk("Cek Saldo", 0, saldo);
}

// Fungsi lihat riwayat transaksi
void lihatRiwayat() {
    int pilihan;

    do {
        cout << "\n--- Riwayat Transaksi ---" << endl;

        if (riwayatTransaksi.empty()) {
            cout << "Belum ada transaksi yang tercatat.\n";
        } else {
            for (size_t i = 0; i < riwayatTransaksi.size(); ++i) {
                cout << i + 1 << ". " << riwayatTransaksi[i] << endl;
            }
        }

        cout << "\n0. Kembali ke menu utama\n";
        cout << "Pilih angka 0 untuk kembali: ";
        cin >> pilihan;
    } while (pilihan != 0);
}

// Fungsi utama
int main() {
    if (!verifikasiPIN()) {
        return 0;
    }

    int saldo = 1000000;
    int pilihan;

    do {
        system(CLEAR);
        cout << fixed << setprecision(0);
        cout << "=========================================" << endl;
        cout << "     MESIN ATM BANK BINTANG GANTENG" << endl;
        cout << "=========================================" << endl;
        cout << "1. Tarik Tunai" << endl;
        cout << "2. Cek Saldo" << endl;
        cout << "3. Setor Tunai" << endl;
        cout << "4. Lihat Riwayat Transaksi" << endl;
        cout << "5. Keluar" << endl;
        cout << "-----------------------------------------" << endl;
        cout << "Pilih menu: ";
        cin >> pilihan;

        switch (pilihan) {
            case 1:
                tarikTunai(saldo);
                break;
            case 2:
                cekSaldo(saldo);
                break;
            case 3:
                setorTunai(saldo);
                break;
            case 4:
                lihatRiwayat();
                break;
            case 5:
                cout << "\n✅ Terima kasih telah menggunakan ATM BANK BINTANG GANTENG!\n" << endl;
                break;
            default:
                cout << "❌ Pilihan tidak valid. Silakan coba lagi.\n";
                system("pause");
        }

    } while (pilihan != 5);

    return 0;
}
