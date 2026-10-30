"""Grafik dan panel hasil percobaan, dijalankan dari akar repository."""
import csv
from pathlib import Path
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from praproses import praproses
root=Path('data/sintetis'); out=Path('hasil')
def image(n): return cv2.cvtColor(cv2.imread(str(root/'citra'/f'teh_{n:03d}.png')),cv2.COLOR_BGR2RGB)
def save(name):
    plt.tight_layout(); plt.savefig(out/name,dpi=150,bbox_inches='tight'); plt.close()
fig,axs=plt.subplots(2,5,figsize=(15,6))
for j,n in enumerate(range(41,46)):
    axs[0,j].imshow(image(n)); axs[0,j].set_title(['Normal','Gelap','Terang','Kontras rendah','Bayangan'][j]); axs[0,j].axis('off')
for j,n in enumerate(range(1,6)):
    im=cv2.cvtColor(image(n),cv2.COLOR_RGB2BGR); after=cv2.cvtColor(praproses(im),cv2.COLOR_BGR2RGB)
    axs[1,j].imshow(after); axs[1,j].set_title('Sehat sesudah'); axs[1,j].axis('off')
save('contoh_kondisi_dan_sehat.png')
rows=list(csv.DictReader(open(out/'b2_kb_kanal.csv',encoding='utf-8'))); fig,ax=plt.subplots(figsize=(10,5))
cond=['normal','gelap','terang','kontras_rendah','bayangan']; x=np.arange(5)
for channel in ['B','G','R','Gray','H','S','V']:
    vals=[float(next(r for r in rows if r['kelas']=='berat' and r['kondisi']==c)[channel]) for c in cond]
    ax.plot(x,vals,marker='o',label=channel)
ax.set_xticks(x,cond,rotation=15); ax.set_ylabel('KB rata-rata'); ax.set_title('Kelas berat: kontras bercak per kanal'); ax.legend(ncol=4); ax.grid(alpha=.25)
save('b2_kb_kanal.png')
fig,axs=plt.subplots(2,5,figsize=(15,6))
for j,n in enumerate(range(1,6)):
    bgr=cv2.cvtColor(image(n),cv2.COLOR_RGB2BGR); after=cv2.cvtColor(praproses(bgr),cv2.COLOR_BGR2RGB)
    for row,im in enumerate((image(n),after)): axs[row,j].imshow(im); axs[row,j].set_title(('Sebelum' if row==0 else 'Sesudah')+f' {n:03d}'); axs[row,j].axis('off')
save('b5_sehat.png')
rows=list(csv.DictReader(open(out/'b5_integrasi_ringkasan.csv',encoding='utf-8'))); fig,ax=plt.subplots(figsize=(9,4.5)); subset=[r for r in rows if r['kelompok']=='berbercak']
x=np.arange(5); ax.bar(x-.18,[float(r['sebelum']) for r in subset],.36,label='Sebelum'); ax.bar(x+.18,[float(r['sesudah']) for r in subset],.36,label='Sesudah'); ax.set_xticks(x,cond,rotation=15); ax.set_ylabel('KB rata-rata (40 citra)'); ax.legend(); ax.grid(axis='y',alpha=.2); save('b5_kb.png')
rows=list(csv.DictReader(open(out/'b4_tabel_penapis.csv',encoding='utf-8'))); fig,axs=plt.subplots(1,2,figsize=(12,4))
for ax,d in zip(axs,['gauss_20','sp_4%']):
    subset=[r for r in rows if r['derau']==d]; ax.bar([r['penapis'] for r in subset],[float(r['PSNR_dB']) for r in subset]); ax.set_title(d); ax.set_ylabel('PSNR (dB)'); ax.tick_params(axis='x',rotation=55)
