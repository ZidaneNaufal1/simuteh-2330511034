"""Menyusun PDF laporan dari CSV dan gambar hasil eksekusi, bukan angka rekaan."""
from pathlib import Path
import csv, statistics, sys
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY,TA_CENTER
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path.cwd(); H=ROOT/'hasil'; OUT=ROOT/'laporan'; OUT.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
ss=getSampleStyleSheet(); ss.add(ParagraphStyle(name='BodyA',fontName='Arial',fontSize=11,leading=16.5,alignment=TA_JUSTIFY,spaceAfter=7))
ss.add(ParagraphStyle(name='HeadA',fontName='Arial-Bold',fontSize=15,leading=19,spaceAfter=10))
ss.add(ParagraphStyle(name='SmallA',fontName='Arial',fontSize=11,leading=16.5,spaceAfter=5))
ss.add(ParagraphStyle(name='CapA',fontName='Arial',fontSize=11,leading=16.5,spaceAfter=8,alignment=TA_CENTER))
story=[]; tn=0; gn=0; table_padding=3
def p(t): story.append(Paragraph(t,ss['BodyA']))
def head(t): story.append(Paragraph(t,ss['HeadA']))
def page(t):
    if story: story.append(PageBreak())
    head(t)
def rows(name): return list(csv.DictReader(open(H/name,encoding='utf8')))
def table(title,data,widths=None):
    global tn
    tn+=1; story.append(Paragraph(f'Tabel {tn}. '+title,ss['SmallA']))
    data=[[Paragraph(escape(str(v)),ss['SmallA']) for v in r] for r in data]
    t=Table(data,colWidths=widths or [495/len(data[0])]*len(data[0]),repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0eb')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.lightgrey),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),table_padding),('BOTTOMPADDING',(0,0),(-1,-1),table_padding)]));story.append(t);story.append(Spacer(1,7))
def csvtable(name,title,keys=None):
    rr=rows(name); keys=keys or list(rr[0]); table(title,[keys]+[[r[k] for k in keys] for r in rr])
def fig(name,title,width=465,maxh=245):
    global gn
    gn+=1; im=Image(str(H/name)); scale=min(width/im.imageWidth,maxh/im.imageHeight); im.drawWidth=im.imageWidth*scale; im.drawHeight=im.imageHeight*scale
    story.append(KeepTogether([im,Paragraph(f'Gambar {gn}. '+title,ss['CapA'])]))
def q(code,text):
    refs={'P1':'Tabel 1; Gambar 1 dan 3','P2':'Tabel 4-6 dan 16-17; Gambar 4-6','P3':'Tabel 7-9 dan 18-20; Gambar 7-9','P4':'Tabel 10-12 dan 21-22; Gambar 10-12','P5':'Tabel 13-15; Gambar 13-15'}
    if code=='P1.4':
        text+=' Salah penilaian sehat menjadi berat dapat menguntungkan pembeli secara sesaat bila harga turun. Kesalahan berat menjadi sehat dapat menguntungkan penjual secara sesaat bila harga naik, tetapi berisiko merusak kepercayaan dan mutu rantai pasok.'
    p('<b>'+code+'.</b> '+text+' [Rujukan: '+refs[code.split('.')[0]]+'.]')
def footer(c,doc):
    c.setFont('Arial',8); c.drawString(50,28,'SIMUTEH | 2330511034 | SEED 1034'); c.drawRightString(545,28,str(doc.page))

page('LAPORAN EVALUASI PRAKTIKUM P1-P4')
story.append(Spacer(1,65)); head('SIMUTEH: Akuisisi dan Praproses Citra Daun Teh')
p('Mata kuliah: Computer Vision<br/>Nama: M. Zidane Naufal Azzam<br/>NIM: 2330511034<br/>Kelas: 7A<br/>SEED: 1034<br/>Tanggal penyusunan: 30 Oktober 2026')
p('Repository GitHub: <link href="https://github.com/ZidaneNaufal1/simuteh-2330511034">https://github.com/ZidaneNaufal1/simuteh-2330511034</link><br/>Tag rilis: v0.1-praproses.')
p('Ruang lingkup laporan: lingkungan kerja, pembentukan citra dan ruang warna, histogram, penapisan spasial, serta integrasi praproses. Lampiran tulisan tangan disiapkan terpisah dan perlu dimasukkan setelah difoto.')
page('1. Pendahuluan dan formulasi masalah')
p('SIMUTEH merupakan studi kasus alat bantu penyortiran daun teh. Petugas membutuhkan penilaian yang lebih konsisten ketika bercak kecil sulit terlihat atau pencahayaan berubah. Evaluasi ini menyiapkan akuisisi dan praproses untuk pengembangan segmentasi serta klasifikasi pada pertemuan berikutnya.')
p('<b>Problem statement.</b> Bagi petugas sortir daun teh yang menghadapi penilaian bercak yang tidak seragam, SIMUTEH menerima foto daun di atas nampan dan kelak menghasilkan kelas mutu serta persentase luas bercak, sehingga petugas memperoleh pertimbangan yang dapat ditelusuri. Keputusan akhir tetap pada petugas.')
fig('b1_pipeline.png','Pipeline enam tahap. Evaluasi P1-P4 berfokus pada akuisisi dan praproses.',maxh=220)
table('Risiko responsible computer vision',[['Aspek','Risiko','Mitigasi'],['Privasi','Wajah dan GPS terekam','Cegah wajah, hapus EXIF sebelum unggah'],['Bias dan keadilan','Data sintetis tidak mewakili kebun','Uji foto nyata lintas kondisi dan varietas'],['Transparansi','Kelas dianggap diagnosis pasti','Jelaskan keterbatasan dan tampilkan bukti'],['Keamanan data','Foto diakses tanpa izin','Batasi akses dan simpan cadangan'],['Dampak sosial','Salah mutu merugikan petani','Petugas memeriksa hasil dan bisa mengoreksi'],['Keterlacakan','Parameter dan hasil tertukar','Simpan SEED, CSV, versi, commit dan tag']],[80,170,215])
page('2. Data dan lingkungan kerja')
p('Dataset bawaan dibangkitkan dari Lampiran A dengan SEED 1034: 60 citra berukuran 640 × 480, masing-masing 20 sehat, ringan, dan berat. Tiap kondisi normal, gelap, terang, kontras rendah, dan bayangan memiliki 12 citra. Mask acuan dipakai untuk evaluasi, bukan sebagai masukan yang tersedia pada pemakaian lapangan.')
labels=list(csv.DictReader(open(ROOT/'data/sintetis/label.csv')))
table('Ringkasan luas bercak dari label.csv',[['Kelas','n','Rerata (%)','Minimum (%)','Maksimum (%)']]+[[k,20,round(statistics.mean(float(r['persen_bercak']) for r in labels if r['kelas']==k),3),min(float(r['persen_bercak']) for r in labels if r['kelas']==k),max(float(r['persen_bercak']) for r in labels if r['kelas']==k)] for k in ['sehat','ringan','berat']])
# Versi lingkungan eksperimen 30 Oktober 2026; regenerasi dokumen tidak mengubah catatan eksperimen.
table('Versi pustaka pada eksekusi',[['Pustaka','Versi'],['Python','3.12.14'],['OpenCV','4.12.0'],['NumPy','2.2.6'],['Matplotlib','3.10.8'],['scikit-image','0.26.0'],['pandas','3.0.1'],['Pillow','13.0.0']])
fig('contoh_kondisi_dan_sehat.png','Lima kondisi kelas berat (atas) dan contoh hasil kelas sehat (bawah).',maxh=210)
page('3. Hasil dan analisis Bagian 1')
p('Uji teh_041.png menghasilkan shape (480, 640, 3), dtype uint8, rentang intensitas 11 sampai 255, dan piksel pada y=100, x=200 dalam BGR [156, 194, 220]. Dataset telah dibangkitkan ulang: seluruh 241 berkas cocok secara SHA-256 dengan hasil pertama.')
fig('b1_bgr_rgb.png','Perbandingan tampilan sebelum dan sesudah konversi BGR ke RGB.',maxh=200)
q('P1.1','Petugas memahami daun, bercak, dan tingkat keparahan, sedangkan komputer menerima larik angka. Contohnya [156,194,220] menyatakan intensitas BGR pada satu lokasi, bukan makna "penyakit". Menghubungkan angka dengan konsep mutu merupakan semantic gap.')
q('P1.2','Pencahayaan perlu ditangani pada akuisisi dan praproses; perubahan skala ditangani dengan jarak serta resolusi akuisisi; derau dan latar ditangani melalui penapisan dan segmentasi. Pipeline pada Gambar 1 menunjukkan posisi penanganannya.')
q('P1.3','OpenCV membaca BGR, sedangkan Matplotlib menganggap kanal pertama R. Tanpa konversi, kanal merah dan biru tertukar seperti pada Gambar 3. Fitur warna P9 akan salah makna jika urutan kanal tidak konsisten.')
q('P1.4','Sehat yang dinilai berat dapat menurunkan harga dan merugikan petani; bercak berat yang dinilai sehat dapat merugikan pembeli dan mutu produk. Penilaian yang adil mengukur kedua jenis kesalahan. Amanah berarti menyampaikan keterbatasan dan menjaga pemeriksaan manusia.')
page('4. Bagian 2: syarat akuisisi dan ruang warna')
p('Model kamera menghasilkan diameter bercak 47,62 piksel pada jarak 300 mm dan 23,81 piksel pada 600 mm. Setelah foto asli diperkecil dari lebar 4000 ke 640, bercak pada jarak 300 mm tinggal 7,62 piksel. Batas teoretis jarak untuk 10 piksel setelah pengecilan adalah 228,57 mm. Hitungan lengkap disediakan dalam Lembar_Hitung_Manual_2330511034.pdf.')
table('Rencana akuisisi',[['Komponen','Rencana'],['Jarak dan sudut','Sekitar 200 mm, kamera tegak lurus; periksa fokus dan seluruh daun masuk bingkai'],['Resolusi','Pada 300 mm diperlukan lebar kerja minimal 840 piksel. Untuk kerja lebar 640, gunakan jarak ≤228,57 mm sesuai model soal'],['Alas dan skala','Alas polos tidak mengilap dan penggaris pada bidang daun'],['Cahaya','Wakili normal, gelap, terang, kontras rendah, bayangan; hindari clipping'],['Jumlah awal nyata','Usulan 20 citra per kelas, seimbang antar kondisi; perlu diperluas sebelum model lapangan'],['Nama berkas','teh_ID_kelas_kondisi.png, tanpa nama atau identitas petani'],['Persetujuan','Minta izin pemotretan serta publikasi; cegah wajah dan hapus EXIF termasuk GPS']],[95,370])
fig('b2_kanal.png','Citra berat normal dan tujuh kanal pembanding.',maxh=230)
page('5. Bagian 2: hasil perbandingan kanal')
rr=rows('b2_kb_kanal.csv'); table('Rerata KB kelas berat per kondisi',[['Kondisi','B','G','R','Gray','H','S','V']]+[[r['kondisi']]+[round(float(r[k]),2) for k in ['B','G','R','Gray','H','S','V']] for r in rr if r['kelas']=='berat'])
table('Rerata KB kelas ringan per kondisi',[['Kondisi','B','G','R','Gray','H','S','V']]+[[r['kondisi']]+[round(float(r[k]),2) for k in ['B','G','R','Gray','H','S','V']] for r in rr if r['kelas']=='ringan'])
fig('b2_kb_kanal.png','Perbandingan KB kelas berat pada seluruh kondisi.',maxh=260)
page('6. Bagian 2: sampling, kuantisasi, dan analisis')
fig('b2_sampling_kuantisasi.png','Sampling (atas) dan kuantisasi (bawah) pada teh_041.',maxh=210)
q('P2.1','Aturan untuk petugas: foto tegak lurus sekitar 20 cm, gunakan fokus yang jelas dan seluruh daun masuk bingkai, lalu periksa bercak terkecil tetap sedikitnya 10 piksel pada ukuran kerja. Dasar batas jarak ada pada Bagian 4 laporan.')
q('P2.2','Kanal R memberi KB tertinggi pada kelima kondisi kelas berat, sebagaimana tabel perbandingan kanal. Bercak pucat memiliki komponen merah lebih tinggi daripada daun hijau. Keunggulan ini tetap perlu diperiksa pada daun nyata dan kelas ringan, bukan dianggap universal.')
q('P2.3','H mengungguli V pada gelap (5,54 vs 3,10), terang (7,45 vs 2,08), dan bayangan (4,55 vs 1,35), tetapi KB H berubah antarkondisi. Hue relatif memisahkan warna; derau, saturasi rendah, dan kuantisasi tetap memengaruhinya. Ketahanan bukan invariansi mutlak.')
q('P2.4','KB tinggi pada bit kecil tidak menjamin informasi terjaga. Kuantisasi dapat mengecilkan simpangan baku daun sehat sehingga pembagi KB turun, sekaligus membuang gradasi. Panel sampling dan kuantisasi serta CSV menunjukkan 3 bit menghasilkan KB 4,655, tetapi hanya lima level terpakai.')
q('P2.5','Pada panel, detail bercak semakin tidak jelas ketika faktor menjadi 0,1 dan terutama 0,05. CSV menunjukkan KB turun menjadi 3,087 dan 1,421. Ambang visual bergantung ukuran bercak. Perhitungan 7,62 piksel pada lebar 640 memperlihatkan perlunya mengendalikan resolusi sebelum pemrosesan.')
q('P2.6','EXIF dapat mengungkap koordinat GPS, waktu, dan perangkat. Petani atau pemilik kebun dapat dirugikan oleh terbukanya lokasi. Rencana akuisisi mewajibkan izin, menghapus metadata, memeriksa berkas keluaran, dan mencegah wajah masuk bingkai.')
page('7. Bagian 3: diagnosis dan perbaikan')
csvtable('b3_diagnosis.csv','Statistik citra kelas berat dan ringan')
p('Citra gelap cenderung bergeser ke intensitas rendah, terang ke tinggi, kontras rendah memadat pada rentang lebih sempit, sedangkan bayangan membuat distribusi dipengaruhi posisi. Statistik seluruh citra juga mencakup latar, sehingga diagnosis perlu dibandingkan dengan panel visual.')
fig('b3_histogram_5kondisi.png','Histogram lima kondisi kelas berat.',maxh=210)
page('8. Bagian 3: perbandingan metode')
csvtable('b3_perbaikan.csv','Perbaikan grayscale teh_045 (bayangan)')
fig('b3_metode_histogram.png','Citra dan histogram sembilan metode pada kondisi bayangan.',maxh=150)
p('Hasil aktual berbeda dari asumsi pertanyaan P3.2: CLAHE grayscale juga menurunkan KB dari 2,862 menjadi 2,551, sementara ekualisasi global menghasilkan 2,035. Gamma 1,8 memberi KB 3,654. Kenaikan KB tetap perlu dibandingkan dengan detail visual dan risiko penggelapan.')
csvtable('b3_pilihan_kondisi.csv','Pilihan perbaikan untuk empat kondisi, kelas ringan dan berat')
page('9. Analisis Bagian 3')
q('P3.1','Dengan s=round(7 CDF), nilai 3 dan 4 sama-sama dipetakan menjadi 7. Kedua intensitas tidak dapat dibedakan lagi dari hasilnya. Ekualisasi mendistribusikan ulang intensitas yang sudah ada, bukan menciptakan informasi baru.')
q('P3.2','Ekualisasi global menggunakan satu pemetaan histogram untuk bagian terang dan teduh sehingga tidak mengatasi perbedaan lokal secara khusus. CLAHE membatasi penguatan lokal, tetapi data pada tabel perbaikan menunjukkan CLAHE tetap menurunkan KB. Oleh karena itu klaim "CLAHE tidak menurunkan KB" tidak didukung pada contoh ini.')
q('P3.3','Piksel ekstrem akibat derau dapat membuat min-maks tidak mewakili rentang utama. Misalnya mayoritas piksel berada di 100-120 tetapi ada 0 dan 255; peregangan min-maks hampir tidak memperluas rentang utama. Persentil 2-98 mengabaikan ekstrem tersebut, dengan risiko memotong detail yang sah.')
q('P3.4','CLAHE tiap kanal BGR menggunakan tiga pemetaan berbeda sehingga rasio warna dan hue dapat bergeser. Pada panel CLAHE warna, hasil BGR perlu dibandingkan dengan V yang mempertahankan H dan S sebelum konversi kembali. Pembulatan dan clipping tetap dapat menimbulkan perubahan warna kecil pada pendekatan V.')
q('P3.5','Satu pengaturan tidak cukup untuk seluruh kondisi: evaluasi integrasi menunjukkan KB turun pada kondisi terang. Aturan usulan adalah gamma <1 ketika rerata area daun rendah, gamma >1 ketika tinggi, dan mengecilkan clipLimit bila simpangan baku tinggi. Ambang harus divalidasi dan area daun di lapangan harus diperkirakan tanpa mask acuan.')
q('P3.6','CLAHE atau penajaman kuat dapat memperbesar derau sehingga tampak sebagai bercak. Pencegahannya adalah membatasi parameter, memeriksa kelas sehat, membandingkan citra asli, dan melaporkan kegagalan. Uji kelas sehat integrasi menunjukkan simpangan baku kondisi terang meningkat 14,07%.')
fig('b3_clahe_warna.png','Perbandingan CLAHE V dengan pemetaan terpisah BGR.',maxh=180)
page('10. Bagian 4: perbandingan penapis')
rr=rows('b4_tabel_penapis.csv'); table('PSNR, waktu dan KB pada dua derau utama',[['Derau','Penapis','PSNR dB','ms','KB']]+[[r[k] for k in ['derau','penapis','PSNR_dB','waktu_ms','KB']] for r in rr if r['derau'] in ['gauss_20','sp_4%']])
fig('b4_psnr.png','PSNR Gaussian 20 dan garam-merica 4%.',maxh=175)
p('Waktu merupakan pengukuran pada lingkungan eksekusi ini, bukan hasil benchmark telepon genggam. Pengukuran sangat singkat dipengaruhi penjadwalan dan pemanasan pustaka. Angka lengkap lima derau terdapat pada CSV dan notebook.')
page('11. Bagian 4: detail kecil dan urutan operasi')
fig('b4_di.png','Pengaruh ukuran kernel median terhadap rerata dI kelas ringan.',maxh=180)
fig('b4_crop_bercak.png','Pembesaran bercak ringan: kernel besar mengurangi detail.',maxh=160)
csvtable('b4_konvolusi.csv','Korelasi manual, konvolusi sejati dan filter2D')
csvtable('b4_urutan.csv','Urutan penajaman dan peredaman derau')
page('12. Analisis Bagian 4')
q('P4.1','Median keempat jendela adalah 60 karena nilai tengah tetap berada pada kelompok intensitas daun meskipun terdapat 0 dan 255. Rerata dan Gaussian menjumlahkan intensitas sehingga nilai ekstrem memengaruhi hasilnya. Ini menjelaskan efektivitas median terhadap derau impuls.')
q('P4.2','filter2D melakukan korelasi, sama dengan fungsi manual yang tidak membalik kernel. Konvolusi sejati membalik kernel 180 derajat. Kernel simetris tetap sama setelah dibalik, sedangkan kernel asimetris dapat membalik respons. Tabel konvolusi menunjukkan beda 0 untuk korelasi dan beda maksimum 255 untuk kernel asimetris sejati setelah clipping.')
q('P4.3','Pada Gaussian 20, median 9 memberi PSNR tertinggi di antara enam penapis yang dicoba. Pada garam-merica 4%, median 3 unggul PSNR. Namun median 9 jauh lebih lambat dan menghapus detail kecil; median 3 menjadi kompromi konservatif pada modul akhir. Pilihan ini tidak berarti selalu terbaik untuk semua derau.')
q('P4.4','Grafik dI dan crop menunjukkan pengurangan detail makin kuat pada kernel 9 dan 15. Tidak ada satu batas universal karena bercak memiliki ukuran beragam. KB dapat tetap tinggi ketika pembilang dI turun apabila simpangan baku daun sehat turun lebih cepat. Karena itu keputusan memakai dI, KB, dan inspeksi crop bersama.')
q('P4.5','Gaussian dan unsharp adalah operasi linear dalam ideal float tanpa clipping, sehingga dapat hampir komutatif dengan penanganan batas yang sesuai. Implementasi uint8 melakukan pembulatan dan clipping sehingga tidak identik. Median nonlinear, sehingga urutan dapat lebih berpengaruh. Tabel urutan menunjukkan hasil aktual, bukan jaminan urutan selalu unggul.')
q('P4.6','Perkalian kernel 5×5 sekitar 4000×3000×25 = 300.000.000 per kanal, sedangkan 640×480×25 = 7.680.000, berkurang sekitar 39,06 kali. Untuk tiga kanal jumlahnya tiga kali lipat. Tabel waktu manual vs pustaka mendukung penggunaan operasi teroptimasi untuk perangkat menengah.')
q('P4.7','Blur ringan menyisakan bentuk dan ciri identitas sehingga tidak memberi jaminan anonimisasi. Prosedur yang lebih aman adalah menolak foto berwajah, mengambil ulang atau memotong seluruh area wajah, memeriksa hasil secara visual, menghapus EXIF, lalu hanya membagikan berkas yang sudah diperiksa.')
page('13. Bagian 5: rangkaian akhir')
fig('b5_pipeline.png','Urutan dan parameter praproses akhir.',maxh=95)
rr=rows('b5_integrasi_ringkasan.csv'); table('KB kanal R, rerata 40 citra berbercak',[['Kondisi','Sebelum','Sesudah','Perubahan %']]+[[r[k] for k in ['kondisi','sebelum','sesudah','perubahan_persen']] for r in rr if r['kelompok']=='berbercak'])
fig('b5_kb.png','KB sebelum dan sesudah praproses.',maxh=150)
table('Justifikasi parameter',[['Langkah','Parameter dan alasan','Risiko'],['Ubah ukuran','Lebar 640, sesuai dataset dan biaya komputasi','Bercak hilang bila resolusi awal kurang'],['Gamma','1,0: tidak memakai koreksi global tetap','Kondisi ekstrem belum dikoreksi khusus'],['CLAHE V','clip 2,0; tile 8, koreksi lokal terbatas','Pada terang KB turun'],['Redam derau','Median 3 menjaga detail dibanding kernel besar','Derau Gaussian belum optimal'],['Tajamkan','k=0, tidak menguatkan derau','Tepi kurang tajam; perlu uji P5']],[75,250,140])
page('14. Uji kelas sehat dan analisis integrasi')
table('Simpangan baku R pada area daun sehat, 20 citra',[['Kondisi','Sebelum','Sesudah','Perubahan %']]+[[r[k] for k in ['kondisi','sebelum','sesudah','perubahan_persen']] for r in rr if r['kelompok']=='sehat'])
fig('b5_sehat.png','Citra sehat sebelum dan sesudah pada lima kondisi.',maxh=200)
q('P5.1','KB meningkat pada normal, gelap, kontras rendah, dan bayangan, tetapi turun 18,53% pada terang. KB akhir terendah terjadi pada kontras rendah (5,063). Intensitas bercak dan daun telah saling mendekat dan gangguan tidak sepenuhnya dapat dipulihkan.')
q('P5.2','Pada terang, transformasi V memodifikasi distribusi intensitas dan dapat menguatkan variasi daun sehat, sehingga rasio pemisahan turun. Perbaikan yang perlu diuji adalah melewati atau melemahkan CLAHE pada foto terang serta memilih gamma adaptif. Ini usulan lanjutan, belum diklaim tervalidasi.')
q('P5.3','Simpangan baku kondisi terang meningkat 14,07%, sementara empat kondisi lain turun. Kondisi terang menjadi risiko utama bercak palsu. Simpangan baku bukan ukuran false-positive klasifikasi; validasi segmentasi dan klasifikasi P11 masih diperlukan.')
page('15. Kesimpulan, refleksi, dan rencana P5')
q('P5.4','Transformasi dan parameter yang sama perlu diterapkan pada latih dan uji agar distribusi fitur konsisten. Jika berbeda, model dapat mempelajari karakter praproses alih-alih bercak. Pemilihan parameter berdasarkan seluruh data saat ini bersifat eksplorasi, bukan pengukuran akurasi generalisasi. Evaluasi P11 memerlukan pemisahan data dan pengaturan dari data latih saja.')
q('P5.5','Amanah diterapkan dengan menjaga SEED, mask acuan, dan keterlacakan hasil. Jujur diterapkan dengan melaporkan penurunan KB pada terang serta mengungkap penggunaan AI, bukan hanya menampilkan hasil yang meningkat. Implementasi perlu dipahami dan diverifikasi pemilik tugas sebelum pengumpulan.')
p('<b>Kesimpulan.</b> Kanal R paling konsisten pada lima kondisi dataset kelas berat. Pengaturan akhir meningkatkan KB pada empat kondisi tetapi gagal mempertahankannya pada terang. Kernel median kecil menjadi kompromi menjaga bercak dan meredam derau. Hasil sintetis belum menunjukkan kemampuan diagnosis atau klasifikasi nyata.')
p('<b>Rencana P5.</b> Memeriksa gradien pada kanal R hasil praproses; membandingkan tepi bercak dengan tulang daun; menguji pengaturan lebih lemah pada terang; mengukur pengaruh parameter terhadap mask prediksi setelah segmentasi tersedia.')
p('<b>Refleksi penggunaan AI.</b> AI membantu penyusunan kode, pelaksanaan percobaan, pemeriksaan hitungan, dan draf penjelasan. Angka diperoleh dengan menjalankan kode pada dataset SEED 1034. Penulis bertanggung jawab memeriksa hasil, memahami kode dan analisis, serta memastikan penggunaan bantuan sesuai izin dosen.')
p('<b>Responsible computer vision dan AIK.</b> Data nyata memerlukan persetujuan, perlindungan identitas dan lokasi, serta keterwakilan kondisi lapangan. Penilaian akhir tetap pada petugas. Keterbukaan hasil yang gagal dan batas penggunaan merupakan bentuk amanah, kejujuran, dan kepedulian terhadap petani.')
page('16. Daftar pustaka dan lampiran')
p('1. Petunjuk Praktikum Evaluasi P1-P4 Computer Vision, studi kasus SIMUTEH, Teknik Informatika UMMI. Sumber tugas, parameter soal, Lampiran A dan B, serta definisi KB.')
p('2. Kode eksperimen dan hasil eksekusi lokal SIMUTEH SEED 1034, 30 Oktober 2026. Berkas CSV dan PNG pada folder hasil, notebook B1-B5, serta src/praproses.py.')
p('<b>Lampiran hitung manual.</b> Perhitungan Bagian 2.1, 3.1 dan 4.1 tersedia dalam Lembar_Hitung_Manual_2330511034.pdf. Foto hasil perhitungan yang ditulis tangan dilampirkan pada laporan setelah selesai.')
p('<b>Bukti tambahan.</b> Notebook dan folder hasil memuat tabel sampling/kuantisasi, eksperimen CLAHE, panel ringan dan bayangan, grafik lima jenis derau, waktu penapis, crop bercak kecil, PSNR 12 citra normal, dan keluaran uji konvolusi.')
p('<b>Berkas pendamping.</b> Slide presentasi 12 halaman tersedia pada Slide_EvalP1-4_2330511034.pptx. Lembar hitung manual tersedia sebagai PDF terpisah. Tautan repository dicantumkan di halaman judul dan kolom LMS.')
page('17. Bukti tambahan ruang warna')
csvtable('b2_sampling.csv','Sampling dan KB pada teh_041')
csvtable('b2_kuantisasi.csv','Kuantisasi dan jumlah level yang benar-benar terpakai')
fig('b2_ringan_bayangan.png','Kanal R pada kelas ringan normal dan berat bayangan.',maxh=220)
p('Ukuran memori tanpa kompresi: foto asli 36 MB, citra kerja berwarna 0,9216 MB, citra keabuan 0,3072 MB, dan 300 foto asli 10,8 GB (satuan desimal). Konversi contoh warna menghasilkan Y bercak 172,894 dan Y daun 102,22; pemeriksaan OpenCV menghasilkan 173 dan 102, serta Hue 25 dan 63.')
page('18. Bukti tambahan histogram dan parameter')
csvtable('b3_clahe.csv','KB eksperimen clipLimit dan tileGridSize')
table('Diagnosis dan usulan perbaikan',[['Kondisi','Diagnosis histogram','Usulan'],['Normal','Sebaran tanpa gangguan cahaya khusus','Pertahankan intensitas, redam derau'],['Gelap','Intensitas bergeser rendah','Gamma 0,5'],['Terang','Intensitas bergeser tinggi','Gamma 1,8'],['Kontras rendah','Sebaran utama memadat','Regang persentil 2-98'],['Bayangan','Distribusi berbeda menurut posisi','Bandingkan koreksi lokal dan gamma 1,8']],[90,220,155])
table('Parameter metode tabel perbaikan',[['Metode','Parameter'],['Negatif','255 - gray'],['Cerah','Tambah 50, saturasi uint8'],['Kontras','alpha 1,5, beta -40; convertScaleAbs memakai absolut'],['Regang','Persentil 2 dan 98'],['Gamma','0,5 dan 1,8; LUT dipotong menjadi uint8'],['Ekualisasi','cv2.equalizeHist'],['CLAHE','clipLimit 2,0; tileGridSize 8 × 8']],[140,325])
page('19. Bukti tambahan pengujian penapis')
csvtable('b4_derau_bawaan.csv','PSNR 12 citra kondisi normal: sebelum dan sesudah median 3')
rrp=rows('b4_tabel_penapis.csv')
best=[]
for noise in ['gauss_10','gauss_20','gauss_40','sp_4%','sp_10%']:
    r=max((r for r in rrp if r['derau']==noise),key=lambda r:float(r['PSNR_dB'])); best.append([noise,r['penapis'],r['PSNR_dB'],r['waktu_ms'],r['KB']])
table('Penapis dengan PSNR tertinggi pada tiap derau',[['Derau','Penapis','PSNR','ms','KB']]+best)
p('Pemeringkatan ini hanya untuk keenam penapis dan citra acuan yang diuji. Data waktu bervariasi antar-eksekusi. Parameter akhir median 3 dipilih sebagai kompromi biaya dan pelestarian detail, bukan sebagai pemenang PSNR pada semua derau.')
path=OUT/'Laporan_EvalP1-4_2330511034_M. Zidane Naufal Azzam.pdf'
SimpleDocTemplate(str(path),pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=45,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
# Lembar perhitungan diketik; foto tulisan tangan dilampirkan secara terpisah.
story=[]; ss['BodyA'].spaceAfter=1; table_padding=0; tn=0
manual=(ROOT/'LEMBAR_HITUNG_MANUAL.md').read_text(encoding='utf8').splitlines(); idx=0
while idx<len(manual):
    line=manual[idx]; idx+=1
    if not line.strip(): continue
    if line.startswith('|'):
        grid=[line];
        while idx<len(manual) and manual[idx].startswith('|'):
            grid.append(manual[idx]); idx+=1
        cells=[[c.strip() for c in row.strip('|').split('|')] for row in grid if not set(row.replace('|','').replace(':','').replace('-','').strip())==set()]
        table('Ekualisasi: PDF = n/16, s = round(7 × CDF)',cells)
    elif line.startswith('## Bagian 3') or line.startswith('## Bagian 4'):
        story.append(PageBreak()); head(escape(line.lstrip('# ')))
    elif line.startswith('#'): head(escape(line.lstrip('# ')))
    else: p(escape(line.replace('**','')))
SimpleDocTemplate(str(OUT/'Lembar_Hitung_Manual_2330511034.pdf'),pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=45,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
print(path)
