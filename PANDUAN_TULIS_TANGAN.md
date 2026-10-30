# Lembar hitung manual SIMUTEH

Nama: M. Zidane Naufal Azzam
NIM: 2330511034
Kelas: 7A
SEED: 1034

Tuliskan rumus, substitusi, dan satuan. Gambarkan diagram batang histogram pada Bagian 3. Foto hasil tulisan yang terbaca dan masukkan sebagai lampiran laporan.

## Bagian 2. Pembentukan citra

Diketahui f = 4 mm, diameter bercak X = 5 mm, ukuran piksel sensor = 0,0014 mm.

**a. Jarak 300 mm**
x = fX/Z = (4 mm × 5 mm)/(300 mm) = 0,06667 mm.
Diameter pada sensor dalam piksel = 0,06667/0,0014 = 47,62 piksel.

**b. Jarak 600 mm**
x = (4 × 5)/600 = 0,03333 mm.
Diameter = 0,03333/0,0014 = 23,81 piksel. Jarak dua kali lipat membuat ukuran bayangan setengahnya.

**c. Jarak maksimum untuk minimal 10 piksel pada foto asli**
10 ≤ (4 × 5)/(Z × 0,0014), sehingga Z ≤ 1428,57 mm.

**d. Setelah lebar diperkecil menjadi 640 piksel**
Faktor skala = 640/4000 = 0,16.
Pada Z = 300 mm: 47,62 × 0,16 = 7,62 piksel.
Agar minimal 10 piksel: 10 ≤ [(4 × 5)/(Z × 0,0014)] × 0,16.
Jadi Z ≤ 228,57 mm. Nilai ini teoretis untuk model kamera soal.

**e. Memori tanpa kompresi**
Foto asli = 4000 × 3000 × 3 × 8 bit = 36.000.000 byte = 36 MB (desimal).
Citra berwarna = 640 × 480 × 3 = 921.600 byte = 0,9216 MB.
Citra keabuan = 640 × 480 × 1 = 307.200 byte = 0,3072 MB.
300 foto asli = 300 × 36.000.000 = 10.800.000.000 byte = 10,8 GB (desimal).

**f. Konversi keabuan dan Hue**
Y = 0,299R + 0,587G + 0,114B.
Bercak: Y = 0,299(196) + 0,587(178) + 0,114(86) = 172,894 ≈ 173.
Daun: Y = 0,299(52) + 0,587(136) + 0,114(60) = 102,22 ≈ 102.
Selisih sebelum pembulatan = 70,674; setelah pembulatan = 71 tingkat intensitas.
Pemeriksaan OpenCV: grayscale bercak = 173, daun = 102; Hue bercak = 25, daun = 63 pada rentang OpenCV 0–179.

## Bagian 3. Histogram dan operasi titik

Matriks awal M (4 × 4):
Baris 1: [1, 2, 2, 3]
Baris 2: [2, 2, 3, 3]
Baris 3: [1, 2, 3, 4]
Baris 4: [2, 3, 3, 2]

**a. Histogram M**
Untuk intensitas r = 0,1,2,3,4,5,6,7, jumlah piksel n = 0,2,7,6,1,0,0,0. Jumlah = 16. Gambar diagram batang dengan r pada sumbu mendatar dan n pada sumbu tegak.

**b. Peregangan kontras**
s = pembulatan[(r - 1)/(4 - 1) × 7]. Pemetaan: 1→0, 2→2, 3→5, 4→7.
Matriks hasil:
0 2 2 5
2 2 5 5
0 2 5 7
2 5 5 2

**c. Ekualisasi histogram**
Gunakan s = pembulatan(7 × CDF), sesuai rumus pada soal. PDF = n/16.

| r | n | PDF | CDF | 7 × CDF | s |
|---|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 2 | 0,125 | 0,125 | 0,875 | 1 |
| 2 | 7 | 0,4375 | 0,5625 | 3,9375 | 4 |
| 3 | 6 | 0,375 | 0,9375 | 6,5625 | 7 |
| 4 | 1 | 0,0625 | 1 | 7 | 7 |
| 5 | 0 | 0 | 1 | 7 | 7 |
| 6 | 0 | 0 | 1 | 7 | 7 |
| 7 | 0 | 0 | 1 | 7 | 7 |

Matriks hasil:
1 4 4 7
4 4 7 7
1 4 7 7
4 7 7 4

**d. Operasi titik 8 bit**
Negatif r = 60: s = 255 - 60 = 195.
Kontras r = 120: s = 1,4(120) - 30 = 138.
Kontras r = 210: s = 1,4(210) - 30 = 264, setelah clipping = 255.
Gamma r = 100: s = 255(r/255)^γ.
γ = 0,6: s = 255(100/255)^0,6 = 145,42 ≈ 145.
γ = 1,8: s = 255(100/255)^1,8 = 47,29 ≈ 47.

## Bagian 4. Konvolusi dan penapisan

Matriks awal P:
Baris 1: [52, 55, 61, 58]
Baris 2: [59, 255, 64, 60]
Baris 3: [62, 60, 0, 57]
Baris 4: [58, 61, 59, 63]

**a. Keluaran valid 2 × 2**
Untuk setiap posisi ambil jendela 3 × 3. Nilai rerata adalah jumlah sembilan angka dibagi 9, Gaussian adalah jumlah perkalian jendela dengan kernel dibagi 16, dan median adalah angka kelima setelah sembilan angka diurutkan.

Jumlah jendela secara berurutan kiri atas, kanan atas, kiri bawah, kanan bawah: 668, 670, 678, 679.
Contoh kiri atas rerata: (52+55+61+59+255+64+62+60+0)/9 = 668/9 = 74,22.
Contoh kiri atas Gaussian: (1×52+2×55+1×61+2×59+4×255+2×64+1×62+2×60+1×0)/16 = 1671/16 = 104,4375.
Contoh kiri atas median: urutkan [0,52,55,59,60,61,62,64,255]. Angka kelima = 60.
Rerata: baris atas [668/9; 670/9] = [74,22; 74,44], baris bawah [678/9; 679/9] = [75,33; 75,44].
Jumlah berbobot Gaussian untuk urutan posisi yang sama: 1671, 1238, 1236, 919.
Gaussian: baris atas [1671/16; 1238/16] = [104,4375; 77,375], baris bawah [1236/16; 919/16] = [77,25; 57,4375].
Median = [[60, 60], [60, 60]].

**b. Kernel tajam pada tengah Q**
s = 5(120) - 72 - 74 - 78 - 76 = 300. Setelah clipping ke 0–255, s = 255.

**c. Padding satu piksel untuk [12, 30, 45, 70]**
Zero: [0, 12, 30, 45, 70, 0]. Rerata piksel pertama = (0+12+30)/3 = 14.
Replicate: [12, 12, 30, 45, 70, 70]. Rerata = (12+12+30)/3 = 18.
Reflect_101: [30, 12, 30, 45, 70, 45]. Rerata = (30+12+30)/3 = 24.
