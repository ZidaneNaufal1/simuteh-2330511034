"""Membuat notebook pelaksanaan dan menguji Run All melalui kernel baru."""
import os,sys,json
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path.cwd()
kernel=ROOT/'.kernel/kernels/simuteh'; kernel.mkdir(parents=True,exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'SIMUTEH','language':'python'}))
os.environ['JUPYTER_PATH']=str(ROOT/'.kernel')
os.environ['JUPYTER_RUNTIME_DIR']=str(ROOT/'.kernel/runtime')
os.environ['MPLCONFIGDIR']=str(ROOT/'.mplconfig')
os.environ['IPYTHONDIR']=str(ROOT/'.ipython')
def run_script(name):
    return """import os, sys, runpy
from pathlib import Path
root = Path.cwd().resolve().parent
sys.path.insert(0, str(root / 'src'))
os.chdir(root)
try:
    runpy.run_path(str(root / 'src' / %r), run_name='__main__')
finally:
    os.chdir(root / 'notebook')
"""%name
spec=[('B1_lingkungan.ipynb',None,[],[]),('B2_citra_warna.ipynb','eksperimen_awal.py',['b2_kb_kanal.csv','b2_sampling.csv','b2_kuantisasi.csv'],['b2_kanal.png','b2_kb_kanal.png','b2_sampling_kuantisasi.png','b2_ringan_bayangan.png']),('B3_histogram.ipynb','eksperimen_penapis.py',['b3_diagnosis.csv','b3_perbaikan.csv','b3_clahe.csv','b3_pilihan_kondisi.csv'],['b3_histogram_5kondisi.png','b3_histogram_ringan.png','b3_metode_histogram.png','b3_clahe_warna.png','b3_pilihan_kondisi.png']),('B4_penapisan.ipynb','eksperimen_penapis.py',['b4_konvolusi.csv','b4_tabel_penapis.csv','b4_urutan.csv','b4_derau_bawaan.csv'],['b4_psnr.png','b4_semua_derau.png','b4_waktu.png','b4_di.png','b4_crop_bercak.png']),('B5_praproses.ipynb','eksperimen_awal.py',['b5_integrasi_ringkasan.csv'],['b5_pipeline.png','b5_kb.png','b5_sehat.png'])]
for idx,(file,script,tables,figures) in enumerate(spec):
    if idx==0:
        old=json.loads((ROOT/'notebook'/file).read_text(encoding='utf8'))
        nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('# B1 Lingkungan kerja\nM. Zidane Naufal Azzam | 2330511034 | 7A | SEED 1034'),nbformat.v4.new_code_cell('%matplotlib inline\n'+''.join(old['cells'][1]['source']))])
    else:
        cells=[nbformat.v4.new_markdown_cell(f'# {file[0:2]} SIMUTEH\nM. Zidane Naufal Azzam | 2330511034 | 7A | SEED 1034\n\nImplementasi lengkap tersedia pada modul src yang dipanggil di bawah. Keluaran tabel dan gambar ditampilkan setelah percobaan. Analisis ada di laporan PDF.'),nbformat.v4.new_code_cell(run_script(script))]
        if idx==1:
            cells.append(nbformat.v4.new_code_cell(run_script('gambar_hasil.py')))
            cells.append(nbformat.v4.new_code_cell(run_script('lengkapi_hasil.py')))
        for name in tables:
            cells.append(nbformat.v4.new_code_cell(f"import pandas as pd\nfrom IPython.display import display\ndisplay(pd.read_csv('../hasil/{name}'))"))
        for name in figures:
            cells.append(nbformat.v4.new_code_cell(f"from IPython.display import display, Image\ndisplay(Image(filename='../hasil/{name}'))"))
        nb=nbformat.v4.new_notebook(cells=cells)
    nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
    NotebookClient(nb,timeout=300,kernel_name='simuteh',resources={'metadata':{'path':str(ROOT/'notebook')}}).execute()
    nbformat.write(nb,ROOT/'notebook'/file)
    print('LULUS Run All:',file,flush=True)
