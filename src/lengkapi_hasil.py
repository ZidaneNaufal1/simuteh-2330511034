"""Bukti pelengkap Bagian 1-5; dijalankan dari akar repository."""
from pathlib import Path
import csv
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils_cv import kontras_bercak

D=Path('data/sintetis'); O=Path('hasil')
def read(n,sub='citra',gray=False):
    im=cv2.imread(str(D/sub/f'teh_{n:03d}.png'),0 if gray else 1)
    if im is None: raise FileNotFoundError(n)
    return im
def save(name):
    plt.tight_layout(); plt.savefig(O/name,dpi=160,bbox_inches='tight'); plt.close()
def table(name,rows):
    with (O/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def panel(name,items,cols=3):
    fig,axs=plt.subplots(int(np.ceil(len(items)/cols)),cols,figsize=(cols*4,int(np.ceil(len(items)/cols))*3),squeeze=False)
    for ax in axs.flat: ax.axis('off')
    for ax,(title,im) in zip(axs.flat,items):
        ax.imshow(cv2.cvtColor(im,cv2.COLOR_BGR2RGB) if im.ndim==3 else im,cmap='gray',vmin=0,vmax=255); ax.set_title(title)
    save(name)

# Pipeline enam tahap, dengan masukan, proses, dan keluaran per tahap.
steps=[('Akuisisi','Daun + kamera','Foto sesuai jarak/resolusi','Citra BGR'),('Praproses','Citra BGR','Gamma, CLAHE V, median','Citra diperbaiki'),('Segmentasi','Citra praproses','Pisahkan daun dan bercak','Mask prediksi'),('Ekstraksi fitur','Citra + mask prediksi','Hitung luas, warna, tekstur','Vektor fitur'),('Klasifikasi','Vektor fitur','Model mutu (P11)','Sehat/ringan/berat'),('Interpretasi','Kelas + luas','Persentase dan penjelasan','Pertimbangan petugas')]
fig,axs=plt.subplots(2,3,figsize=(13,5))
for i,(ax,(title,inp,proc,out)) in enumerate(zip(axs.flat,steps)):
    ax.axis('off'); ax.text(.02,.9,f'{i+1}. {title}',fontsize=14,fontweight='bold'); ax.text(.02,.65,'Masukan: '+inp,fontsize=10); ax.text(.02,.4,'Proses: '+proc,fontsize=10); ax.text(.02,.15,'Keluaran: '+out,fontsize=10)
save('b1_pipeline.png')
panel('b2_ringan_bayangan.png',[('Ringan normal (021)',read(21)),('Kanal R (021)',read(21)[:,:,2]),('Berat bayangan (045)',read(45)),('Kanal R (045)',read(45)[:,:,2])],2)
# Perbandingan CLAHE V dengan BGR.
im=read(45); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); cl=cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)); hsv[:,:,2]=cl.apply(hsv[:,:,2]); via_v=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR); via_bgr=cv2.merge([cl.apply(c) for c in cv2.split(im)])
panel('b3_clahe_warna.png',[('Asli',im),('CLAHE V',via_v),('CLAHE BGR',via_bgr)])
rows=[]; items=[]
for offset,condition in [(1,'gelap'),(2,'terang'),(3,'kontras_rendah'),(4,'bayangan')]:
    for base in (21,41):
        n=base+offset; g=cv2.cvtColor(read(n),cv2.COLOR_BGR2GRAY)
        if condition=='kontras_rendah':
            lo,hi=np.percentile(g,(2,98)); result=np.clip((g.astype(float)-lo)/(hi-lo)*255,0,255).astype('uint8'); method='regang persentil 2-98'
        else:
            gamma=.5 if condition=='gelap' else 1.8
            result=cv2.LUT(g,np.array([255*(v/255)**gamma for v in range(256)]).astype('uint8')); method=f'gamma {gamma}'
        md=read(n,'mask_daun',True); mb=read(n,'mask_bercak',True)
        rows.append(dict(nama=f'teh_{n:03d}',kondisi=condition,metode=method,KB_sebelum=round(kontras_bercak(g,md,mb),3),KB_sesudah=round(kontras_bercak(result,md,mb),3)))
        items.extend([(f'{n:03d} sebelum',g),(f'{n:03d} sesudah',result)])
table('b3_pilihan_kondisi.csv',rows); panel('b3_pilihan_kondisi.png',items,4)
# Histogram kelas ringan.
plt.figure(figsize=(8,4))
for n in range(21,26):
    g=cv2.cvtColor(read(n),cv2.COLOR_BGR2GRAY); plt.plot(cv2.calcHist([g],[0],None,[256],[0,256]),label=f'{n:03d}')
plt.xlabel('Intensitas'); plt.ylabel('Jumlah piksel'); plt.legend(); save('b3_histogram_ringan.png')
# Crop bercak kecil dari citra bersih, bukan dari citra berderau.
mb=read(21,'mask_bercak',True); count,lab,stats,cent=cv2.connectedComponentsWithStats(mb)
idx=1+int(np.argmin(stats[1:,cv2.CC_STAT_AREA])); x,y,w,h,area=stats[idx]; x0=max(0,x-12); y0=max(0,y-12); x1=min(640,x+w+12); y1=min(480,y+h+12)
g=cv2.cvtColor(read(21,'bersih'),cv2.COLOR_BGR2GRAY)
panel('b4_crop_bercak.png',[(f'Median {k}',(g if k==1 else cv2.medianBlur(g,k))[y0:y1,x0:x1]) for k in (1,3,5,9,15)],5)
rows=list(csv.DictReader(open(O/'b4_tabel_penapis.csv'))); plt.figure(figsize=(9,4))
for noise in ['gauss_10','gauss_20','gauss_40','sp_4%','sp_10%']:
    rr=[r for r in rows if r['derau']==noise]; plt.plot([r['penapis'] for r in rr],[float(r['waktu_ms']) for r in rr],marker='o',label=noise)
plt.ylabel('Waktu rata-rata (ms), 20 pengulangan'); plt.xticks(rotation=30); plt.legend(); save('b4_waktu.png')
fig,axs=plt.subplots(1,2,figsize=(12,4))
for ax,measure in zip(axs,['PSNR_dB','KB']):
    for noise in ['gauss_10','gauss_20','gauss_40','sp_4%','sp_10%']:
        rr=[r for r in rows if r['derau']==noise]; ax.plot([r['penapis'] for r in rr],[float(r[measure]) for r in rr],marker='o',label=noise)
    ax.set_ylabel(measure); ax.tick_params(axis='x',rotation=40); ax.legend(fontsize=8)
save('b4_semua_derau.png')
fig,ax=plt.subplots(figsize=(12,2)); ax.axis('off'); ax.text(.01,.55,'Ubah lebar 640  →  Gamma 1,0  →  CLAHE V (2,0; 8×8)  →  Median 3×3  →  Tajam k=0',fontsize=12); save('b5_pipeline.png')
print('Bukti pelengkap tersimpan.')
