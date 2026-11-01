from pathlib import Path
import csv
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('hasil/presentasi'); OUT.mkdir(exist_ok=True,parents=True)
plt.rcParams.update({'font.family':'Arial','font.size':24,'axes.titlesize':26,'axes.labelsize':24,'xtick.labelsize':22,'ytick.labelsize':22,'legend.fontsize':22})
def rows(n): return list(csv.DictReader(open('hasil/'+n,encoding='utf-8')))
def save(fig,n): fig.savefig(OUT/n,dpi=110,facecolor='white'); plt.close(fig)
conds=['normal','gelap','terang','kontras_rendah','bayangan']
fig,ax=plt.subplots(figsize=(16,5.5)); fig.subplots_adjust(left=.07,right=.99,bottom=.22,top=.79)
rr=rows('b2_kb_kanal.csv')
for ch,col in zip(['B','G','R','Gray','H','S','V'],['#2687de','#49a862','#df4338','#6f7377','#9467bd','#c29d19','#d76bb5']):
    ax.plot(range(5),[float(next(r for r in rr if r['kelas']=='berat' and r['kondisi']==c)[ch]) for c in conds],label=ch,color=col,marker='o',lw=3.5,ms=9)
ax.set_xticks(range(5),['Normal','Gelap','Terang','Kontras\nrendah','Bayangan']); ax.set_yticks([0,2,4,6,8,10]); ax.set_ylabel('KB'); ax.set_ylim(0,10.5); ax.grid(alpha=.18); ax.legend(ncol=7,loc='lower center',bbox_to_anchor=(.5,1.01),frameon=False)
save(fig,'slide06_kanal_besar.png')

gray=cv2.cvtColor(cv2.imread('data/sintetis/citra/teh_045.png'),cv2.COLOR_BGR2GRAY)
lut=np.array([255*(i/255)**1.8 for i in range(256)]).astype('uint8')
variants=[('Asli',gray),('Gamma 1,8',cv2.LUT(gray,lut)),('Ekualisasi',cv2.equalizeHist(gray)),('CLAHE',cv2.createCLAHE(clipLimit=2,tileGridSize=(8,8)).apply(gray))]
fig,(ax,bx)=plt.subplots(1,2,figsize=(16,6),gridspec_kw={'width_ratios':[1.15,1]}); fig.subplots_adjust(left=.07,right=.98,bottom=.22,top=.78,wspace=.55)
for label,arr in variants:
    hist=cv2.calcHist([arr],[0],None,[64],[0,256]).ravel()/arr.size*100
    ax.plot(np.linspace(2,254,64),hist,label=label,lw=3)
ax.set_xlabel('Intensitas'); ax.set_ylabel('Piksel (%)'); ax.set_xticks([0,128,255]); ax.grid(alpha=.18); ax.legend(fontsize=22,loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2,frameon=False)
rr=rows('b3_perbaikan.csv'); labels=['Asli','Negatif','Cerah +50','Kontras','Regang','Gamma 0,5','Gamma 1,8','Ekualisasi','CLAHE']; vals=[float(r['KB']) for r in rr]
bx.barh(range(9),vals,color=['#1e539a' if i!=6 else '#20afd1' for i in range(9)]); bx.set_yticks(range(9),labels); bx.invert_yaxis(); bx.set_xlim(0,4.4); bx.set_xlabel('Kontras bercak (KB)'); bx.set_xticks([0,2,4]); bx.grid(axis='x',alpha=.15)
for i,v in enumerate(vals): bx.text(v+.05,i,f'{v:.2f}'.replace('.',','),va='center',fontsize=22)
save(fig,'slide07_histogram_besar.png')

