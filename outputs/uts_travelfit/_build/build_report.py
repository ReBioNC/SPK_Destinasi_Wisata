"""Build a source-backed UTS report without changing production artifacts."""
from pathlib import Path
import hashlib
import json
import math
import sqlite3
import subprocess
import sys
from datetime import date, datetime

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from recommender.data_pipeline import validate_artifacts
from recommender.spk import ahp, profiles, topsis, validation, similarity, geo
from recommender.kota_asal import KOTA_ASAL

OUT = ROOT / 'outputs/uts_travelfit'
BUILD = OUT / '_build'
OUT.mkdir(parents=True, exist_ok=True)
DEST = BUILD / 'source_report.docx'
REPO_URL = 'https://github.com/ReBioNC/SPK_Destinasi_Wisata'
BRANCH = 'new'
ACCESS = '5 Oktober 2026'

result = validate_artifacts(ROOT)
df = result.destinations
summary = result.summary
km = json.loads((ROOT / 'reports/clustering/kmeans_evaluation.json').read_text(encoding='utf-8'))
assert km['pipeline_fingerprint'] == result.manifest['pipeline_fingerprint']
assert len(df) == 443 and df.place_id.is_unique
head = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True).strip()
protected = ['Laporan_SPK_TravelFit.docx', 'Perhitungan_SPK_TravelFit.xlsx', 'db.sqlite3']
protected += list(result.manifest['source_hashes'])
before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in protected}

# Use the same ticket and Haversine definitions as the active website.
origin = KOTA_ASAL['Serang']
banten = df.loc[df.province.eq('Banten')].sort_values('place_id').copy()
decision, provenance, costs = [], [], []
for row in banten.itertuples():
    distance = geo.haversine(*origin, row.lat, row.long)
    c5 = 1.0 if row.category_clean == 'alam' else 0.5 if row.category_clean == 'budaya' else 0.0
    decision.append([float(row.price), row.c2_rating_for_model, distance,
                     row.c4_facility_score, c5, 0.0])
    costs.append({'tiket': float(row.price), 'sisa': 10000 - float(row.price)})
    provenance.append({'place_id': row.place_id, 'distance': distance, 'source': 'Haversine'})
weights = profiles.ACTIVE_PROFILES['hemat']['weights']
X = np.array(decision, dtype=float)
den = np.sqrt((X**2).sum(axis=0))
R = np.divide(X, den, out=np.zeros_like(X), where=den != 0)
V = R * np.array(weights)
pos = np.array([V[:,j].min() if cost else V[:,j].max() for j,cost in enumerate(profiles.IS_COST)])
neg = np.array([V[:,j].max() if cost else V[:,j].min() for j,cost in enumerate(profiles.IS_COST)])
rank = topsis.rank(decision, weights, profiles.IS_COST)
saw = validation.saw_rank(decision, weights, profiles.IS_COST)
rho = validation.spearman([r['idx'] for r in rank], [r[0] for r in saw])
evidence = {'head': head, 'rows':len(df), 'categories':df.category_clean.value_counts().to_dict(),
            'provinces':df.province.value_counts().to_dict(), 'summary': summary,
            'scenario': {'origin':'Serang','province':'Banten','budget':10000,'budget_basis':'ticket',
                         'distance_basis':'haversine','profile':'hemat','primary':'alam','secondary':'budaya','hobbies':[]},
            'decision':decision,'denominators':den.tolist(),'normalized':R.tolist(),
            'weighted':V.tolist(),'ideal_positive':pos.tolist(),'ideal_negative':neg.tolist(),
            'distance_provenance':provenance,'rank':rank,'saw':saw,'spearman':rho,
            'protected_hashes':before}
