"""Eksperimen kuantitatif awal; jalankan dari folder utama proyek."""
import csv
import json
from pathlib import Path
import cv2
import numpy as np
from praproses import praproses, simpan_param

root = Path('data/sintetis')
out = Path('hasil')
out.mkdir(exist_ok=True)
with (root / 'label.csv').open(newline='', encoding='utf-8') as f:
    labels = list(csv.DictReader(f))
def baca(sub, name, gray=False):
    img = cv2.imread(str(root / sub / name), 0 if gray else 1)
    if img is None:
        raise FileNotFoundError(str(root / sub / name))
    return img
def kb(x, md, mb):
    a = x[(md > 0) & (mb == 0)].astype(float)
    b = x[mb > 0].astype(float)
    return abs(b.mean() - a.mean()) / (a.std() + 1e-6) if len(b) else float('nan')
def channels(img):
    b, g, r = cv2.split(img)
    h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
    return dict(B=b, G=g, R=r, Gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), H=h, S=s, V=v)
def save(name, rows):
    with (out / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

individual = []
for row in labels:
    if row['kelas'] == 'sehat': continue
    name = row['nama_file']; im = baca('citra',name)
    md, mb = baca('mask_daun',name,True), baca('mask_bercak',name,True)
    individual.append({'nama':name, 'kelas':row['kelas'], 'kondisi':row['kondisi_cahaya'],
                       **{k:round(kb(v,md,mb),4) for k,v in channels(im).items()}})
save('b2_kb_individu.csv', individual)
aggregated = []
for kelas in ('ringan','berat'):
    for cond in ('normal','gelap','terang','kontras_rendah','bayangan'):
        subset = [r for r in individual if r['kelas']==kelas and r['kondisi']==cond]
        aggregated.append({'kelas':kelas,'kondisi':cond, **{k:round(float(np.mean([r[k] for r in subset])),4) for k in ('B','G','R','Gray','H','S','V')}})
save('b2_kb_kanal.csv', aggregated)
print('Rerata KB kelas berat per kondisi:')
for row in aggregated:
    if row['kelas']=='berat': print(row)

im=baca('citra','teh_041.png'); md=baca('mask_daun','teh_041.png',True); mb=baca('mask_bercak','teh_041.png',True)
gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
sampling=[]
for fx in (0.5,0.2,0.1,0.05):
    small=cv2.resize(gray,None,fx=fx,fy=fx,interpolation=cv2.INTER_AREA)
    enlarged=cv2.resize(small,gray.shape[::-1],interpolation=cv2.INTER_NEAREST)
    sampling.append({'faktor':fx,'lebar':small.shape[1],'tinggi':small.shape[0],'KB':round(kb(enlarged,md,mb),3)})
save('b2_sampling.csv',sampling)
quant=[]
for bits in (1,2,3,4,8):
    step=256//(2**bits); result=(gray.astype(np.uint16)//step)*step
    quant.append({'bit':bits,'level':int(np.unique(result).size),'KB':round(kb(result,md,mb),3)})
save('b2_kuantisasi.csv',quant)

# Pilihan kanal berdasarkan rerata kelas berat dengan mempertimbangkan semua kondisi.
means={k:float(np.mean([r[k] for r in aggregated if r['kelas']=='berat'])) for k in ('B','G','R','Gray','H','S','V')}
best=max(means,key=means.get)
print('Kanal terbaik rerata:',best,means)
param={'lebar':640,'gamma':1.0,'clahe_clip':2.0,'clahe_tile':8,'penapis':'median','kernel':3,'sigma':1.0,'tajam_k':0.0}
simpan_param(param,str(out/'param_praproses.json'))
integrasi=[]
for row in labels:
    name=row['nama_file']; im=baca('citra',name); md=baca('mask_daun',name,True); mb=baca('mask_bercak',name,True)
    a=channels(im)[best]; b=channels(praproses(im,param))[best]
    if row['kelas']=='sehat':
        integrasi.append({'nama':name,'kelas':'sehat','kondisi':row['kondisi_cahaya'],'sebelum':float(a[md>0].std()),'sesudah':float(b[md>0].std())})
    else:
        integrasi.append({'nama':name,'kelas':row['kelas'],'kondisi':row['kondisi_cahaya'],'sebelum':kb(a,md,mb),'sesudah':kb(b,md,mb)})
save('b5_integrasi_individu.csv',integrasi)
summ=[]
for label in ('berbercak','sehat'):
    for cond in ('normal','gelap','terang','kontras_rendah','bayangan'):
        subset=[r for r in integrasi if r['kondisi']==cond and ((r['kelas']=='sehat') == (label=='sehat'))]
        av=float(np.mean([r['sebelum'] for r in subset])); bv=float(np.mean([r['sesudah'] for r in subset]))
        summ.append({'kelompok':label,'kondisi':cond,'sebelum':round(av,3),'sesudah':round(bv,3),'perubahan_persen':round((bv-av)/av*100,2) if av else None})
save('b5_integrasi_ringkasan.csv',summ)
print('Hasil praproses:',summ)
