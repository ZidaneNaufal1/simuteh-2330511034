"""Uji histogram dan penapis pada data SIMUTEH; jalankan dari akar proyek."""
import csv
import time
from pathlib import Path
import cv2
import numpy as np

root=Path('data/sintetis'); out=Path('hasil'); out.mkdir(exist_ok=True)
def baca(sub,name,gray=False):
    im=cv2.imread(str(root/sub/name),0 if gray else 1)
    if im is None: raise FileNotFoundError(name)
    return im
def masks(name): return baca('mask_daun',name,True),baca('mask_bercak',name,True)
def di_kb(x,md,mb):
    sehat=x[(md>0)&(mb==0)].astype(float); bercak=x[mb>0].astype(float)
    di=abs(bercak.mean()-sehat.mean()); return di, di/(sehat.std()+1e-6)
def save(name,rows):
    with (out/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with (root/'label.csv').open(newline='') as f: labels=list(csv.DictReader(f))

stats=[]
for i in list(range(21,26))+list(range(41,46)):
    name=f'teh_{i:03d}.png'; g=cv2.cvtColor(baca('citra',name),cv2.COLOR_BGR2GRAY)
    stats.append({'nama':name,'rerata':round(g.mean(),2),'simpangan_baku':round(g.std(),2),'min':int(g.min()),'maks':int(g.max()),'persen_gelap':round((g<50).mean()*100,2),'persen_terang':round((g>205).mean()*100,2)})
save('b3_diagnosis.csv',stats)
name='teh_045.png'; img=baca('citra',name); gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); md,mb=masks(name)
def gamma(g): return cv2.LUT(gray,np.array([255*(i/255)**g for i in range(256)]).clip(0,255).astype(np.uint8))
lo,hi=np.percentile(gray,(2,98))
metodes={'asli':gray,'negatif':255-gray,'cerah+50':cv2.add(gray,50),'kontras':cv2.convertScaleAbs(gray,alpha=1.5,beta=-40),'regang':np.clip((gray.astype(float)-lo)/(hi-lo)*255,0,255).astype('uint8'),'gamma0.5':gamma(.5),'gamma1.8':gamma(1.8),'ekualisasi':cv2.equalizeHist(gray),'CLAHE':cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(gray)}
save('b3_perbaikan.csv',[{'metode':k,'KB':round(di_kb(v,md,mb)[1],3),'simpangan_baku_citra':round(v.std(),3)} for k,v in metodes.items()])
save('b3_clahe.csv',[{'clip':clip,'tile':tile,'KB':round(di_kb(cv2.createCLAHE(clipLimit=clip,tileGridSize=(tile,tile)).apply(gray),md,mb)[1],3)} for clip in (1.,2.,4.) for tile in (4,8,16)])
rng=np.random.default_rng(42); clean=cv2.cvtColor(baca('bersih','teh_041.png'),cv2.COLOR_BGR2GRAY); md,mb=masks('teh_041.png')
def gauss(sd): return np.clip(clean+rng.normal(0,sd,clean.shape),0,255).astype('uint8')
def sp(p):
    x=clean.copy(); m=rng.random(x.shape); x[m<p/2]=0; x[m>1-p/2]=255; return x
noises={'gauss_10':gauss(10),'gauss_20':gauss(20),'gauss_40':gauss(40),'sp_4%':sp(.04),'sp_10%':sp(.10)}
filters={'rerata_3':lambda x:cv2.blur(x,(3,3)),'rerata_5':lambda x:cv2.blur(x,(5,5)),'gauss_5':lambda x:cv2.GaussianBlur(x,(5,5),1.0),'median_3':lambda x:cv2.medianBlur(x,3),'median_5':lambda x:cv2.medianBlur(x,5),'median_9':lambda x:cv2.medianBlur(x,9)}
rows=[]
for dn,d in noises.items():
    rows.append({'derau':dn,'penapis':'tanpa','PSNR_dB':round(cv2.PSNR(clean,d),3),'waktu_ms':0,'KB':round(di_kb(d,md,mb)[1],3)})
    for name,f in filters.items():
        result=f(d); start=time.perf_counter()
        for _ in range(20): f(d)
        elapsed=(time.perf_counter()-start)*50
        rows.append({'derau':dn,'penapis':name,'PSNR_dB':round(cv2.PSNR(clean,result),3),'waktu_ms':round(elapsed,4),'KB':round(di_kb(result,md,mb)[1],3)})