save('b4_psnr.png')
rows=list(csv.DictReader(open(out/'b4_bercak_kecil.csv',encoding='utf-8'))); fig,ax=plt.subplots(figsize=(7,4)); ks=[1,3,5,9,15]; means=[np.mean([float(r['dI']) for r in rows if int(r['kernel'])==k]) for k in ks]; ax.plot(ks,means,marker='o'); ax.set_xticks(ks); ax.set_xlabel('Ukuran kernel median'); ax.set_ylabel('Rerata dI'); ax.grid(alpha=.3); save('b4_di.png')
raw=cv2.imread(str(root/'citra'/'teh_041.png')); hsv=cv2.cvtColor(raw,cv2.COLOR_BGR2HSV); b,g,r=cv2.split(raw); h,s,v=cv2.split(hsv); gray=cv2.cvtColor(raw,cv2.COLOR_BGR2GRAY)
fig,axs=plt.subplots(2,4,figsize=(12,6))
for ax,(name,arr) in zip(axs.flat,[('Asli',cv2.cvtColor(raw,cv2.COLOR_BGR2RGB)),('B',b),('G',g),('R',r),('Gray',gray),('H',h),('S',s),('V',v)]):
    ax.imshow(arr,cmap='gray' if arr.ndim==2 else None); ax.set_title(name); ax.axis('off')
save('b2_kanal.png')
fig,axs=plt.subplots(2,5,figsize=(15,5))
for j,fx in enumerate((.5,.2,.1,.05)):
    small=cv2.resize(gray,None,fx=fx,fy=fx,interpolation=cv2.INTER_AREA); arr=cv2.resize(small,gray.shape[::-1],interpolation=cv2.INTER_NEAREST)
    axs[0,j].imshow(arr,cmap='gray',vmin=0,vmax=255); axs[0,j].set_title(f'Sampling {fx}'); axs[0,j].axis('off')
axs[0,4].imshow(gray,cmap='gray',vmin=0,vmax=255); axs[0,4].set_title('Asli'); axs[0,4].axis('off')
for j,bits in enumerate((1,2,3,4,8)):
    step=256//2**bits; arr=((gray.astype('uint16')//step)*step).astype('uint8'); axs[1,j].imshow(arr,cmap='gray',vmin=0,vmax=255); axs[1,j].set_title(f'{bits} bit'); axs[1,j].axis('off')
save('b2_sampling_kuantisasi.png')
fig,ax=plt.subplots(figsize=(8,4))
for n in range(41,46):
    gray=cv2.cvtColor(cv2.imread(str(root/'citra'/f'teh_{n:03d}.png')),cv2.COLOR_BGR2GRAY)
    ax.plot(cv2.calcHist([gray],[0],None,[256],[0,256]),label=f'{n:03d}')
ax.set_xlabel('Intensitas'); ax.set_ylabel('Jumlah piksel'); ax.legend(); save('b3_histogram_5kondisi.png')
gray=cv2.cvtColor(cv2.imread(str(root/'citra'/'teh_045.png')),cv2.COLOR_BGR2GRAY); lo,hi=np.percentile(gray,(2,98))
def gamma(g): return cv2.LUT(gray,np.array([255*(i/255)**g for i in range(256)]).astype('uint8'))
methods={'Asli':gray,'Negatif':255-gray,'Cerah +50':cv2.add(gray,50),'Kontras':cv2.convertScaleAbs(gray,alpha=1.5,beta=-40),'Regang':np.clip((gray.astype(float)-lo)/(hi-lo)*255,0,255).astype('uint8'),'Gamma 0,5':gamma(.5),'Gamma 1,8':gamma(1.8),'Ekualisasi':cv2.equalizeHist(gray),'CLAHE':cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(gray)}
fig,axs=plt.subplots(2,9,figsize=(19,4))
for j,(name,arr) in enumerate(methods.items()):
    axs[0,j].imshow(arr,cmap='gray',vmin=0,vmax=255); axs[0,j].set_title(name); axs[0,j].axis('off'); axs[1,j].hist(arr.ravel(),bins=64,range=(0,256)); axs[1,j].set_xlim(0,255); axs[1,j].set_yticks([])
save('b3_metode_histogram.png')
print('Panel dan grafik tersimpan di hasil/')