rr=rows('b4_tabel_penapis.csv'); fig=plt.figure(figsize=(16,7)); grid=fig.add_gridspec(2,10,height_ratios=[2.0,1],hspace=.78,wspace=1.1); fig.subplots_adjust(left=.06,right=.99,bottom=.06,top=.86)
axs=[fig.add_subplot(grid[0,:5]),fig.add_subplot(grid[0,5:])]; names=['tanpa','rerata_3','rerata_5','gauss_5','median_3','median_5','median_9']; x=np.arange(7)
for ax,key,title in zip(axs,['PSNR_dB','waktu_ms'],['PSNR (dB)','Waktu (ms)']):
    for j,(noise,label,col) in enumerate([('gauss_20','Gaussian 20','#1e539a'),('sp_4%','Garam-merica 4%','#20afd1')]):
        vals=[float(next(r for r in rr if r['derau']==noise and r['penapis']==n)[key]) for n in names]
        ax.bar(x+(j-.5)*.36,vals,width=.36,color=col,label=label)
    ax.set_title(title); ax.set_xticks(x,['Asli','R3','R5','G5','M3','M5','M9']); ax.grid(axis='y',alpha=.16); ax.tick_params(axis='x',labelsize=22)
axs[0].set_yticks([0,20,40,60]); axs[1].set_yticks([0,5,10,15]); fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,bbox_to_anchor=(.5,1.01),frameon=False,fontsize=24)
fig.text(.5,.405,'R: rerata | G: Gaussian | M: median | angka: ukuran kernel',ha='center',fontsize=22)
im=cv2.cvtColor(cv2.imread('data/sintetis/bersih/teh_021.png'),cv2.COLOR_BGR2GRAY); mask=cv2.imread('data/sintetis/mask_bercak/teh_021.png',0); n,lab,stats,cent=cv2.connectedComponentsWithStats((mask>0).astype('uint8')); idx=1+np.argmin(stats[1:,cv2.CC_STAT_AREA]); xx,yy,ww,hh,area=stats[idx]; x0=max(0,xx-12); y0=max(0,yy-12); x1=min(640,xx+ww+12); y1=min(480,yy+hh+12)
for j,k in enumerate([1,3,5,9,15]):
    ax=fig.add_subplot(grid[1,j*2:j*2+2]); arr=im if k==1 else cv2.medianBlur(im,k); ax.imshow(arr[y0:y1,x0:x1],cmap='gray',vmin=0,vmax=255,interpolation='nearest'); ax.set_title('Median '+str(k),fontsize=24); ax.axis('off')
save(fig,'slide08_penapis_besar.png')
rr=rows('b5_integrasi_ringkasan.csv')
fig,(ax,bx)=plt.subplots(1,2,figsize=(16,6),gridspec_kw={'width_ratios':[1.6,1]}); fig.subplots_adjust(left=.07,right=.99,bottom=.23,top=.83,wspace=.2)
for j,(key,label,col) in enumerate([('sebelum','Sebelum','#1e539a'),('sesudah','Sesudah','#20afd1')]):
    vals=[float(next(r for r in rr if r['kelompok']=='berbercak' and r['kondisi']==c)[key]) for c in conds]
    ax.bar(np.arange(5)+(j-.5)*.36,vals,width=.36,color=col,label=label)
ax.set_xticks(range(5),['Normal','Gelap','Terang','Kontras\nrendah','Bayangan']); ax.tick_params(axis='x',labelsize=22); ax.set_ylim(0,20); ax.set_yticks([0,5,10,15,20]); ax.set_ylabel('KB'); ax.grid(axis='y',alpha=.15); ax.legend(ncol=2,loc='lower center',bbox_to_anchor=(.5,1.01),frameon=False)
bx.axis('off'); bx.text(.03,.96,'KB naik pada\n4 dari 5 kondisi.',transform=bx.transAxes,va='top',fontsize=29,color='#1e539a',linespacing=1.5)
bx.text(.03,.53,'Terang: KB turun 18,53%.\n\nDaun sehat terang:\nsimpangan baku naik 14,07%.',transform=bx.transAxes,va='top',fontsize=25,linespacing=1.35)
save(fig,'slide10_integrasi_besar.png')
print('Empat panel grafik siap.')
