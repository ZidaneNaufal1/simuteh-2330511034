# SIMUTEH - Evaluasi Praktikum P1-P4

Nama: M. Zidane Naufal Azzam  
NIM: 2330511034  
Kelas: 7A  
SEED dataset: 1034 (empat digit terakhir NIM)

Repository: https://github.com/ZidaneNaufal1/simuteh-2330511034

## Cara menjalankan

Gunakan Python 3.12. Dari folder utama proyek jalankan:

```text
python -m pip install -r requirements.txt
python src/buat_dataset_sintetis.py
python -m jupyterlab
```

Buka folder notebook/, jalankan B1 sampai B5 berurutan dengan Restart Kernel & Run All. Notebook harus tetap berada dalam folder notebook/ karena memakai jalur relatif. B2 menyiapkan grafik dan bukti pelengkap. B3 dan B4 menjalankan modul histogram/penapis yang sama agar bukti tersedia.

Alternatif tanpa antarmuka notebook:

```text
python src/eksperimen_awal.py
python src/eksperimen_penapis.py
python src/gambar_hasil.py
python src/lengkapi_hasil.py
```

Kelima notebook telah berhasil diuji dari awal sampai akhir dengan kernel baru melalui nbclient. Dataset dibangkitkan dari kode Lampiran A. SHA-256 seluruh 241 berkas hasil pembangkitan ulang cocok. Dataset tidak disertakan ZIP dan dapat dibuat ulang menggunakan SEED 1034.

## Ringkasan hasil

Kanal R memberi KB rata-rata tertinggi kelas berat pada lima kondisi. Praproses: lebar 640, gamma 1,0, CLAHE V clip 2,0 tile 8, median 3, tanpa penajaman. KB naik pada empat kondisi dan turun 18,53% pada terang. Simpangan baku area daun sehat pada terang naik 14,07%. Waktu pengukuran dapat berubah antar-eksekusi. Hasil sintetis belum membuktikan kemampuan diagnosis nyata atau akurasi klasifikasi.

## Bantuan AI dan pengumpulan

AI membantu secara luas pada implementasi, percobaan, pemeriksaan hitungan dan penyusunan laporan; hal ini diungkapkan dalam refleksi. Pemilik tugas wajib memahami dan memverifikasi hasil serta memastikan cakupan bantuan sesuai izin dosen.

Foto lembar hitung manual Bagian 2, 3 dan 4 belum dilampirkan. Gunakan panduan PDF untuk menulis lalu tambahkan foto tulisan ke laporan. PPTX tidak dibuat sesuai permintaan pemilik tugas, tetapi tetap diwajibkan dosen. Repository pribadi perlu memberi dosen akses kolaborator sesuai arahan kelas. LMS belum dikirim.

Tag rilis: v0.1-praproses.