save('b4_tabel_penapis.csv',rows)
rows=[]
for item in labels:
    if item['kelas']!='ringan': continue
    name=item['nama_file']; g=cv2.cvtColor(baca('bersih',name),cv2.COLOR_BGR2GRAY); md,mb=masks(name)
    for k in (1,3,5,9,15):
        result=g if k==1 else cv2.medianBlur(g,k); di,contrast=di_kb(result,md,mb)
        rows.append({'nama':name,'kernel':k,'dI':round(di,4),'KB':round(contrast,4)})
save('b4_bercak_kecil.csv',rows)
rows=[]
for item in labels:
    if item['kondisi_cahaya']!='normal': continue
    name=item['nama_file']; image=baca('citra',name); clean=baca('bersih',name)
    rows.append({'nama':name,'kelas':item['kelas'],'PSNR_sebelum':round(cv2.PSNR(clean,image),3),'PSNR_sesudah_median3':round(cv2.PSNR(clean,cv2.medianBlur(image,3)),3)})
save('b4_derau_bawaan.csv',rows)
def unsharp(x,k=1.0):
    return cv2.addWeighted(x,1+k,cv2.GaussianBlur(x,(5,5),1.0),-k,0)
noisy=noises['gauss_20']; clean=cv2.cvtColor(baca('bersih','teh_041.png'),cv2.COLOR_BGR2GRAY); md,_=masks('teh_041.png'); latar=md==0
rows=[]
for name,redam in {'Gaussian':lambda x:cv2.GaussianBlur(x,(5,5),1.0),'Median':lambda x:cv2.medianBlur(x,5)}.items():
    for urutan,output in [('tajam-redam',redam(unsharp(noisy))),('redam-tajam',unsharp(redam(noisy)))]:
        rows.append({'penapis':name,'urutan':urutan,'PSNR_dB':round(cv2.PSNR(clean,output),3),'sigma_latar':round(output[latar].std(),3)})
save('b4_urutan.csv',rows)
def korelasi(img,k):
    kh,kw=k.shape; ph,pw=kh//2,kw//2
    padded=np.pad(img.astype(float),((ph,ph),(pw,pw)),mode='edge')
    result=np.zeros(img.shape)
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            result[y,x]=np.sum(padded[y:y+kh,x:x+kw]*k)
    return np.clip(np.round(result),0,255).astype('uint8')
def konvolusi_sejati(img,k):
    """Konvolusi membalik kernel 180 derajat sebelum korelasi."""
    return korelasi(img,np.flip(k))
rows=[]
for name,k in {'rerata':np.ones((3,3))/9, 'asimetris':np.array([[1,0,-1],[2,0,-2],[1,0,-1]],float)}.items():
    t=time.perf_counter(); a=korelasi(clean,k); manual=time.perf_counter()-t
    t=time.perf_counter(); b=cv2.filter2D(clean,-1,k,borderType=cv2.BORDER_REPLICATE); library=time.perf_counter()-t
    c=konvolusi_sejati(clean,k)
    rows.append({'kernel':name,'beda_korelasi_filter2D':int(np.abs(a.astype(int)-b.astype(int)).max()),'beda_konvolusi_filter2D':int(np.abs(c.astype(int)-b.astype(int)).max()),'manual_detik':round(manual,4),'filter2D_detik':round(library,6)})
save('b4_konvolusi.csv',rows)
print('Hasil tersimpan pada folder hasil/')