(BUILD / 'evidence.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

def number(value, decimals=2):
    return f'{float(value):,.{decimals}f}'.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

def money(value):
    return 'Rp' + number(value,0)

def repo(path):
    return f'{REPO_URL}/blob/{BRANCH}/{path}'

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(4), Cm(3)
sec.top_margin, sec.bottom_margin = Cm(3), Cm(3)
sec.header_distance, sec.footer_distance = Cm(1.25), Cm(1.25)
sec.different_first_page_header_footer = True

for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','TOC 1','TOC 2','TOC 3']:
    if name not in doc.styles:
        doc.styles.add_style(name,1)
    s=doc.styles[name]
    s.font.name='Times New Roman'
    s.font.size=Pt(12)
    s.font.color.rgb=RGBColor(0,0,0)
    s.paragraph_format.line_spacing=1.15
    s.paragraph_format.space_after=Pt(6)
    s.paragraph_format.widow_control=True
    fonts=s.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ['ascii','hAnsi','eastAsia','cs']:
        fonts.set(qn('w:'+attr),'Times New Roman')

# Remove template theme fonts and decorative rules, including linked character
# styles, so Word cannot reintroduce a sans-serif heading from the theme.
for s in doc.styles:
    if not hasattr(s,'font'): continue
    s.font.name='Times New Roman'
    s.font.size=Pt(12)
    rp=s.element.get_or_add_rPr()
    fonts=rp.get_or_add_rFonts()
    for attr in list(fonts.attrib):
        if 'theme' in attr.lower(): del fonts.attrib[attr]
    for attr in ['ascii','hAnsi','eastAsia','cs']:
        fonts.set(qn('w:'+attr),'Times New Roman')
    for border in s.element.xpath('.//w:pBdr'):
        border.getparent().remove(border)
for name in ['TOC 1','TOC 2','TOC 3']:
    doc.styles[name].paragraph_format.space_after=Pt(0)
    doc.styles[name].paragraph_format.space_before=Pt(0)
    doc.styles[name].paragraph_format.keep_with_next=False
doc.styles['Normal'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
for name in ['Title','Heading 1','Heading 2','Heading 3']:
    doc.styles[name].font.bold=True
    doc.styles[name].paragraph_format.keep_with_next=True
    doc.styles[name].paragraph_format.space_before=Pt(12)
doc.styles['Heading 1'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.styles['Heading 2'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
doc.styles['Heading 3'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
doc.styles['Title'].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
settings=doc.settings.element
update=OxmlElement('w:updateFields'); update.set(qn('w:val'),'true');settings.append(update)

def paragraph(text='', style=None, align=None):
    p=doc.add_paragraph(text,style)
    if align is not None:p.alignment=align
    return p

def heading(text,level=2):
    return doc.add_heading(text,level)

def chapter(text):
    p=heading(text,1)
    p.paragraph_format.page_break_before=True

def link(label,url):
    p=paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');rp=OxmlElement('w:rPr')
    f=OxmlElement('w:rFonts');f.set(qn('w:ascii'),'Times New Roman');f.set(qn('w:hAnsi'),'Times New Roman');rp.append(f)
    c=OxmlElement('w:color');c.set(qn('w:val'),'000000');rp.append(c)
    u=OxmlElement('w:u');u.set(qn('w:val'),'single');rp.append(u)
    size=OxmlElement('w:sz');size.set(qn('w:val'),'24');rp.append(size)
    r.append(rp);t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)
    return p

def caption(text):
    p=paragraph(text,'Caption',WD_ALIGN_PARAGRAPH.LEFT)
    p.paragraph_format.keep_with_next=True
    return p

def table(headers, rows, widths=None, centered=()):
    t=doc.add_table(rows=1,cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    widths=widths or [14/len(headers)]*len(headers)
    props=t._tbl.tblPr
    layout=OxmlElement('w:tblLayout');layout.set(qn('w:type'),'fixed');props.append(layout)
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        el=OxmlElement('w:'+side)
        for k,v in [('val','single'),('sz','4'),('color','D9D9D9')]:el.set(qn('w:'+k),v)
        borders.append(el)
    props.append(borders)
    grid=t._tbl.tblGrid
    for el,w in zip(grid.gridCol_lst,widths):el.set(qn('w:w'),str(round(Cm(w).twips)))
    for j,h in enumerate(headers):t.rows[0].cells[j].text=str(h)
    for values in rows:
        cells=t.add_row().cells
        for j,val in enumerate(values):cells[j].text='' if val is None else str(val)
    for i,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr()
        nosplit=OxmlElement('w:cantSplit');trpr.append(nosplit)
        if i==0:
            repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
        for j,cell in enumerate(row.cells):
            cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for side,value in [('top','75'),('bottom','75'),('left','90'),('right','90')]:
                e=OxmlElement('w:'+side);e.set(qn('w:w'),value);e.set(qn('w:type'),'dxa');margins.append(e)
            cp.append(margins)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E7E7E7' if i==0 else 'FFFFFF');cp.append(sh)
            for p in cell.paragraphs:
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER if i==0 or j in centered else WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after=Pt(3)
                p.paragraph_format.line_spacing=1.15
                if len(t.rows)<=8:
                    p.paragraph_format.keep_with_next=(i<len(t.rows)-1)
                elif i<3:
                    p.paragraph_format.keep_with_next=True
                for r in p.runs:
                    r.font.name='Times New Roman';r.font.size=Pt(12);r.font.bold=(i==0)
    paragraph().paragraph_format.space_after=Pt(0)
    return t

# Simple native Word math runs retain editability without a raster approximation.
def math_run(text):
    r=OxmlElement('m:r')
    rp=OxmlElement('w:rPr')
    f=OxmlElement('w:rFonts')
    for attr in ['ascii','hAnsi','eastAsia','cs']:f.set(qn('w:'+attr),'Times New Roman')
    rp.append(f)
    size=OxmlElement('w:sz');size.set(qn('w:val'),'24');rp.append(size)
    r.append(rp)
    t=OxmlElement('m:t');t.text=text;r.append(t);return r

def frac(numerator,denominator):
    f=OxmlElement('m:f');a=OxmlElement('m:num');b=OxmlElement('m:den')
    a.append(math_run(numerator));b.append(math_run(denominator));f.extend([a,b]);return f

def equation(left, numerator=None, denominator=None, rest=''):
    p=paragraph(align=WD_ALIGN_PARAGRAPH.CENTER)
    om=OxmlElement('m:oMath');om.append(math_run(left))
    if numerator is not None:om.append(frac(numerator,denominator))
    if rest:om.append(math_run(rest))
    p._p.append(om)
    return p

footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE')
r=OxmlElement('w:r');t=OxmlElement('w:t');t.text='1';r.append(t);field.append(r);footer._p.append(field)

# COVER
paragraph('LAPORAN UTS','Title')
paragraph('SISTEM PENDUKUNG KEPUTUSAN DAN DATA MINING',align=WD_ALIGN_PARAGRAPH.CENTER)
paragraph()
paragraph('TravelFit Rekomendasi Destinasi Wisata Jawa','Title')
paragraph('Penerapan CRISP DM K Means dan AHP TOPSIS',align=WD_ALIGN_PARAGRAPH.CENTER)
paragraph('Dataset aktif 437 destinasi Kaggle dan 6 destinasi kurasi Jawa',align=WD_ALIGN_PARAGRAPH.CENTER)
paragraph()
paragraph('Disusun oleh',align=WD_ALIGN_PARAGRAPH.CENTER)
for name,nim in [('Kristofer Ryan Giggs Eka Saputra','412024005'),('Cristian Dion','412024006'),
                 ('Reynard Liu','412025022'),('Justin Augusto Liustri','412025029')]:
    paragraph(name+'  '+nim,align=WD_ALIGN_PARAGRAPH.CENTER)
paragraph()
paragraph('PROGRAM STUDI INFORMATIKA',align=WD_ALIGN_PARAGRAPH.CENTER)
paragraph('2026',align=WD_ALIGN_PARAGRAPH.CENTER)

doc.add_page_break()
p=paragraph('DAFTAR ISI','Title')
toc=paragraph()
begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin')
instr=OxmlElement('w:instrText');instr.set(qn('xml:space'),'preserve');instr.text=' TOC \\o "1-2" \\h \\z \\u '
sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate')
end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end')
for el in [begin,instr,sep,end]:
    run=OxmlElement('w:r');run.append(el);toc._p.append(run)

chapter('BAB 1 PENDAHULUAN DAN INTELLIGENCE')
heading('1 1 Latar Belakang')
paragraph('TravelFit dikembangkan untuk membantu wisatawan membandingkan destinasi wisata berdasarkan anggaran, lokasi asal, minat, dan prioritas perjalanan. Satu tempat tidak selalu menjadi pilihan terbaik untuk semua pengguna. Destinasi dengan harga rendah dapat memerlukan perjalanan yang lebih jauh, sedangkan tempat dengan rating tinggi dapat kurang sesuai dengan kategori atau aktivitas yang diinginkan. Karena itu, pemilihan tujuan memerlukan penilaian beberapa kriteria secara bersamaan.')
paragraph('Dalam proyek ini, kami menggabungkan data destinasi dan preferensi pengguna melalui Sistem Pendukung Keputusan atau SPK. Data mining digunakan untuk mengenali kelompok destinasi yang memiliki karakteristik serupa. SPK kemudian menghitung peringkat kandidat yang memenuhi batas anggaran dan wilayah pengguna. Hasilnya berupa rekomendasi yang dapat ditelusuri melalui nilai kriteria, bobot, harga dan sisa alokasi tiket, dan catatan kualitas data.')
paragraph(f'Implementasi aktif menggunakan 443 destinasi, yaitu 437 baris Indonesia Tourism Destination dari Kaggle dan 6 tambahan hasil kurasi di Jawa. Seluruh 443 ID dipertahankan dalam preprocessing dan pengelompokan. Model K-Means pada snapshot ini memilih dua cluster dengan silhouette {number(km["silhouette"],5)}. Nilai tersebut menunjukkan hasil evaluasi internal clustering, bukan persentase akurasi rekomendasi atau kepuasan pengguna (Kelompok TravelFit, 2026a).')

heading('1 2 Identifikasi Masalah')
paragraph('Masalah utama yang kami tangani adalah kesulitan membandingkan alternatif wisata secara konsisten ketika pengguna mempunyai kebutuhan yang berbeda. Informasi pada dataset belum seluruhnya seragam: sebagian durasi kunjungan kosong, satu rating perlu imputasi untuk model, dan satu destinasi mempunyai konflik antara label kota dan koordinat. Deskripsi juga tidak selalu menyebut fasilitas secara lengkap sehingga perlu dibaca sebagai sumber indikator, bukan bukti survei lapangan.')
paragraph('Budget aplikasi dibatasi pada harga tiket satu destinasi per orang. Transportasi, makan dan penginapan berada di luar cakupan agar sistem tidak memerlukan koefisien biaya yang belum tervalidasi. Angka harga pada dataset tetap belum menjamin keseragaman antara tiket masuk dan paket wisata. Pulau Pelangi, misalnya, memiliki Price sebesar Rp900.000 pada data asli. Angka ini dipertahankan sebagai snapshot sumber, tetapi jenis komponen biayanya perlu diaudit sebelum disebut sebagai tiket masuk murni.')
paragraph('Rumusan masalah proyek adalah bagaimana menyiapkan data wisata tanpa kehilangan ID aktif, bagaimana mengelompokkan destinasi berdasarkan fitur yang tersedia, dan bagaimana menghasilkan peringkat yang mempertimbangkan enam kriteria sesuai preferensi pengguna. Rumusan berikutnya adalah bagaimana menyampaikan keterbatasan data agar pengguna tidak menganggap tarif snapshot maupun indikator deskripsi sebagai fakta lapangan yang sudah terverifikasi.')

heading('1 3 Tujuan dan Manfaat')
paragraph('Tujuan proyek adalah membangun aplikasi rekomendasi wisata yang memberikan penilaian terukur dan mudah dipahami. Secara teknis, tujuan tersebut diterjemahkan menjadi pipeline yang mempertahankan 443 ID, fitur clustering yang finite, model K-Means dengan evaluasi terdokumentasi, bobot kriteria yang konsisten, serta TOPSIS yang menangani kondisi kandidat kosong, satu kandidat, dan kriteria bernilai sama.')
paragraph('Manfaat bagi wisatawan adalah tersedianya daftar pembanding yang sesuai preferensi beserta alasan peringkatnya. Bagi pengelola proyek, pemisahan data mentah, data olahan, metadata, dan hasil model memudahkan pembaruan serta audit. Bagi pembelajaran SPK dan data mining, TravelFit memperlihatkan hubungan antara pemahaman masalah, persiapan data, pengelompokan, pembobotan, dan pemilihan alternatif.')

heading('1 4 Ruang Lingkup')
paragraph('Wilayah tujuan aplikasi dibatasi pada enam provinsi di Jawa: Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, Daerah Istimewa Yogyakarta, dan Jawa Timur. Kota asal masih dapat dipilih dari daftar kota di Indonesia. Pembatasan tujuan tidak berarti bahwa seluruh kabupaten, kota, atau objek wisata di setiap provinsi telah terwakili. Dataset awal berpusat pada lima kota, sedangkan tambahan mencakup Pandeglang, Lebak, Purworejo, dan Ngawi.')
paragraph('Cakupan geografis mengikuti label administratif sumber dan keputusan retensi data. Beberapa wisata bahari berada di pulau lepas pantai, sehingga dataset tidak tepat disebut hanya destinasi daratan Pulau Jawa. Pelabuhan Marina dengan ID 9 tetap dipertahankan meskipun koordinat sumber berada di luar Jawa. Aplikasi menandainya sebagai data yang perlu ditinjau. Peta SVG memuat enam provinsi dan merupakan visualisasi skematis, bukan sistem navigasi atau pembuktian batas administratif.')
paragraph('Data aktif terdiri atas 437 destinasi Kaggle dan 6 destinasi tambahan hasil kurasi. Lingkup perhitungan adalah pemilihan satu destinasi berdasarkan enam kriteria. Pengguna memasukkan preferensi melalui formulir, lalu sistem menyaring kandidat berdasarkan provinsi dan budget tiket sebelum menghitung peringkat TOPSIS.')

heading('1 5 Cara Pengumpulan Data')
paragraph('Data utama diperoleh dari dataset Indonesia Tourism Destination milik aprabowo di Kaggle. Berkas tourism_with_id.csv memuat 437 destinasi dan tourism_rating.csv memuat 10.000 baris interaksi. Pemeriksaan terhadap unduhan langsung Kaggle pada 1 Oktober 2026 menunjukkan bahwa kedua berkas lokal identik secara byte dan SHA-256 dengan berkas dalam arsip unduhan. Dengan demikian, nilai sumber tidak dibuat oleh tahap preprocessing. Akan tetapi, kesamaan berkas tidak membuktikan bahwa semua atribut merupakan harga atau kondisi terkini (aprabowo, n.d.).')
paragraph('Enam destinasi tambahan disusun dari dokumen tarif pemerintah daerah dan titik lokasi OpenStreetMap. Kelompok mencatat URL, halaman tarif, titik lokasi, dan pembatasan penggunaan data. Lima rating tambahan berasal dari pengamatan manual panel Google Maps pada 30 September 2026 setelah nama dan lokasi dinyatakan sesuai. Rating Taman Hutan Raya Banten tidak diambil dari listing yang identitasnya belum pasti. Nilai sumbernya tetap kosong, sedangkan kolom khusus model diisi median 4,5.')
caption('Tabel 1 Sumber data aktif dan perannya')
table(['Sumber','Jumlah','Peran'],[
    ['Kaggle tourism_with_id.csv','437 destinasi','Nama, deskripsi, kota, kategori, harga, rating, dan koordinat sumber'],
    ['Kurasi Jawa destinasi_jawa_review.csv','6 destinasi','Dua tambahan Banten dan empat tambahan Jawa lainnya'],
    ['Kaggle tourism_rating.csv','10.000 interaksi','Agregasi penilaian pengguna setelah validasi dan deduplikasi'],
    ['Pengamatan Google Maps','5 rating dipakai','Melengkapi rating destinasi tambahan yang cocok identitasnya'],
    ['Formulir website','Per permintaan','Preferensi pengguna untuk pemeringkatan, bukan survei kelompok']], [4.1,2.6,7.3])
paragraph('Data tambahan bukan dataset resmi pemerintah secara keseluruhan. Tarif didukung dokumen pemerintah, titik lokasi berasal dari pemetaan komunitas, kategori dan deskripsi merupakan kurasi, serta rating berasal dari agregat pihak ketiga. OpenStreetMap mempunyai ketentuan ODbL dan atribusi. Rating Google Maps tidak otomatis mempunyai lisensi terbuka yang sama dengan OSM. Asal, fungsi, dan batas setiap atribut harus dibedakan saat laporan maupun data didistribusikan (OpenStreetMap Foundation, n.d.; Kelompok TravelFit, 2026b).')

heading('1 6 Gambaran dan Kualitas Data')
caption('Tabel 2 Distribusi kategori destinasi aktif')
table(['Kategori','Jumlah','Proporsi'],[[cat,str(int(count)),number(count/443*100,2)+'%']
    for cat,count in df.category_clean.value_counts().items()]+[['Total','443','100,00%']], [6,4,4], (1,2))
caption('Tabel 3 Distribusi label provinsi pada data olahan')
table(['Provinsi','Jumlah destinasi'],[[prov,str(int(count))] for prov,count in df.province.value_counts().items()], [10,4],(1,))
paragraph('Label DI Yogyakarta pada CSV dinormalisasi menjadi Daerah Istimewa Yogyakarta saat impor ke aplikasi. Jumlah tersebut adalah distribusi label pada dataset, bukan ukuran banyaknya destinasi nyata di provinsi. Sebanyak 137 destinasi mempunyai harga nol; nilainya dipertahankan karena tempat wisata gratis merupakan alternatif yang sah. Harga sumber berkisar Rp0 sampai Rp900.000, sedangkan rating teramati berkisar 3,4 sampai 5,0.')
paragraph('Pada data Kaggle, 232 nilai Time_Minutes kosong. Setelah enam tambahan digabungkan, jumlah nilai kosong menjadi 238. Kolom durasi kunjungan tidak diimputasi dan tidak digunakan sebagai fitur K-Means. Formulir aktif tidak menggunakan durasi perjalanan atau moda untuk menghitung biaya.')
paragraph('Kolom data_quality_issues menandai masalah, bukan otomatis menghapus baris. Snapshot aktif menandai dua ID: Pelabuhan Marina karena konflik lokasi dan Tahura karena rating kosong. Pemeriksaan rentang latitude -90 sampai 90 dan longitude -180 sampai 180 hanya memastikan koordinat numerik berada pada rentang dunia. Pemeriksaan itu tidak membuktikan bahwa titik benar-benar berada pada wilayah administratif yang dicantumkan.')

heading('1 7 Kategorisasi Masalah dan Pengguna Akhir')
paragraph('Pemilihan destinasi termasuk masalah semi-terstruktur dan multikriteria. Harga, rating, jarak, serta skor hasil ekstraksi dapat dihitung, tetapi prioritas biaya, kualitas, kategori, dan hobi bergantung pada pengguna. Sistem membantu menyusun perbandingan tanpa menggantikan keputusan akhir wisatawan. Pengelompokan destinasi adalah masalah unsupervised karena dataset tidak menyediakan label cluster acuan yang benar untuk setiap objek.')
paragraph('Pengguna akhir utama adalah wisatawan yang merencanakan tujuan berdasarkan anggaran dan minat. Mahasiswa dan wisatawan dengan anggaran terbatas dapat menggunakan profil Hemat; pengguna yang menekankan rating dapat menggunakan profil Kualitas. Profil Petualang menekankan jarak dan kecocokan, sedangkan profil Seimbang menjadi pilihan umum. Pengelola data menjalankan preprocessing, impor, dan pembaruan model.')
paragraph('Tahap Intelligence mengidentifikasi masalah dan mengumpulkan informasi. Tahap Design merumuskan alternatif, kriteria, metode, dan rancangan pengujian. Tahap Choice diwujudkan sebagai pemeringkatan TOPSIS dan pemilihan alternatif oleh pengguna. Implementasi menempatkan perhitungan tersebut pada aplikasi Django agar dapat digunakan kembali untuk preferensi yang berbeda.')

heading('1 8 Penerapan CRISP DM')
paragraph('CRISP-DM adalah kerangka proses data mining, bukan algoritma yang menggantikan K-Means. Enam tahapnya dapat diulang ketika hasil evaluasi memperlihatkan masalah data atau kebutuhan pengguna berubah. Kami menggunakan kerangka ini untuk menjaga keterkaitan antara tujuan rekomendasi dan keputusan teknis (IBM, n.d.).')
for name,text in [
    ('Business Understanding','Kami menetapkan masalah pemilihan tujuan wisata, pengguna akhir, ruang lingkup Jawa, batas anggaran, dan kebutuhan penjelasan rekomendasi. Ukuran keberhasilan teknis dibedakan dari kepuasan pengguna yang belum diukur.'),
    ('Data Understanding','Kami memeriksa sumber Kaggle, enam tambahan, penilaian pengguna, distribusi kota dan kategori, nilai kosong, serta konflik identitas dan lokasi. Tahap ini menemukan keterbatasan representasi wilayah dan semantik harga.'),
    ('Data Preparation','Kami menggabungkan data, merapikan kolom dan teks, melakukan konversi angka, menyimpan penanda kualitas, mengagregasi interaksi, membentuk fitur deskripsi, serta membuat Z-score dan one-hot encoding dengan retensi semua ID.'),
    ('Modeling','Kami melatih K-Means pada seluruh 443 destinasi. AHP menghitung bobot enam kriteria dan TOPSIS menyusun peringkat kandidat pada saat pengguna mengirim preferensi. Label cluster tidak menjadi filter kandidat TOPSIS.'),
    ('Evaluation','Kami mengevaluasi konfigurasi k, silhouette, inertia, ukuran cluster, konsistensi AHP, hasil perhitungan, edge case, sensitivitas, dan integrasi aplikasi. Evaluasi ini memeriksa hasil teknis model dan perhitungan SPK.'),
    ('Deployment','Kami mengintegrasikan data tervalidasi dan hasil pengelompokan ke Django dan SQLite. Website menampilkan rekomendasi, harga tiket, kualitas data, dan peta Jawa. Penerapan yang tercatat merupakan lingkungan lokal, bukan layanan publik yang telah diuji operasional.')]:
    heading(name,3);paragraph(text)

chapter('BAB 2 PERANCANGAN DAN DESIGN')
heading('2 1 Model Masalah')
paragraph('Masukan sistem terdiri atas data destinasi dan preferensi pengguna. Data destinasi menyediakan atribut relatif tetap, seperti harga sumber, rating, koordinat, kategori, dan indikator deskripsi. Preferensi pengguna menentukan wilayah kandidat, budget tiket, kota asal, minat kategori, hobi, dan profil prioritas. Gabungan keduanya menghasilkan matriks keputusan dengan enam kolom kriteria.')
caption('Tabel 4 Variabel input dan hubungannya dengan output')
table(['Variabel','Pengaruh pada sistem'],[
    ['Budget tiket maksimum per orang','Menyaring harga tiket sumber yang tidak melampaui budget'],
    ['Kota asal dan koordinat destinasi','Menentukan jarak garis lurus C3, tidak mengubah harga C1'],
    ['Provinsi tujuan','Menyaring wilayah destinasi yang dibandingkan'],
    ['Kategori utama dan sekunder','Menentukan skor kecocokan C5'],
    ['Hobi yang dipilih','Menentukan kemiripan Jaccard C6'],
    ['Profil atau slider bobot','Menentukan pengaruh relatif C1 sampai C6'],
    ['Harga, rating, deskripsi, dan kategori sumber','Membentuk atribut SPK dan fitur clustering']], [5,9])
paragraph('Output utama adalah maksimal sepuluh rekomendasi yang diurutkan berdasarkan nilai preferensi TOPSIS. Setiap hasil menampilkan identitas destinasi, kategori, label segmen, rating beserta status imputasinya, jarak garis lurus, harga tiket dan sisa alokasi tiket, dan alasan posisi relatifnya. Skor TOPSIS adalah nilai kedekatan terhadap solusi ideal pada kumpulan kandidat yang sedang dibandingkan; skor itu bukan probabilitas bahwa pengguna pasti puas.')
paragraph('C1 harga tiket tidak dihitung dari jarak. C3 menilai kedekatan secara tersendiri sehingga transportasi tidak dihitung ulang di dalam C1. Dua atribut ini memiliki definisi berbeda; hal tersebut tidak berarti keduanya dijamin tidak berkorelasi pada data.')

heading('2 2 Arsitektur dan Alur Sistem')
paragraph('Backend memakai Django dan SQLite. Pengolahan numerik menggunakan Python, pandas, dan NumPy. Frontend menggunakan template HTML, CSS, serta JavaScript native. Pemisahan modul memungkinkan rumus AHP, TOPSIS, harga tiket, jarak, dan kemiripan diuji secara terpisah dari tampilan.')
paragraph('Alur offline adalah sumber data, preprocessing bersama, ekspor master dan fitur, validasi manifest, impor database, lalu pelatihan K-Means. Manifest menyimpan hash sumber, parameter fitur, daftar ID, serta fingerprint pipeline. Importer dan trainer menolak artefak yang tidak sesuai sumber atau transformasi. Tujuannya mencegah database maupun model memakai hasil preprocessing yang usang.')
paragraph('Alur online dimulai dari validasi formulir. Aplikasi mengambil destinasi pada provinsi tujuan dengan harga sumber yang masih berada dalam batas budget. Sistem menghitung Haversine bagi kandidat yang tiketnya lolos. Filter tidak menambahkan ongkos perjalanan dan tidak menghapus destinasi dari database. Budget Rp0 tetap menerima destinasi gratis. TOPSIS menilai semua kandidat yang lolos tanpa penyaringan berdasarkan cluster.')
paragraph('Peta menampilkan enam provinsi, 443 destinasi dalam daftar, dan 442 titik dalam bingkai visual. Titik Marina tidak ditampilkan pada bingkai Jawa karena koordinatnya berada di luar jangkauan. Filter provinsi dari peta mengisi formulir, sedangkan rekomendasi baru memperbarui kartu hasil dan daftar hasil peta dari snapshot respons yang sama.')

heading('2 3 Perancangan Preprocessing')
paragraph('Sumber yang wajib tersedia adalah CSV destinasi Kaggle, CSV enam kurasi Jawa, catatan pengamatan rating Google Maps, dan CSV interaksi pengguna. Pipeline memeriksa jumlah 437 dan 6 serta ID yang diharapkan sebelum melanjutkan. Nama kolom diubah menjadi snake_case, kolom Unnamed dibuang, whitespace teks dirapikan, dan atribut numerik dikonversi. Nilai sumber yang tidak valid ditandai agar dapat ditinjau.')
paragraph('Normalisasi kategori menghasilkan alam, bahari, belanja, budaya, hiburan, dan religi. Mapping kategori merupakan penyederhanaan label sumber. Istilah Cagar Alam pada dataset tidak otomatis membuktikan status hukum suatu objek. Mapping kota ke provinsi menjaga konsistensi aplikasi tetapi tidak memperluas cakupan data kota tersebut menjadi representasi seluruh provinsi.')
paragraph('Interaksi pengguna yang mempunyai ID kosong atau rating di luar 1 sampai 5 dikeluarkan dari tabel interaksi. Pasangan user_id dan place_id yang berulang menggunakan baris terakhir. Proses tersebut menyisakan 9.597 baris dan menghasilkan mean, count, serta standard deviation per destinasi. Agregasi digabungkan melalui left merge sehingga tidak menghapus enam tambahan yang belum mempunyai interaksi Kaggle. Statistik interaksi bukan pengganti rating destinasi C2.')
paragraph('Imputasi hanya dilakukan pada rating model Tahura. Median dihitung dari 442 rating sumber yang valid dan menghasilkan 4,5. Kolom rating asli tetap kosong dan rating_imputed diberi nilai benar. Time_Minutes tetap boleh kosong. Tidak digunakan dropna umum yang dapat menghilangkan destinasi; retensi 443 ID diperiksa lagi sesudah penggabungan dan sebelum ekspor.')
paragraph('C4 dibentuk dari enam kelompok kata fasilitas: toilet, parkir, makanan, ibadah, aksesibilitas, dan pusat informasi. Pencocokan kata utuh mengurangi kesalahan substring, lalu 16 koreksi konteks menghapus penyebutan yang tidak mengonfirmasi fasilitas objek tersebut. Sebanyak 84 destinasi mempunyai kecocokan keyword awal dan 69 masih mempunyai penyebutan yang diterima setelah koreksi. Nilai nol berarti deskripsi belum memberi bukti yang diterima, bukan fasilitas pasti tidak ada.')
paragraph('Tag aktivitas berasal dari nama, deskripsi, dan sebagian kategori. Sebanyak 370 destinasi mempunyai setidaknya satu tag. Tag bersifat heuristik, sehingga tidak boleh diperlakukan sebagai daftar aktivitas resmi yang telah diaudit. C4 dan tag disimpan bersama catatan asal fitur untuk mendukung penjelasan rekomendasi.')

heading('2 4 Fitur dan Pemilihan Algoritma Data Mining')
paragraph('Fitur K-Means berjumlah delapan: harga sumber yang dibatasi P99 dan distandardisasi, rating model yang distandardisasi, serta enam kolom one-hot kategori. ID hanya identitas, bukan fitur jarak. Provinsi, nama, koordinat, C4, dan agregat interaksi tidak digunakan untuk clustering aktif. Pemilihan ini memisahkan indikator fasilitas yang belum terverifikasi dari pembentukan segmen.')
paragraph('P99 sebesar Rp275.800 membatasi nilai harga hanya pada matriks fitur model. Ada '+str(km['capped_training_rows'])+' baris harga di atas batas ini. Harga Rp900.000, misalnya, menjadi Rp275.800 pada fitur sebelum Z-score, tetapi tetap Rp900.000 pada master dan C1 TOPSIS. P99 mengurangi pengaruh nilai ekstrem, tetapi tidak memperbaiki ketidakjelasan apakah Price merupakan tiket atau paket wisata.')
equation('z = ', 'x − μ', 'σ')
paragraph('Mean dan standard deviation dihitung dengan ddof 0 dari data pelatihan. Parameter harga sesudah pembatasan adalah mean '+number(result.manifest['feature_parameters']['mean'][0],6)+' dan standard deviation '+number(result.manifest['feature_parameters']['scale'][0],6)+'. Untuk rating model, mean '+number(result.manifest['feature_parameters']['mean'][1],6)+' dan standard deviation '+number(result.manifest['feature_parameters']['scale'][1],6)+'. Parameter yang sama diperlukan jika fitur data baru akan dibandingkan dengan model tersimpan.')
paragraph('K-Means digunakan untuk mengelompokkan destinasi tanpa label acuan. Model menghasilkan centroid yang merangkum karakteristik setiap kelompok sehingga hasilnya dapat dijelaskan melalui harga, rating, dan kategori. Evaluasinya menggunakan silhouette, inertia, dan jumlah anggota cluster sesuai tujuan pengelompokan (scikit-learn developers, n.d.).')
caption('Tabel 5 Konfigurasi K Means yang digunakan')
table(['Parameter','Nilai pada implementasi'],[
    ['Data pelatihan','Seluruh 443 destinasi'],
    ['Jumlah fitur','8 fitur numerik hasil transformasi'],
    ['Inisialisasi centroid','k-means++'],
    ['Jumlah inisialisasi','10'],
    ['Seed','42'],
    ['Kandidat jumlah cluster','k = 2 sampai 6'],
    ['Maksimal iterasi','100'],
    ['Toleransi perpindahan centroid','0,000001']], [6,8])
paragraph('K-Means sensitif terhadap skala dan pencilan. Standardisasi menyamakan skala fitur, sedangkan pembatasan harga pada P99 mengurangi pengaruh harga ekstrem pada pelatihan. Nilai harga sumber tetap dipertahankan untuk perhitungan SPK. Centroid dan label segmen merupakan ringkasan data, bukan penilaian bahwa semua anggota cluster memiliki kualitas yang sama.')

heading('2 5 Hasil Evaluasi K Means pada Snapshot Aktif')
paragraph('Implementasi K-Means memakai NumPy dengan konfigurasi pada Tabel 5. Ukuran minimum cluster ditetapkan 22 anggota berdasarkan maksimum antara 5 dan pembulatan 5% dari 443. Semua kandidat pada laporan memenuhi batas tersebut. Konfigurasi terpilih adalah yang mempunyai silhouette terbesar di antara konfigurasi yang layak.')
caption('Tabel 6 Evaluasi jumlah cluster dari laporan model aktif')
table(['k','Silhouette','Inertia','Cluster terkecil'],[[str(c['k']),number(c['silhouette'],5),number(c['inertia'],5),str(c['smallest_cluster'])] for c in km['candidates']], [1.5,4,4.5,4],(0,1,2,3))
caption('Tabel 7 Karakteristik dua segmen terpilih')
table(['Segmen','Anggota','Mean harga sumber','Mean rating model'],[
    ['Segmen 1 harga rendah','414',money(km['clusters'][0]['mean_price']),number(km['clusters'][0]['mean_rating'],3)],
    ['Segmen 2 harga tinggi hiburan','29',money(km['clusters'][1]['mean_price']),number(km['clusters'][1]['mean_rating'],3)]],[4.2,2,4.5,3.3],(1,2,3))
paragraph('Kedua cluster mempunyai rata-rata rating yang hampir sama. Perbedaan yang paling terlihat adalah harga, sementara cluster kedua didominasi hiburan. Label harga rendah dan harga tinggi bersifat relatif terhadap snapshot, bukan batas resmi kategori ekonomi atau premium. Harga rata-rata pada ringkasan segmen memakai harga sumber, sedangkan centroid K-Means dibentuk dari harga yang sudah dibatasi dan distandardisasi. Karena itu, kedua besaran tersebut tidak boleh ditafsirkan sebagai nilai yang sama.')
paragraph('Seluruh 443 destinasi mendapatkan label hasil pelatihan, termasuk keenam tambahan. Silhouette dihitung pada data pelatihan yang sama dan memberi evaluasi internal bentuk kelompok. Hasil pengelompokan menjelaskan kemiripan destinasi; urutan rekomendasi dihitung secara terpisah menggunakan TOPSIS.')

heading('2 6 Alternatif Tindakan')
paragraph('Alternatif tindakan A1, A2, A3, dan seterusnya adalah keputusan untuk mengunjungi destinasi tertentu yang lolos filter pada satu permintaan. A1 bukan nama tetap satu destinasi untuk semua pengguna. Jumlah alternatif berubah mengikuti provinsi dan budget. ID sumber tetap disimpan agar hasil tidak tertukar ketika urutan ranking berubah.')
caption('Tabel 8 Contoh alternatif yang berasal dari data aktif')
table(['Kode contoh','ID','Destinasi','Kategori'],[
    ['A1','438','Taman Hutan Raya Banten','alam'],['A2','439','Museum Multatuli','budaya'],
    ['A3','440','Goa Seplawan','alam'],['A4','441','Pantai Jatimalang','bahari'],
    ['A5','442','Kolam Renang Artha Tirta','hiburan'],['A6','443','Museum Trinil','budaya']],[2.1,1.4,7.7,2.8],(0,1))
paragraph('Tabel tersebut adalah inventaris contoh, bukan satu matriks keputusan lintas provinsi. Pada contoh perhitungan Bab 3, provinsi tujuan adalah Banten sehingga hanya A1 dan A2 yang dibandingkan. Destinasi lainnya tetap berada dalam database dan model, tetapi tidak menjadi kandidat pada permintaan Banten.')

heading('2 7 Kriteria dan Jenis Cost atau Benefit')
caption('Tabel 9 Kriteria keputusan pada website aktif')
table(['Kode','Kriteria','Jenis','Definisi nilai'],[
    ['C1','Harga tiket','Cost','Harga sumber satu destinasi per orang, tanpa cap p99'],
    ['C2','Rating model','Benefit','Rating teramati atau imputasi yang diberi penanda'],
    ['C3','Jarak garis lurus','Cost','Haversine dari kota asal; bukan jarak jalan atau ongkos'],
    ['C4','Indikator fasilitas','Benefit','Jumlah kelompok penyebutan yang diterima dibagi 6'],
    ['C5','Kecocokan kategori','Benefit','Utama 1; sekunder 0,5; kategori lainnya 0'],
    ['C6','Kecocokan hobi','Benefit','Kemiripan Jaccard antara hobi pengguna dan tag destinasi']],[1.4,3.3,2,7.3],(0,2))
paragraph('Kriteria cost mengutamakan nilai lebih kecil, sedangkan benefit mengutamakan nilai lebih besar. Jika kategori utama dan sekunder sama, kondisi utama diperiksa lebih dulu sehingga nilainya 1. Jika hobi tidak dipilih, website menetapkan seluruh C6 menjadi 0, bukan menganggap pengguna cocok sempurna dengan semua destinasi.')
equation('C4 = ', 'jumlah kelompok fasilitas yang diterima', '6')
equation('Jaccard(H,T) = ', '|H ∩ T|', '|H ∪ T|')
paragraph('H adalah himpunan hobi pengguna dan T adalah tag aktivitas destinasi. Nilai Jaccard tidak mengukur kualitas wisata, melainkan kecocokan himpunan aktivitas. Pada fungsi umum, dua himpunan kosong bernilai 1; alur website menangani hobi pengguna kosong secara khusus dengan C6 = 0. Perbedaan konteks ini penting ketika rumus diuji dan ketika hasil dijelaskan.')

heading('2 8 Model Budget Tiket dan Jarak')
paragraph('Budget adalah batas tiket masuk satu destinasi per orang. Tidak ada kewajiban menghabiskan batas tersebut. Tiket gratis tetap dapat menjadi alternatif terbaik meskipun budget besar. Sisa alokasi tiket bukan sisa uang perjalanan karena transportasi, makan dan penginapan tidak dihitung.')
equation('C1 = harga tiket sumber')
equation('Lolos jika harga tiket ≤ budget')
equation('Sisa alokasi tiket = budget − harga tiket')
caption('Tabel 10 Aturan budget dan jarak aplikasi aktif')
table(['Komponen','Aturan','Batas interpretasi'],[
    ['Budget','Minimal Rp0; tiket tidak melampaui batas','Bukan anggaran perjalanan'],
    ['C1','Harga sumber tanpa cap p99','Tarif snapshot perlu dicek'],
    ['C3','Haversine dengan radius 6.371 km','Garis lurus, bukan jalan'],
    ['Sisa tiket','Budget dikurangi harga kandidat','Tidak otomatis untuk belanja'],
    ['Transport, makan, inap','Tidak dihitung','Di luar cakupan']],[3.2,5.5,5.3])
paragraph('Perubahan ini menghilangkan kebutuhan koefisien ongkos yang belum terkalibrasi. Nilai harga sumber tetap perlu diaudit bila merupakan paket, bukan tiket masuk murni. Koordinat kota asal adalah titik representatif, bukan lokasi pengguna yang presisi (Kelompok TravelFit, 2026c).')

heading('2 9 Dasar Bobot dan Pemilihan MCDM')
paragraph('AHP digunakan untuk pembobotan kriteria melalui matriks perbandingan berpasangan, sedangkan TOPSIS digunakan untuk meranking alternatif. Pemisahan ini menghindari kebutuhan membandingkan ratusan destinasi secara berpasangan. AHP membandingkan enam kriteria saja. Bobot diperoleh melalui normalisasi kolom dan rata-rata baris, lalu diuji dengan consistency ratio atau CR. Profil digunakan jika CR kurang dari 0,1 (Saaty, 2008).')
paragraph('Empat profil aktif merupakan preset rancangan pengembang. Bobot Seimbang mengikuti spreadsheet contoh awal dan profil lainnya mengikuti matriks yang ditulis pada profiles.py. CR yang kecil menunjukkan konsistensi internal matriks, bukan bukti bahwa bobot telah mewakili populasi wisatawan. Survei preferensi belum menjadi input bobot aktif.')
caption('Tabel 11 Bobot aktual empat profil dan consistency ratio')
for key,p in profiles.ACTIVE_PROFILES.items():
    paragraph('Profil '+p['label']+' dengan CR '+number(p['cr'],6))
    table(['C1','C2','C3','C4','C5','C6'],[[number(w*100,4)+'%' for w in p['weights']]], [14/6]*6,tuple(range(6)))
paragraph('Slider pada website menormalisasi enam nilai nonnegatif agar jumlah bobot menjadi 1. Ketika slider diubah pengguna, bobot tersebut merupakan bobot langsung kustom, bukan AHP baru. Tidak ada matriks perbandingan baru atau CR baru untuk slider. Jika semua nilai slider nol, aplikasi kembali memakai bobot profil yang dipilih.')
caption('Tabel 12 Metode SPK dan perannya pada TravelFit')
table(['Metode','Fungsi dalam proyek','Penggunaan'],[
    ['AHP','Membuat bobot dan memeriksa konsistensi enam kriteria','Dipakai untuk bobot'],
    ['TOPSIS','Membandingkan jarak ke solusi ideal dan anti-ideal','Dipakai untuk ranking'],
    ['SAW','Pembanding penjumlahan terbobot yang sederhana','Validasi internal, bukan ranking website']],[2.4,7.1,4.5])
paragraph('TOPSIS dipilih karena dapat membandingkan kriteria cost dan benefit dengan langkah normalisasi, pembobotan, solusi ideal, jarak, dan nilai preferensi yang dapat diperiksa. Normalisasi vektor mengikuti implementasi pada topsis.py. SAW digunakan sebagai pembanding internal untuk melihat perbedaan urutan, bukan sebagai bukti bahwa salah satu metode menghasilkan keputusan yang benar secara mutlak (Hwang dan Yoon, 1981).')

heading('2 10 Validasi Data Mining dan Rekomendasi')
paragraph('Validasi data memeriksa jumlah destinasi, keunikan ID, kelengkapan fitur, rentang nilai, sumber yang di-hash, serta konsistensi hasil terhadap transformasi bersama. Validasi model mencoba k 2 sampai 6 dan membandingkan silhouette, inertia, dan ukuran cluster. Hasil numerik pada Tabel 6 menjadi dasar pemilihan jumlah cluster.')
paragraph('Validasi SPK memeriksa jumlah bobot sama dengan 1, CR profil, arah cost dan benefit, langkah TOPSIS, dan pembandingan SAW dengan Spearman. Uji sensitivitas mengubah bobot atau profil pada kandidat yang sama dan mengamati perubahan urutan. Ranking yang stabil belum tentu benar bagi pengguna; ranking yang berubah juga tidak otomatis salah karena perubahan bobot memang menunjukkan perubahan prioritas.')
caption('Tabel 13 Validasi dan bukti implementasi')
table(['Aspek','Cara memeriksa','Status snapshot'],[
    ['Retensi data','ID 1 sampai 443 lengkap dan unik','Terpenuhi pada manifest dan keluaran'],
    ['Clustering','k 2 sampai 6 dan silhouette serta inertia','Hasil numerik tersedia'],
    ['AHP','Normalisasi bobot dan CR kurang dari 0,1','Empat profil lolos'],
    ['TOPSIS','Perhitungan manual dan edge case','Modul dan tes tersedia'],
    ['Pembanding SPK','SAW dan korelasi ranking Spearman','Modul validasi tersedia'],
    ['Integrasi website','Preprocessing sampai rekomendasi dan peta','188 tes lulus pada 5 Oktober 2026'],
    ['Penanda kualitas data','Konflik koordinat dan rating kosong','Marina dan Tahura ditandai']],[3.2,5.5,5.3])
paragraph('Pengujian ulang pada 5 Oktober 2026 menghasilkan 188 tes lulus. Pengujian mencakup budget Rp0, tepat batas tiket, kota asal jauh, dan tidak adanya routing eksternal pada rekomendasi. Tes tidak memverifikasi tarif lapangan atau membuktikan kepuasan pengguna. Catatan 30 September tetap menjadi bukti historis integrasi awal (Kelompok TravelFit, 2026c; 2026d).')

chapter('BAB 3 BUKTI PERHITUNGAN DAN PEMAHAMAN MODEL SPK')
heading('3 1 Berkas Bukti dan README')
paragraph('README menjelaskan pipeline dan aplikasi, sedangkan dokumentasi sumber mencatat bukti serta keterbatasan atribut. Excel aktif memuat seluruh 443 destinasi dan formula AHP–TOPSIS untuk contoh Bandung–Jawa Barat. Bab ini menggunakan dua destinasi Banten agar semua langkah angka dapat dibaca lengkap. Input kedua contoh berbeda, tetapi C1 tiket dan C3 Haversine memakai definisi yang sama dengan website.')
link('Buka README proyek di repository',repo('README.md'))
link('Buka Excel aktif AHP TOPSIS TravelFit','../excel_spk_20261005/Perhitungan_AHP_TOPSIS_TravelFit.xlsx')
link('Buka dokumentasi sumber data aktif',repo('Dokumentasi.md'))
link('Buka evaluasi K Means pada repository',repo('reports/clustering/kmeans_evaluation.json'))
paragraph('Excel aktif berada di folder outputs/excel_spk_20261005. Tautan file menggunakan lokasi relatif terhadap laporan ini; pertahankan susunan folder saat dibagikan. Snapshot codebase laporan adalah commit '+head+' dengan manifest java443-v1. Tautan repository mengikuti versi yang sudah diunggah.')

heading('3 2 Skenario Perhitungan dari Snapshot Aplikasi')
paragraph('Contoh perhitungan menggunakan kota asal Serang, provinsi Banten, budget tiket Rp10.000, kategori utama alam, sekunder budaya, profil Hemat dan tanpa hobi. Kedua destinasi lolos karena tiket Rp8.000 dan Rp2.000 tidak melampaui batas. Budget adalah input contoh, bukan rekomendasi anggaran perjalanan. Tidak ada moda atau durasi dalam pembentukan C1.')
paragraph('Koordinat asal pada daftar kota adalah latitude -6,15 dan longitude 106,05. Jarak garis lurus Haversine adalah '+number(provenance[0]['distance'],6)+' km menuju Tahura dan '+number(provenance[1]['distance'],6)+' km menuju Museum Multatuli. Jarak dihitung langsung dari koordinat dengan radius bumi 6.371 km, tanpa faktor 1,3. Perhitungan tidak meminta jaringan atau mengubah cache dan bukan jarak jalan.')
caption('Tabel 14 Data alternatif Banten yang digunakan')
table(['Kode dan ID','Destinasi','Harga sumber','Rating model'],[
    ['A1 438','Taman Hutan Raya Banten','Rp8.000','4,5 imputasi'],
    ['A2 439','Museum Multatuli','Rp2.000','4,6 teramati']],[2.2,6.1,2.8,2.9])
paragraph('Kedua destinasi mempunyai C4 = 0 pada pipeline deskripsi aktif. Ini menunjukkan tidak adanya penyebutan fasilitas yang diterima, bukan fasilitasnya pasti tidak tersedia. Tahura mempunyai tag edukasi, sedangkan Museum Multatuli mempunyai budaya, edukasi, dan sejarah. Karena hobi tidak dipilih pada skenario, seluruh C6 bernilai 0.')

heading('3 3 Pembuktian Bobot AHP')
matrix=profiles.matrix_from_upper(profiles.PROFILE_UPPERS['hemat'])
ahp_w=ahp.weights_from_matrix(matrix)
consistency=ahp.consistency(matrix,ahp_w)
caption('Tabel 15 Matriks perbandingan berpasangan profil Hemat')
table(['Kriteria','C1','C2','C3','C4','C5','C6'],[[f'C{i+1}']+[number(v,4) for v in row] for i,row in enumerate(matrix)],[2.2]+[11.8/6]*6,tuple(range(7)))
paragraph('Nilai C1 terhadap C2 sebesar 4 berarti rancangan profil memberi kepentingan biaya empat kali rating pada pasangan tersebut. Nilai arah sebaliknya adalah 1 dibagi 4 atau 0,25. Diagonal bernilai 1 karena sebuah kriteria dibandingkan dengan dirinya sendiri. Semua nilai merupakan konfigurasi preset yang dapat diaudit pada profiles.py.')
equation('nᵢⱼ = ', 'aᵢⱼ', 'Σᵢ aᵢⱼ')
equation('wᵢ = ', 'Σⱼ nᵢⱼ', '6')
colsum=np.array(matrix).sum(axis=0)
paragraph('Jumlah kolom C1 sampai C6 adalah '+', '.join(number(v,6) for v in colsum)+'. Sebagai contoh, normalisasi elemen C1 terhadap C1 adalah 1 dibagi '+number(colsum[0],6)+' = '+number(1/colsum[0],6)+'. Rata-rata enam nilai pada baris C1 menghasilkan bobot '+number(ahp_w[0],9)+'.')
caption('Tabel 16 Bobot Hemat hasil perhitungan kode')
table(['Kriteria','Bobot','Persentase'],[[f'C{i+1}',number(w,9),number(w*100,4)+'%'] for i,w in enumerate(ahp_w)]+[['Jumlah',number(sum(ahp_w),9),'100,0000%']],[4,5,5],(0,1,2))
equation('CI = ', 'λmaks − n', 'n − 1')
equation('CR = ', 'CI', 'RI')
paragraph('Hasil uji konsistensi adalah lambda maksimum '+number(consistency['lambda_max'],9)+', CI '+number(consistency['ci'],9)+', dan RI untuk enam kriteria sebesar 1,24. CR = '+number(consistency['cr'],9)+' sehingga kurang dari 0,1. Artinya, matriks preset Hemat memenuhi aturan konsistensi internal yang diterapkan aplikasi. Hasil ini tidak membuktikan adanya responden yang memilih bobot tersebut.')

heading('3 4 Pembuktian Harga Tiket C1')
for index,(row,cost) in enumerate(zip(banten.itertuples(),costs),1):
    heading('Alternatif A'+str(index),3)
    paragraph('Harga tiket sumber '+money(row.price)+' menjadi C1 secara langsung. Dengan budget Rp10.000, sisa alokasi tiket = Rp10.000 dikurangi '+money(row.price)+' = '+money(cost['sisa'])+'. Jarak garis lurus '+number(decision[index-1][2],6)+' km hanya menjadi C3, tidak menambah harga tiket.')
caption('Tabel 17 Harga tiket dan sisa alokasi skenario Banten')
table(['Kode','Tiket C1','Sisa alokasi tiket','C3 garis lurus km'],[[f'A{i+1}',number(c['tiket'],0),number(c['sisa'],0),number(decision[i][2],6)] for i,c in enumerate(costs)],[2,3.5,4.5,4],tuple(range(4)))
paragraph('Museum Multatuli lebih murah, sedangkan perbedaan jarak, rating dan kategori diperhitungkan bersamaan oleh TOPSIS. Sisa tiket tidak menjadi kriteria tambahan dan tidak ditambahkan sebagai manfaat kedua dari harga murah.')

heading('3 5 Matriks Keputusan dan Normalisasi TOPSIS')
caption('Tabel 18 Matriks keputusan skenario aktif')
table(['A','C1 rupiah','C2','C3 km','C4','C5','C6'],[[f'A{i+1}',number(row[0],2),number(row[1],1),number(row[2],6),number(row[3],1),number(row[4],1),number(row[5],1)] for i,row in enumerate(decision)],[1,3.3,1.5,3.5,1.5,1.7,1.5],tuple(range(7)))
paragraph('C1 dan C3 adalah cost. C2, C4, C5, dan C6 adalah benefit. Pada skenario ini C4 dan C6 tidak membedakan alternatif karena kedua kolom semuanya nol. Kriteria tersebut tetap dicatat pada matriks, tetapi tidak menyumbang perbedaan jarak terhadap solusi ideal.')
equation('rᵢⱼ = ', 'xᵢⱼ', '√(Σᵢ xᵢⱼ²)')
paragraph('Penyebut normalisasi C1 sampai C6 adalah '+', '.join(number(v,6) for v in den)+'. Ketika penyebut suatu kolom nol, implementasi menetapkan nilai normalisasi kolom itu menjadi nol agar tidak terjadi pembagian dengan nol.')
caption('Tabel 19 Matriks normalisasi R')
table(['A','C1','C2','C3','C4','C5','C6'],[[f'A{i+1}']+[number(v,6) for v in row] for i,row in enumerate(R)],[1.4]+[2.1]*6,tuple(range(7)))
equation('vᵢⱼ = wⱼ × rᵢⱼ')
caption('Tabel 20 Matriks normalisasi terbobot V')
table(['A','C1','C2','C3','C4','C5','C6'],[[f'A{i+1}']+[number(v,6) for v in row] for i,row in enumerate(V)],[1.4]+[2.1]*6,tuple(range(7)))
paragraph('Bobot yang digunakan adalah nilai penuh profil Hemat dari AHP, bukan persentase yang sudah dibulatkan pada kartu website. Nilai pada tabel dibulatkan enam desimal hanya untuk keterbacaan. Pembuktian hasil akhir menggunakan presisi penuh sehingga perbedaan pembulatan manual kecil tidak dianggap perubahan metode.')

heading('3 6 Solusi Ideal Jarak dan Ranking')
paragraph('Untuk setiap cost, solusi ideal positif mengambil nilai terbobot minimum, sedangkan ideal negatif mengambil maksimum. Untuk benefit berlaku sebaliknya. Solusi ideal terbentuk dari nilai terbaik setiap kriteria pada kandidat yang lolos, bukan satu destinasi nyata yang harus mempunyai semua nilai terbaik sekaligus.')
caption('Tabel 21 Vektor ideal positif dan negatif')
table(['Vektor','C1','C2','C3','C4','C5','C6'],[['A positif']+[number(v,6) for v in pos],['A negatif']+[number(v,6) for v in neg]],[2.2]+[11.8/6]*6,tuple(range(7)))
equation('Dᵢ⁺ = √(Σⱼ (vᵢⱼ − Aⱼ⁺)²)')
equation('Dᵢ⁻ = √(Σⱼ (vᵢⱼ − Aⱼ⁻)²)')
equation('Vᵢ = ', 'Dᵢ⁻', 'Dᵢ⁺ + Dᵢ⁻')
caption('Tabel 22 Hasil akhir perhitungan TOPSIS')
table(['Peringkat','Alternatif','D positif','D negatif','V preferensi'],[[str(i+1),'A'+str(r['idx']+1),number(r['d_pos'],9),number(r['d_neg'],9),number(r['vi'],9)] for i,r in enumerate(rank)],[2.5,2.3,3,3,3.2],tuple(range(5)))
best=banten.iloc[rank[0]['idx']]
paragraph('Alternatif dengan nilai preferensi terbesar adalah '+best.place_name+'. Hasil ini berlaku untuk kota asal Serang, profil Hemat, kandidat Banten, dan parameter pada skenario. Nilai C5 yang lebih tinggi serta posisi pada kriteria cost dan rating menjelaskan perbandingan, tetapi tidak boleh diubah menjadi klaim bahwa destinasi tersebut selalu lebih baik untuk semua wisatawan.')
paragraph('TOPSIS membandingkan alternatif yang tersedia. Bila hanya satu kandidat lolos atau seluruh kandidat identik, kode memberikan V = 1 untuk menghindari pembagian nol. Nilai 1 pada keadaan tersebut bukan bukti kualitas sempurna; tidak ada pembanding yang membedakan alternatif. Bila tidak ada kandidat lolos, website menampilkan pesan dan mengosongkan hasil lama.')

heading('3 7 Pembanding SAW dan Sensitivitas')
caption('Tabel 23 Hasil SAW pada matriks keputusan yang sama')
table(['Peringkat','Alternatif','Skor SAW'],[[str(i+1),'A'+str(idx+1),number(score,9)] for i,(idx,score) in enumerate(saw)],[3,4,7],(0,1,2))
paragraph('Korelasi Spearman antara urutan TOPSIS dan SAW pada dua alternatif ini adalah '+number(rho,6)+'. Korelasi hanya menggunakan dua alternatif sehingga tidak cukup untuk menyimpulkan kesesuaian metode pada seluruh 443 destinasi. SAW juga mempunyai skala skor yang berbeda dari V TOPSIS, sehingga skor kedua metode tidak dibandingkan sebagai besaran yang identik.')
caption('Tabel 24 Uji profil pada kandidat Banten yang sama')
sensitivity=[]
for key,p in profiles.ACTIVE_PROFILES.items():
    rr=topsis.rank(decision,p['weights'],profiles.IS_COST)
    vals={item['idx']:item['vi'] for item in rr}
    sensitivity.append([p['label'],number(vals[0],6),number(vals[1],6),'A'+str(rr[0]['idx']+1)])
table(['Profil','V A1','V A2','Peringkat pertama'],sensitivity,[3.4,3.3,3.3,4],(1,2,3))
paragraph('Tabel sensitivitas dihitung ulang dari matriks kandidat Banten yang sama dengan empat bobot preset. Hasilnya memperlihatkan dampak perubahan prioritas pada skenario tersebut. C4 dan C6 bernilai konstan pada kedua kandidat sehingga tidak membedakan peringkat dalam contoh ini.')

heading('3 8 Reproduksi Perhitungan dan Keterbatasan')
paragraph('Pipeline produksi direproduksi dengan urutan preprocess_destinations, import_destinations, lalu train_clusters. Notebook preprocessing menjelaskan pembersihan dan pembentukan fitur. Fungsi bersama pada data_pipeline.py menjaga konsistensi transformasi, sedangkan manifest dan fingerprint memeriksa kesesuaian data olahan dengan sumber sebelum impor dan pelatihan.')
paragraph('Untuk pemeriksaan rumus, gunakan fungsi weights_from_matrix dan consistency pada ahp.py, rank pada topsis.py, serta saw_rank dan spearman pada validation.py. Perhitungan Bab 3 memakai Haversine dan harga asli. Identitas, harga, rating imputasi, dan koordinat tidak diubah demi menyesuaikan peringkat. Hasilnya juga diperiksa terhadap view Django dengan input skenario yang sama.')
paragraph('Pemahaman model yang perlu dipertahankan adalah perbedaan segmentasi dan rekomendasi, harga sumber dan budget tiket, rating asli dan rating model, serta indikator deskripsi dan fakta fasilitas. Keterbatasan utama tetap berupa representasi geografis yang tidak merata, kemungkinan harga paket bercampur tiket, konflik koordinat Marina, imputasi rating Tahura, serta ketidakpastian tarif terkini. Sistem merupakan alat bantu perbandingan dengan batasan yang terlihat, bukan pengganti verifikasi sebelum perjalanan.')

chapter('BAB 4 LOGBOOK DAN JADWAL KEGIATAN')
heading('4 1 Logbook Harian')
paragraph('Logbook digunakan untuk mencatat aktivitas nyata dengan satu aktivitas pada satu baris. Tanggal, anggota, uraian pekerjaan, tools, hasil, kendala, dan tindak lanjut diisi setelah kegiatan dilakukan. Tabel berikut disediakan kosong.')
caption('Tabel 25 Template logbook kegiatan')
t=table(['No','Tanggal','Anggota','Detail pekerjaan','Tools AI','Hasil','Kendala','Tindak lanjut'],[['']*8 for _ in range(12)],[0.95,1.95,1.95,2.55,1.4,1.35,1.95,1.9])
for row in t.rows[1:]:
    row.height=Cm(1.15)

heading('4 2 Jadwal Kegiatan dari Awal sampai Implementasi')
paragraph('Jadwal berikut menunjukkan rentang rekam kegiatan pada riwayat commit repository dari 1 September sampai 1 Oktober 2026. Rentang bar memperlihatkan tanggal pertama dan terakhir bukti terkait, bukan jam kerja atau bukti bahwa kegiatan dilakukan terus-menerus setiap hari. Tahapan kegiatan mencakup perencanaan, preprocessing, penerapan metode, website, dan integrasi data Java443.')
schedule=[('Perencanaan awal',date(2026,9,1),date(2026,9,1)),
          ('Prototipe peta',date(2026,9,4),date(2026,9,4)),
          ('Kerangka CRISP DM',date(2026,9,9),date(2026,9,9)),
          ('Metode dan rumus',date(2026,9,16),date(2026,9,17)),
          ('Preprocessing awal',date(2026,9,20),date(2026,9,25)),
          ('SPK dan website',date(2026,9,25),date(2026,9,29)),
          ('Integrasi Java443',date(2026,9,30),date(2026,9,30)),
          ('Pembaruan notebook',date(2026,10,1),date(2026,10,1))]
canvas=Image.new('RGB',(1800,1140),'white')
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/times.ttf',48)
small=ImageFont.truetype('C:/Windows/Fonts/times.ttf',42)
x0,x1,y0,step=610,1750,160,108
start=date(2026,9,1); span=31
def xpos(d):return x0+(d-start).days/span*(x1-x0)
for tick in [date(2026,9,1),date(2026,9,9),date(2026,9,16),date(2026,9,25),date(2026,10,1)]:
    x=xpos(tick);draw.line((x,130,x,1010),fill='#D9D9D9',width=2)
    draw.text((x-50,65),tick.strftime('%d/%m'),font=small,fill='black')
for i,(label,a,b) in enumerate(schedule):
    y=y0+i*step
    draw.text((15,y),label,font=font,fill='black')
    xa,xb=xpos(a),xpos(b)+max(22,(x1-x0)/span)
    draw.rectangle((xa,y+10,min(xb,x1),y+58),fill='#5E6570')
draw.text((15,1060),'Tanggal commit tahun 2026',font=font,fill='black')
chart=BUILD/'jadwal.png';canvas.save(chart)
caption('Gambar 1 Bar chart jadwal berdasarkan rekam commit')
p=paragraph(align=WD_ALIGN_PARAGRAPH.CENTER);run=p.add_run();run.add_picture(str(chart),width=Cm(14))
inline=run._r.xpath('.//wp:docPr')
if inline:inline[0].set('descr','Bar chart delapan kegiatan proyek dari 1 September sampai 1 Oktober 2026 berdasarkan riwayat commit')
caption('Tabel 26 Rentang kegiatan dan bukti tanggal')
table(['Kegiatan','Tanggal awal dan akhir','Bukti repository'],[
    ['Perencanaan awal','1 September 2026','Initial plan dan initial commit'],
    ['Prototipe peta','4 September 2026','First Version Map dan Zoom Feature'],
    ['Kerangka CRISP DM','9 September 2026','Commit penambahan CRISP-DM'],
    ['Metode dan rumus','16 sampai 17 September 2026','Method Update dan contoh perhitungan'],
    ['Preprocessing awal','20 sampai 25 September 2026','Update drive path dan notebook'],
    ['SPK dan website','25 sampai 29 September 2026','Django, AHP, TOPSIS, dan integrasi perhitungan'],
    ['Integrasi Java443','30 September 2026','Data, impor, model, UI, peta, dan verifikasi'],
    ['Pembaruan notebook','1 Oktober 2026','Notebook update pada riwayat repository']],[4.1,4.5,5.4])

heading('4 3 Status Implementasi Project')
paragraph('Implementasi lokal sudah mencakup pengolahan 443 destinasi, pelabelan K-Means, empat profil AHP, TOPSIS, formulir preferensi, batas tiket, dan peta Jawa. Peringkat dipublikasikan bersama rincian yang membantu pembaca melihat penyebab suatu alternatif lebih dekat dengan nilai ideal. Sumber dan catatan kualitas ditampilkan agar hasil tidak terlepas dari kondisi data.')
paragraph('Jika sumber data berubah, preprocessing, impor, dan model harus diperbarui dalam urutan yang sama. Manifest dan fingerprint menjaga keterlacakan snapshot, tetapi bukan jaminan bahwa sumber eksternal selalu benar. Dengan pencatatan tersebut, perubahan angka dapat dijelaskan sebagai pembaruan sumber atau parameter, bukan perubahan tanpa bukti.')

chapter('DAFTAR PUSTAKA')
refs=[
    ('aprabowo (n.d.) Indonesia Tourism Destination. Kaggle. Tersedia pada: https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination (Diakses: 1 Oktober 2026).'),
    ('Hwang, C.L. dan Yoon, K. (1981) Multiple Attribute Decision Making Methods and Applications A State of the Art Survey. Berlin: Springer. doi: 10.1007/978-3-642-48318-9.'),
    ('IBM (n.d.) CRISP-DM Help Overview. IBM SPSS Modeler. Tersedia pada: https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview (Diakses: 1 Oktober 2026).'),
    ('Kelompok TravelFit (2026a) TravelFit Rekomendasi Destinasi Wisata Jawa dan evaluasi K-Means Java443. Repository proyek, branch new, snapshot commit '+head+'. Tersedia pada: '+REPO_URL+' (Diakses lokal: '+ACCESS+').'),
    ('Kelompok TravelFit (2026b) Dokumentasi data aktif TravelFit Java443. Dokumentasi.md dan dokumentasi kurasi gabungan Jawa. Tersedia pada: '+repo('Dokumentasi.md')+' (Diakses: 1 Oktober 2026).'),
    ('Kelompok TravelFit (2026c) Keputusan budget tiket dan implementasi rekomendasi. docs/decisions/2026-10-05-ticket-budget.md dan recommender/views.py. Tersedia pada: '+repo('docs/decisions/2026-10-05-ticket-budget.md')+' (Diakses lokal: 5 Oktober 2026).'),
    ('Kelompok TravelFit (2026d) Verifikasi integrasi Java443 30 September 2026. reports/java443_final_verification.md. Tersedia pada: '+repo('reports/java443_final_verification.md')+' (Diakses: 1 Oktober 2026).'),
    ('OpenStreetMap Foundation (n.d.) Copyright and License. Tersedia pada: https://www.openstreetmap.org/copyright (Diakses: 1 Oktober 2026).'),
    ('Pemerintah Kabupaten Lebak (2025) Peraturan Daerah Kabupaten Lebak Nomor 1 Tahun 2025. Lampiran tarif Museum Multatuli, hlm. 232. Tersedia pada: https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Kabupaten Ngawi (2023) Peraturan Daerah Kabupaten Ngawi Nomor 10 Tahun 2023 tentang Pajak Daerah dan Retribusi Daerah. Lampiran II tarif Museum Trinil, hlm. 122 PDF. Tersedia pada: https://jdih.ngawikab.go.id/peraturan/view/526 (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Kabupaten Purworejo (2026) Peraturan Daerah Kabupaten Purworejo Nomor 1 Tahun 2026. Lampiran tarif destinasi wisata, hlm. 242. Tersedia pada: https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Pemerintah Provinsi Banten (2024) Peraturan Daerah Provinsi Banten Nomor 1 Tahun 2024. Lampiran tarif Tahura, hlm. 261. Tersedia pada: https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf (Diakses untuk kurasi: 30 September 2026).'),
    ('Saaty, T.L. (2008) Decision making with the analytic hierarchy process. International Journal of Services Sciences, 1(1), hlm. 83-98. doi: 10.1504/IJSSCI.2008.017590.'),
    ('scikit-learn developers (n.d.) Clustering. scikit-learn documentation. Tersedia pada: https://scikit-learn.org/stable/modules/clustering.html (Diakses: 1 Oktober 2026).')]
for ref in refs:
    p=paragraph(ref);p.paragraph_format.left_indent=Cm(0.8);p.paragraph_format.first_line_indent=Cm(-0.8)
    p.paragraph_format.space_after=Pt(8)
    p.paragraph_format.keep_together=True

# Verify typography, margins, links and snapshot without mutating existing files.
doc.core_properties.title='Laporan UTS TravelFit Rekomendasi Destinasi Wisata Jawa'
doc.core_properties.subject='SPK dan Data Mining dengan CRISP DM K Means serta AHP TOPSIS'
doc.core_properties.author='Kelompok TravelFit'
doc.core_properties.keywords='UTS, TravelFit, Java443, CRISP-DM, AHP, TOPSIS, K-Means'
doc.save(DEST)
after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in protected}
assert before==after, 'Existing production files changed unexpectedly.'
print(json.dumps({'docx':str(DEST),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),
                  'dataset_rows':len(df),'scenario_rank':[banten.iloc[r['idx']].place_name for r in rank],
                  'scenario_vi':[r['vi'] for r in rank],'source_files_unchanged':before==after},ensure_ascii=False))
