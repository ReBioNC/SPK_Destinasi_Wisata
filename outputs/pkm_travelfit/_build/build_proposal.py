"""Bangun Proposal PKM-KC TravelFit dengan format template Proposal-PKM-KC.docx.

Pemakaian:
    python build_proposal.py <template.docx> [pages.json]

Style, numbering, header/footer dan ukuran halaman disalin dari template; hanya
isi badan dokumen, gambar dan properti dokumen yang diganti. pages.json (hasil
measure_pages.ps1) mengisi nomor halaman daftar isi/gambar/tabel/lampiran.
"""

import json
import re
import struct
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parent / "Proposal_PKM_KC_TravelFit.docx"
TITLE = ("APLIKASI WEB PENDUKUNG KEPUTUSAN BERBASIS AHP DAN TOPSIS DENGAN SEGMENTASI "
         "K-MEANS UNTUK REKOMENDASI DESTINASI WISATA DI PULAU JAWA")
IMAGES = {  # rId template -> (berkas baru, judul gambar)
    "rId10": ("gambar1_tahapan.png", "Gambar 1. Tahapan pelaksanaan PKM-KC"),
    "rId11": ("gambar2_arsitektur.png", "Gambar 2. Arsitektur sistem TravelFit"),
    "rId12": ("gambar3_hasil.png", "Gambar 3. Tampilan hasil rekomendasi pada prototipe"),
    "rId13": ("gambar4_bobot.png", "Gambar 4. Bobot AHP hasil kuesioner dibanding rancangan awal"),
}

FONT = ('<w:rFonts w:ascii="Times New Roman" w:cs="Times New Roman" '
        'w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"/>')
BORDER = ('<w:tcBorders><w:top w:val="single" w:color="000000" w:sz="4"/><w:left w:val="single" '
          'w:color="000000" w:sz="4"/><w:bottom w:val="single" w:color="000000" w:sz="4"/>'
          '<w:right w:val="single" w:color="000000" w:sz="4"/></w:tcBorders>')
CELL_MAR = ('<w:tcMar><w:top w:type="dxa" w:w="50"/><w:left w:type="dxa" w:w="90"/>'
            '<w:bottom w:type="dxa" w:w="50"/><w:right w:type="dxa" w:w="90"/></w:tcMar>')
TABLE_BORDERS = ('<w:tblBorders><w:top w:val="single" w:color="auto" w:sz="4"/><w:left w:val="single" '
                 'w:color="auto" w:sz="4"/><w:bottom w:val="single" w:color="auto" w:sz="4"/>'
                 '<w:right w:val="single" w:color="auto" w:sz="4"/><w:insideH w:val="single" '
                 'w:color="auto" w:sz="4"/><w:insideV w:val="single" w:color="auto" w:sz="4"/></w:tblBorders>')
TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|⟦[^⟧]*⟧)")


def run(text, bold=False, italic=False, highlight=False, size=None, bold_off=False):
    props = FONT
    if bold:
        props += "<w:b/><w:bCs/>"
    elif bold_off:
        props += '<w:b w:val="false"/><w:bCs w:val="false"/>'
    if italic:
        props += "<w:i/><w:iCs/>"
    if highlight:
        props += '<w:highlight w:val="yellow"/><w:highlightCs w:val="yellow"/>'
    if size:
        props += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def runs(text, size=None):
    """**tebal**, *miring*, ⟦isian⟧ (tebal + stabilo kuning seperti template)."""
    out = []
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**"):
            out.append(run(part[2:-2], bold=True, size=size))
        elif part.startswith("⟦"):
            out.append(run(part, bold=True, highlight=True, size=size))
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append(run(part[1:-1], italic=True, size=size))
        else:
            out.append(run(part, size=size))
    return "".join(out)


def para(text, ppr):
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs(text)}</w:p>"


BODY_PPR = '<w:keepNext w:val="false"/><w:spacing w:after="100" w:line="276"/><w:jc w:val="both"/>'


def body(text):
    return para(text, BODY_PPR)


def ref(text):
    return para(text, '<w:keepNext w:val="false"/><w:spacing w:after="100" w:line="276"/>'
                      '<w:ind w:left="720" w:hanging="720"/><w:jc w:val="both"/>')


def heading(text, level):
    return f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/></w:pPr>{run(text)}</w:p>'


def item(text, num_id):
    return para(text, f'<w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/>'
                      f'<w:numId w:val="{num_id}"/></w:numPr><w:spacing w:after="40" w:line="276"/>')


def table_caption(text):
    return para(text, '<w:keepNext/><w:spacing w:after="100" w:line="276"/><w:jc w:val="both"/>')


def figure_caption(text):
    return (f'<w:p><w:pPr><w:spacing w:after="200"/><w:jc w:val="center"/></w:pPr>'
            f'{run(text, size=22)}</w:p>')


def empty():
    return f"<w:p><w:pPr>{BODY_PPR}</w:pPr></w:p>"


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def png_size(path):
    data = path.read_bytes()[16:24]
    return struct.unpack(">II", data)


def figure(rid, doc_id, width_emu=5040000):
    name, caption = IMAGES[rid]
    w, h = png_size(HERE / "img" / name)
    cx, cy = width_emu, round(width_emu * h / w)
    pic = (f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
           f'<pic:cNvPr id="0" name="{name}" descr=""/><pic:cNvPicPr><a:picLocks noChangeAspect="1" '
           f'noChangeArrowheads="1"/></pic:cNvPicPr></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}" '
           f'cstate="none"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
           f'<pic:spPr bwMode="auto"><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>')
    drawing = (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" '
               f'cy="{cy}"/><wp:effectExtent t="0" r="0" b="0" l="0"/><wp:docPr id="{doc_id}" '
               f'name="{name}" descr="{escape(caption)}" title="{escape(caption)}"/><wp:cNvGraphicFramePr>'
               f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
               f'noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic '
               f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData '
               f'uri="http://schemas.openxmlformats.org/drawingml/2006/picture">{pic}</a:graphicData>'
               f'</a:graphic></wp:inline></w:drawing>')
    return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:after="60" w:before="120"/><w:jc w:val="center"/>'
            f'</w:pPr><w:r>{drawing}</w:r></w:p>' + figure_caption(caption))


def cell(text, width, header=False, bold=False):
    shade = '<w:shd w:fill="E7E6E6" w:color="auto" w:val="clear"/>' if header else ""
    content = (run(text, bold=True, size=20) if (header or bold) and text else runs(text, size=20)) if text else ""
    return (f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{width}"/>{BORDER}{shade}{CELL_MAR}</w:tcPr>'
            f'<w:p><w:pPr><w:spacing w:after="0" w:before="0"/></w:pPr>{content}</w:p></w:tc>')


def table(widths, rows, bold_rows=()):
    assert sum(widths) == 7937, sum(widths)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = [f'<w:tbl><w:tblPr><w:tblW w:type="dxa" w:w="7937"/>{TABLE_BORDERS}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>']
    for index, row in enumerate(rows):
        assert len(row) == len(widths), row
        head = index == 0
        trpr = "<w:trPr><w:tblHeader/></w:trPr>" if head else ""
        out.append(f"<w:tr>{trpr}" + "".join(
            cell(text, width, header=head, bold=index in bold_rows) for text, width in zip(row, widths)) + "</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


# --- Daftar isi/gambar/tabel/lampiran (nomor halaman dari pages.json) ---------
def toc_title(text):
    return (f'<w:p><w:pPr><w:spacing w:after="240" w:before="0"/><w:jc w:val="center"/></w:pPr>'
            f'{run(text, bold=True, size=24)}</w:p>')


def toc_entry(text, page, level=1):
    indent = 0 if level == 1 else 360
    label = run(text, bold=True, size=24) if level == 1 else run(text, size=24, bold_off=True)
    return (f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="7937" w:leader="dot"/></w:tabs>'
            f'<w:spacing w:after="40" w:line="276"/><w:ind w:left="{indent}"/></w:pPr>{label}'
            f'{run(chr(9) + str(page), size=24)}</w:p>')


def toc_plain(text, page):
    return (f'<w:p><w:pPr><w:tabs><w:tab w:val="right" w:pos="7937" w:leader="dot"/></w:tabs>'
            f'<w:spacing w:after="40" w:line="276"/><w:ind w:left="0"/></w:pPr>'
            f'{run(text, size=24, bold_off=True)}{run(chr(9) + str(page), size=24)}</w:p>')


# --- Isi proposal --------------------------------------------------------------
def content():
    b = []
    add = b.append
    add(heading("BAB 1. PENDAHULUAN", 1))
    add(heading("1.1 Latar Belakang", 2))
    add(body("Pulau Jawa memiliki enam provinsi dengan ragam destinasi wisata alam, budaya, bahari, religi, "
             "belanja, dan hiburan. Saat memilih tujuan, wisatawan menimbang beberapa hal sekaligus: harga tiket "
             "masuk, ulasan pengunjung, jarak dari kota asal, fasilitas, serta kecocokan dengan minat dan hobi. "
             "Informasi tersebut tersebar di berbagai situs dan aplikasi yang umumnya mengurutkan tempat menurut "
             "satu ukuran, seperti popularitas, rating, atau kedekatan. Akibatnya, wisatawan tetap harus "
             "menimbang sendiri ketika kriteria saling bertentangan, misalnya destinasi dengan rating tinggi "
             "tetapi jauh dan mahal."))
    add(body("Dataset publik Indonesia Tourism Destination (aprabowo, t.t.) memuat 437 destinasi di lima kota "
             "Jawa: Jakarta, Yogyakarta, Bandung, Semarang, dan Surabaya. Tim menambahkan enam destinasi hasil "
             "kurasi di Banten, Jawa Tengah, dan Jawa Timur yang tarifnya diambil dari peraturan daerah dan "
             "lokasinya dari OpenStreetMap, sehingga total data menjadi 443 destinasi. Analisis awal menunjukkan "
             "bahwa 137 destinasi (30,9%) bertiket gratis, harga tiket berkisar Rp0 sampai Rp900.000, dan "
             "kelengkapan deskripsi fasilitas tidak seragam. Karakteristik ini menuntut metode penilaian yang "
             "tetap stabil ketika banyak nilai bernilai nol dan kriteria cost serta benefit bercampur."))
    add(body("Kuesioner perbandingan berpasangan kepada 28 responden juga menunjukkan bahwa kecocokan kategori "
             "wisata (26,0%) dan kecocokan hobi (23,2%) lebih diutamakan daripada harga tiket (16,1%), "
             "sedangkan jarak menjadi pertimbangan terendah (7,9%). Artinya, rekomendasi wisata perlu menilai "
             "minat pribadi, bukan hanya murah atau populer. Sistem pendukung keputusan multikriteria, yaitu "
             "Analytic Hierarchy Process (AHP) untuk pembobotan (Saaty, 2008) dan TOPSIS untuk pemeringkatan "
             "(Hwang dan Yoon, 1981), menyediakan kerangka yang dapat ditelusuri langkah demi langkah."))
    add(heading("1.2 Rumusan Masalah dan Inspirasi", 2))
    add(body("Karya ini terinspirasi dari pengalaman anggota tim saat merencanakan perjalanan dan dari hasil "
             "kuesioner di atas. Masalah yang dijawab adalah bagaimana membangun alat bantu yang (1) menyaring "
             "destinasi sesuai provinsi tujuan dan batas harga tiket; (2) menilai setiap destinasi pada enam "
             "kriteria sekaligus dengan bobot yang berasal dari preferensi responden dan lolos uji konsistensi; "
             "(3) menampilkan peringkat beserta alasan per kriteria yang mudah dipahami; dan (4) menjaga "
             "keterlacakan sumber data, termasuk harga yang hanya berupa snapshot."))
    add(heading("1.3 Keterbaruan dan Fase Final", 2))
    add(body("Keterbaruan karya adalah integrasi tiga metode dalam satu aplikasi web. AHP menghasilkan bobot "
             "enam kriteria dari kuesioner dengan consistency ratio (CR) di bawah 0,1. TOPSIS memeringkat "
             "destinasi berdasarkan kedekatan dengan solusi ideal. K-Means (MacQueen, 1967) memberi label segmen "
             "destinasi tanpa mengubah peringkat. Kriteria mencakup kecocokan hobi dengan kemiripan Jaccard dan "
             "jarak garis lurus Haversine dari 339 kota asal. Setiap kartu hasil menampilkan posisi destinasi "
             "pada keenam kriteria dan kalimat alasan. Seluruh 443 destinasi dipertahankan tanpa penghapusan; "
             "data yang bermasalah diberi catatan kualitas, dan pipeline data menolak hasil olahan yang usang."))
    add(body("Prototipe fungsional telah berjalan secara lokal dengan Django dan lolos 190 uji otomatis. Fase "
             "final PKM-KC adalah aplikasi yang dapat diakses daring, memakai bobot dari kuesioner berskala "
             "Saaty 1–9 dengan responden yang lebih beragam, memuat tarif destinasi sampel yang telah "
             "diverifikasi, dilengkapi penjelasan kontribusi kriteria, simulasi \"bagaimana jika\", dan uji "
             "sensitivitas bobot, serta telah diuji oleh calon pengguna."))
    add(heading("1.4 Luaran dan Manfaat", 2))
    add(body("Luaran yang ditargetkan: (1) aplikasi web SPK TravelFit yang dapat diakses daring; (2) dataset "
             "destinasi Jawa terkurasi beserta dokumentasi sumber; (3) laporan bobot AHP hasil kuesioner; "
             "(4) buku panduan pengguna; (5) laporan kemajuan dan laporan akhir; serta (6) akun media sosial "
             "dan video promosi kegiatan. Bagi wisatawan, aplikasi memberi daftar pembanding yang sesuai "
             "preferensi beserta alasannya. Bagi pengelola wisata, aplikasi menggambarkan posisi destinasi "
             "menurut kriteria yang dipertimbangkan wisatawan. Bagi pembelajaran SPK, karya ini menjadi contoh "
             "penerapan CRISP-DM, AHP, dan TOPSIS yang dapat ditelusuri."))

    add(heading("BAB 2. TINJAUAN PUSTAKA", 1))
    add(heading("2.1 Sistem Rekomendasi dan Pendukung Keputusan Wisata", 2))
    add(body("Sistem rekomendasi membantu pengguna memilih di antara banyak item yang sulit dibandingkan secara "
             "manual (Ricci, Rokach dan Shapira, 2015). Pendekatan berbasis riwayat interaksi membutuhkan data "
             "perilaku pengguna dalam jumlah besar. Pendekatan keputusan multikriteria lebih sesuai ketika "
             "pengguna dapat menyatakan preferensinya secara langsung, misalnya budget, minat, dan kota asal, "
             "karena hasil dapat dihitung tanpa akun maupun riwayat sebelumnya. TravelFit memakai pendekatan "
             "kedua: preferensi dimasukkan melalui formulir, lalu setiap destinasi dinilai pada kriteria yang "
             "sama."))
    add(heading("2.2 Analytic Hierarchy Process (AHP)", 2))
    add(body("AHP menurunkan bobot kriteria dari matriks perbandingan berpasangan (Saaty, 2008). Setiap kolom "
             "matriks dinormalisasi, lalu bobot adalah rata-rata baris. Konsistensi diuji dengan "
             "CI = (λmaks − n)/(n − 1) dan CR = CI/RI; untuk enam kriteria RI = 1,24 dan matriks diterima bila "
             "CR < 0,1. Pada kuesioner tahap awal, responden memilih kriteria yang lebih penting pada setiap "
             "pasangan, sehingga nilai matriks diperoleh dari rasio jumlah pemilih, aᵢⱼ = nᵢ/nⱼ, yang dibatasi "
             "pada skala 1/9 sampai 9."))
    add(heading("2.3 TOPSIS", 2))
    add(body("TOPSIS memeringkat alternatif berdasarkan jarak ke solusi ideal positif dan negatif (Hwang dan "
             "Yoon, 1981). Nilai dinormalisasi vektor rᵢⱼ = xᵢⱼ/√Σxᵢⱼ², dikalikan bobot, lalu dihitung jarak "
             "Euclidean D⁺ dan D⁻. Nilai preferensi Vᵢ = D⁻/(D⁺ + D⁻) berada pada rentang 0–1. Metode ini "
             "dipilih karena tetap terdefinisi ketika ada nilai nol, berbeda dengan normalisasi cost min/x pada "
             "SAW dan perpangkatan negatif pada Weighted Product. Kelemahannya, peringkat dapat berubah bila "
             "himpunan kandidat berubah, sehingga skor dibaca relatif terhadap kandidat pada pencarian tersebut."))
    add(heading("2.4 K-Means, Haversine, Jaccard, dan CRISP-DM", 2))
    add(body("K-Means mengelompokkan data ke k cluster dengan meminimalkan jarak ke centroid (MacQueen, 1967). "
             "Inisialisasi k-means++ memilih centroid awal yang saling berjauhan sehingga hasil lebih stabil "
             "(Arthur dan Vassilvitskii, 2007), dan kualitas cluster dinilai dengan koefisien silhouette "
             "(Rousseeuw, 1987). Jarak garis lurus antara kota asal dan destinasi dihitung dengan rumus "
             "Haversine (Sinnott, 1984), sedangkan kecocokan hobi diukur dengan kemiripan Jaccard, yaitu irisan "
             "dibagi gabungan dua himpunan (Jaccard, 1912). Seluruh pengembangan mengikuti CRISP-DM: pemahaman "
             "bisnis, pemahaman data, persiapan data, pemodelan, evaluasi, dan penerapan (Wirth dan Hipp, 2000)."))
    add(heading("2.5 Posisi Karya terhadap Produk yang Ada", 2))
    add(body("Situs peta dan ulasan menyediakan banyak informasi, tetapi pengguna tidak dapat menentukan bobot "
             "kepentingan setiap kriteria dan tidak memperoleh alasan peringkat. Penerapan AHP dan TOPSIS untuk "
             "pemilihan alternatif sudah umum dalam literatur SPK. Pembeda karya ini terletak pada empat hal: "
             "(1) bobot berasal dari kuesioner dan diuji konsistensinya; (2) kriteria personal berupa kecocokan "
             "kategori dan hobi dinilai bersama harga, rating, jarak, dan fasilitas; (3) alasan per kriteria "
             "ditampilkan langsung kepada pengguna; dan (4) sumber serta keterbatasan data tetap terlihat."))

    add(heading("BAB 3. TAHAP PELAKSANAAN", 1))
    add(body("Pelaksanaan terdiri atas enam tahap berulang (Gambar 1). Hasil uji pada tahap 6 menjadi umpan "
             "balik untuk memperbaiki data, bobot, dan antarmuka."))
    add(figure("rId10", 1))
    add(heading("3.1 Tahap 1: Pengumpulan Data", 2))
    add(body("**Data sekunder.** Dataset Kaggle Indonesia Tourism Destination (aprabowo, t.t.) berisi 437 "
             "destinasi dan data rating pengguna, dengan 9.597 rating valid setelah pembersihan. Enam destinasi "
             "tambahan dikurasi dengan tarif dari Peraturan Daerah Provinsi Banten (Pemerintah Provinsi Banten, "
             "2024), Kabupaten Lebak (Pemerintah Kabupaten Lebak, 2025), Kabupaten Purworejo (Pemerintah "
             "Kabupaten Purworejo, 2026), dan Kabupaten Ngawi (Pemerintah Kabupaten Ngawi, 2023), serta lokasi "
             "dari OpenStreetMap (OpenStreetMap Foundation, t.t.). Koordinat 339 kota dan kabupaten asal dipakai "
             "untuk menghitung jarak."))
    add(body("**Data primer.** Kuesioner Google Form berisi 15 pasangan kriteria. Tahap awal memperoleh 28 "
             "responden dan menghasilkan bobot dengan CR 0,060. Pada fase final, kuesioner memakai skala Saaty "
             "1–9 dan disebarkan kepada responden yang lebih beragam, dengan target minimal 100 respons valid. "
             "Jumlah respons yang telah terkumpul: ⟦ISI⟧."))
    add(heading("3.2 Tahap 2: Persiapan Data", 2))
    add(item("**Integrasi dan retensi.** Data Kaggle dan kurasi digabung menjadi 443 baris dengan ID 1–443. "
             "Pipeline berhenti bila ada ID yang hilang atau ganda; tidak ada destinasi yang dihapus.", 2))
    add(item("**Pembersihan dan penandaan kualitas.** Nama kolom dan teks dirapikan, nilai numerik diperiksa, dan "
             "masalah data, seperti koordinat Pelabuhan Marina yang berada di luar Jawa, disimpan sebagai catatan "
             "kualitas.", 2))
    add(item("**Imputasi minimal.** Hanya rating Taman Hutan Raya Banten yang kosong diisi median 4,5 pada kolom "
             "perhitungan, sementara rating sumber tetap kosong.", 2))
    add(item("**Konstruksi fitur.** C4 dibentuk dari penyebutan enam kelompok fasilitas pada deskripsi dengan "
             "pencocokan kata utuh dan koreksi konteks pada 16 destinasi. Tiga belas tag aktivitas dibentuk "
             "untuk C6, dan kategori diseragamkan menjadi enam.", 2))
    add(item("**Manifest.** Hash SHA-256 sumber dan keluaran serta fingerprint pipeline disimpan, sehingga impor "
             "basis data dan pelatihan model menolak artefak yang tidak sesuai sumber.", 2))
    add(heading("3.3 Tahap 3: Segmentasi K-Means", 2))
    add(body("Fitur segmentasi berjumlah delapan: harga tiket yang dibatasi persentil ke-99 (Rp275.800) lalu "
             "distandardisasi Z-score, rating yang distandardisasi, dan enam kolom one-hot kategori. Model "
             "dilatih pada seluruh 443 destinasi dengan k = 2 sampai 6, inisialisasi k-means++, 10 kali "
             "pengulangan, dan seed 42. Konfigurasi dipilih dari silhouette tertinggi dengan ukuran cluster "
             "minimal 22 anggota. Hasil saat ini adalah dua segmen (414 dan 29 destinasi) dengan silhouette "
             "0,54302. Label segmen hanya ditampilkan sebagai informasi; label tersebut tidak menyaring kandidat "
             "maupun mengubah bobot. Model dievaluasi ulang setelah data diperbarui pada fase final."))
    add(heading("3.4 Tahap 4: Pembobotan AHP dan Peringkat TOPSIS", 2))
    add(item("**Kriteria (6).** C1 harga tiket dan C3 jarak Haversine dari kota asal bersifat cost. C2 rating, C4 "
             "indikator fasilitas, C5 kecocokan kategori (utama 1, sekunder 0,5, lainnya 0), dan C6 kecocokan "
             "hobi (Jaccard) bersifat benefit.", 3))
    add(item("**Bobot AHP.** Jawaban kuesioner diubah menjadi matriks aᵢⱼ = nᵢ/nⱼ. Bobot hasilnya adalah C5 "
             "26,04%, C6 23,19%, C1 16,13%, C2 13,51%, C4 13,23%, dan C3 7,90% dengan CR 0,060 (Lampiran 5, "
             "Gambar 4). Profil Hemat, Kualitas, dan Petualang tetap tersedia sebagai variasi prioritas.", 3))
    add(item("**Filter kandidat.** Kandidat adalah destinasi di provinsi tujuan dengan harga tiket tidak melebihi "
             "budget per orang. Destinasi gratis tetap menjadi kandidat.", 3))
    add(item("**TOPSIS.** Matriks keputusan dinormalisasi vektor, dikalikan bobot, lalu dihitung D⁺, D⁻, dan V "
             "untuk setiap kandidat. Sepuluh destinasi dengan V tertinggi ditampilkan.", 3))
    add(item("**Penjelasan.** Setiap hasil menampilkan posisi pada keenam kriteria terhadap rentang ideal kandidat "
             "dan kalimat \"unggul pada … ; tertahan oleh …\".", 3))
    add(body("**Contoh.** Pengguna dari Bandung memilih Jawa Barat, budget Rp50.000, kategori utama alam, kategori "
             "sekunder budaya, hobi fotografi dan hiking, serta profil Seimbang. Sebanyak 113 destinasi lolos "
             "filter. Peringkat pertama adalah Caringin Tilu dengan tiket Rp0, rating 4,4, jarak 8,3 km, dan "
             "Jaccard hobi 0,5. Nilainya D⁺ = 0,0524, D⁻ = 0,0958, dan V = 0,0958/(0,0524 + 0,0958) = 0,6462. "
             "Peringkat berikutnya adalah Gunung Lalakon (0,6038) dan Tafso Barn (0,5599)."))
    add(heading("3.5 Tahap 5: Konstruksi Aplikasi", 2))
    add(body("Aplikasi dibangun dengan Python dan Django, dengan antarmuka HTML, CSS, dan JavaScript tanpa "
             "framework tambahan. Arsitekturnya ada di Lampiran 5. Aplikasi memiliki tiga halaman:"))
    add(item("Rekomendasi: formulir preferensi, pengaturan bobot lanjutan, dan kartu hasil Top 10.", 4))
    add(item("Peta Jawa: peta enam provinsi untuk memilih wilayah dan daftar seluruh 443 destinasi.", 4))
    add(item("Metode dan Data: tahapan CRISP-DM, sumber data, dan keterbatasan.", 4))
    add(body("Preprocessing dan pelatihan K-Means berjalan luring. Aplikasi daring hanya menghitung AHP dan "
             "TOPSIS saat pengguna mengirim preferensi. Pada fase final, data dibaca langsung dari berkas CSV "
             "dan JSON sehingga aplikasi dapat di-hosting di PythonAnywhere tanpa proses impor basis data."))
    add(heading("3.6 Tahap 6: Pengujian Keandalan dan Penerimaan", 2))
    add(body("**Uji teknis.** Uji teknis mencakup: (1) 190 uji otomatis yang memeriksa preprocessing, impor, "
             "pelatihan, AHP, TOPSIS, dan tampilan, dan seluruhnya telah lulus pada prototipe; (2) pencocokan "
             "hasil TOPSIS dengan perhitungan manual di spreadsheet; (3) pembanding SAW dengan korelasi "
             "peringkat Spearman; dan (4) uji sensitivitas, yaitu bobot tiap kriteria diubah ±10% dan ±20% untuk "
             "melihat stabilitas sepuluh besar. Uji sensitivitas dijalankan pada fase final."))
    add(body("**Uji penerimaan.** Minimal 30 calon wisatawan mencoba aplikasi, lalu menilainya pada skala 1–5 "
             "untuk lima aspek: kemudahan penggunaan, kesesuaian hasil, kejelasan alasan, kecepatan, dan "
             "tampilan. Responden juga menilai apakah tiga rekomendasi teratas relevan dengan rencana mereka. "
             "Target: skor rata-rata ≥ 4 dan minimal 70% responden menilai setidaknya satu dari tiga "
             "rekomendasi teratas relevan."))
    add(heading("3.7 Analisis Hasil dan Etika", 2))
    add(body("Keberhasilan dinilai dari tiga indikator: aplikasi daring berjalan stabil, bobot final lolos uji "
             "konsistensi (CR < 0,1), dan target uji penerimaan tercapai. Aplikasi tidak meminta akun dan tidak "
             "menyimpan data pribadi. Respons kuesioner mentah yang memuat nama dan surel tidak disimpan di "
             "repositori; hanya rekap jumlah pilihan yang anonim. Harga ditampilkan sebagai snapshot sumber "
             "beserta tautan bukti, skor TOPSIS dijelaskan sebagai kedekatan relatif dan bukan jaminan kepuasan, "
             "dan data OpenStreetMap diberi atribusi sesuai lisensinya."))

    add(heading("BAB 4. BIAYA DAN JADWAL KEGIATAN", 1))
    add(heading("4.1 Anggaran Biaya", 2))
    add(table_caption("Tabel 1. Rekapitulasi rencana anggaran biaya"))
    add(table([1227, 4329, 1154, 1227], [
        ["No", "Jenis Pengeluaran", "Sumber Dana", "Besaran Dana (Rp)"],
        ["1", "Bahan habis pakai (ATK, kertas, cetak kuesioner, poster, buku panduan, x-banner, stiker QR, "
              "kartu panduan)", "Belmawa", "1.840.000"],
        ["", "", "Perguruan Tinggi", "1.000.000"],
        ["2", "Sewa dan jasa (hosting aplikasi web 4 bulan dan domain 1 tahun)", "Belmawa", "650.000"],
        ["3", "Transportasi lokal (verifikasi tarif dan lokasi destinasi sampel, sesi uji pengguna)", "Belmawa",
         "1.800.000"],
        ["4", "Lain-lain (iklan media sosial, akses publikasi berbayar, komunikasi)", "Belmawa", "850.000"],
        ["Jumlah", "", "", "6.140.000"],
        ["Rekap sumber dana", "", "Belmawa", "5.140.000"],
        ["", "", "Perguruan Tinggi", "1.000.000"],
        ["", "", "Instansi Lain", "0"],
        ["", "", "Jumlah", "6.140.000"],
    ], bold_rows=(6, 10)))
    add(empty())
    add(body("Proporsi: bahan habis pakai 46,3%, sewa dan jasa 10,6%, transportasi 29,3%, dan lain-lain 13,8%. "
             "Semua proporsi di bawah batas maksimum. Rincian ada di Lampiran 2."))
    add(heading("4.2 Jadwal Kegiatan", 2))
    add(table_caption("Tabel 2. Jadwal kegiatan"))
    m = "■"
    add(table([624, 3648, 624, 624, 624, 624, 1169], [
        ["No", "Kegiatan", "Bulan 1", "Bulan 2", "Bulan 3", "Bulan 4", "Penanggung Jawab"],
        ["1", "Koordinasi tim dan penyusunan kuesioner bobot skala 1–9", m, "", "", "", "Reynard Liu"],
        ["2", "Penyebaran kuesioner dan rekap anonim", m, m, "", "", "Justin Augusto Liustri"],
        ["3", "Verifikasi tarif dan lokasi destinasi sampel", m, m, "", "", "Kristofer Ryan Giggs Eka Saputra"],
        ["4", "Pembaruan bobot AHP dan evaluasi ulang K-Means", "", m, "", "", "Cristian Dion"],
        ["5", "Migrasi data ke CSV/JSON dan deployment daring", "", m, m, "", "Cristian Dion"],
        ["6", "Fitur penjelasan: kontribusi kriteria, simulasi, sensitivitas", "", m, m, "",
         "Kristofer Ryan Giggs Eka Saputra"],
        ["7", "Uji keandalan dan uji penerimaan pengguna", "", "", m, m, "Reynard Liu"],
        ["8", "Perbaikan berdasarkan umpan balik", "", "", "", m, "Cristian Dion"],
        ["9", "Publikasi media sosial, laporan kemajuan dan akhir", m, m, m, m, "Justin Augusto Liustri"],
    ]))
    add(empty())

    add(heading("DAFTAR PUSTAKA", 1))
    for text in REFERENCES:
        add(ref(text))
    add(page_break())

    add(heading("LAMPIRAN", 1))
    add(heading("Lampiran 1. Biodata Ketua, Anggota, dan Dosen Pendamping", 2))
    add(body("Isi satu tabel untuk setiap anggota (Kristofer Ryan Giggs Eka Saputra, Cristian Dion, Reynard Liu, "
             "Justin Augusto Liustri) dan satu untuk dosen pendamping. Bagian bertanda ⟦ISI⟧ dilengkapi sendiri "
             "oleh yang bersangkutan."))
    add(body("**A. Identitas Diri (contoh format, ulangi untuk setiap anggota)**"))
    add(table([744, 5953, 1240], [["No", "Identitas", "Isian"]] + [
        [str(i), label, "⟦ISI⟧"] for i, label in enumerate(
            ["Nama Lengkap", "Jenis Kelamin", "Program Studi", "NIM", "Tempat dan Tanggal Lahir",
             "Alamat Surel", "Nomor Telepon/HP"], 1)]))
    add(empty())
    add(body("**B. Kegiatan Kemahasiswaan yang Sedang/Pernah Diikuti**"))
    add(table([677, 1992, 2989, 2279], [["No", "Jenis Kegiatan", "Status dalam Kegiatan", "Waktu dan Tempat"],
                                        ["1", "⟦ISI⟧", "⟦ISI⟧", "⟦ISI⟧"]]))
    add(empty())
    add(body("**C. Penghargaan yang Pernah Diterima**"))
    add(table([680, 2624, 3859, 774], [["No", "Jenis Penghargaan", "Pihak Pemberi Penghargaan", "Tahun"],
                                       ["1", "⟦ISI⟧", "⟦ISI⟧", "⟦ISI⟧"]]))
    add(empty())
    add(body("Semua data yang saya isikan dan tercantum dalam biodata ini adalah benar dan dapat "
             "dipertanggungjawabkan secara hukum. Apabila di kemudian hari ternyata dijumpai ketidaksesuaian "
             "dengan kenyataan, saya sanggup menerima sanksi. Demikian biodata ini saya buat dengan sebenarnya "
             "untuk memenuhi salah satu persyaratan dalam pengajuan PKM-KC."))
    add(body("⟦Kota⟧, ⟦tanggal bulan tahun⟧ — Pengusul, ⟦tanda tangan⟧ ⟦Nama Lengkap⟧"))
    add(body("Biodata Dosen Pendamping: nama lengkap dan gelar, jenis kelamin, program studi, NIP/NIDN, tempat dan "
             "tanggal lahir, alamat surel, nomor HP; riwayat pendidikan (S1/S2/S3: institusi, bidang ilmu, tahun); "
             "rekam jejak Tri Dharma PT (pendidikan/pengajaran, penelitian, pengabdian kepada masyarakat). ⟦ISI⟧"))

    add(heading("Lampiran 2. Justifikasi Anggaran Kegiatan", 2))
    add(table([659, 3899, 1429, 1104, 846], [
        ["No", "Jenis Pengeluaran", "Volume", "Harga Satuan (Rp)", "Total (Rp)"],
        ["1", "Bahan habis pakai", "", "", ""],
        ["", "ATK (pulpen, map, buku catatan)", "1 paket", "300.000", "300.000"],
        ["", "Kertas A4 80 gram", "2 rim", "60.000", "120.000"],
        ["", "Cetak lembar kuesioner dan informasi responden", "200 lembar", "1.000", "200.000"],
        ["", "Cetak poster A3 sosialisasi aplikasi", "10 lembar", "30.000", "300.000"],
        ["", "Cetak buku panduan pengguna", "10 eksemplar", "75.000", "750.000"],
        ["", "X-banner untuk sesi uji pengguna", "2 buah", "200.000", "400.000"],
        ["", "Stiker kode QR tautan aplikasi", "200 lembar", "2.500", "500.000"],
        ["", "Cetak kartu panduan singkat untuk pengguna", "300 lembar", "900", "270.000"],
        ["", "Subtotal (Belmawa 1.840.000; Perguruan Tinggi 1.000.000)", "", "", "2.840.000"],
        ["2", "Sewa dan jasa", "", "", ""],
        ["", "Hosting aplikasi web berbayar (PythonAnywhere)", "4 bulan", "100.000", "400.000"],
        ["", "Domain aplikasi", "1 tahun", "250.000", "250.000"],
        ["", "Subtotal (Belmawa)", "", "", "650.000"],
        ["3", "Transportasi lokal", "", "", ""],
        ["", "Kunjungan verifikasi tarif dan lokasi destinasi sampel serta sesi uji pengguna",
         "10 kunjungan × 2 orang", "90.000", "1.800.000"],
        ["", "Subtotal (Belmawa)", "", "", "1.800.000"],
        ["4", "Lain-lain", "", "", ""],
        ["", "Iklan berbayar media sosial untuk publikasi kegiatan", "1 paket", "400.000", "400.000"],
        ["", "Akses artikel ilmiah berbayar", "1 paket", "150.000", "150.000"],
        ["", "Biaya komunikasi (kuota internet tim)", "4 bulan", "75.000", "300.000"],
        ["", "Subtotal (Belmawa)", "", "", "850.000"],
        ["", "Jumlah (Belmawa 5.140.000; Perguruan Tinggi 1.000.000)", "", "", "6.140.000"],
    ], bold_rows=(1, 11, 15, 18, 23)))
    add(empty())

    add(heading("Lampiran 3. Susunan Tim Pengusul dan Pembagian Tugas", 2))
    add(table([650, 1422, 684, 650, 1369, 3162], [
        ["No", "Nama / NIM", "Program Studi", "Bidang Ilmu", "Alokasi Waktu (jam/minggu)", "Uraian Tugas"],
        ["1", "Kristofer Ryan Giggs Eka Saputra / 412024005", "⟦ISI⟧", "⟦ISI⟧", "10",
         "Verifikasi tarif dan lokasi destinasi, pengembangan fitur penjelasan dan uji sensitivitas"],
        ["2", "Cristian Dion / 412024006", "⟦ISI⟧", "⟦ISI⟧", "10",
         "Pipeline data, pemodelan AHP–TOPSIS dan K-Means, pengembangan dan deployment aplikasi"],
        ["3", "Reynard Liu / 412025022", "⟦ISI⟧", "⟦ISI⟧", "10",
         "Kajian pustaka, penyusunan kuesioner dan proposal, koordinasi uji penerimaan pengguna"],
        ["4", "Justin Augusto Liustri / 412025029", "⟦ISI⟧", "⟦ISI⟧", "10",
         "Penyebaran dan rekap kuesioner, publikasi media sosial, laporan kemajuan dan akhir"],
    ]))
    add(empty())
    add(body("Ketua tim: ⟦ISI: nama ketua⟧. Sesuai aturan kolaborasi mata kuliah, anggota angkatan 2025 memimpin "
             "penyusunan proposal, dan anggota angkatan 2024 memimpin integrasi teknis. Seluruh anggota tetap "
             "terlibat di setiap tahap."))

    add(page_break())
    add(heading("Lampiran 4. Surat Pernyataan Ketua Tim Pengusul", 2))
    add(body("Yang bertanda tangan di bawah ini:"))
    for label in ("Nama", "NIM", "Program Studi", "Fakultas"):
        add(item(f"{label}: ⟦ISI⟧", 5))
    add(body(f"Dengan ini menyatakan bahwa proposal PKM-KC saya dengan judul \"{TITLE}\" yang diusulkan untuk "
             "tahun anggaran 2026 adalah asli karya kami dan belum pernah dibiayai oleh lembaga atau sumber dana "
             "lain."))
    add(body("Bilamana di kemudian hari ditemukan ketidaksesuaian dengan pernyataan ini, maka saya bersedia dituntut "
             "dan diproses sesuai dengan ketentuan yang berlaku dan mengembalikan seluruh biaya yang sudah diterima "
             "ke kas negara."))
    add(body("Demikian pernyataan ini dibuat dengan sesungguhnya dan dengan sebenar-benarnya."))
    add(body("⟦Kota⟧, ⟦tanggal bulan tahun⟧ — Yang menyatakan, ⟦meterai dan tanda tangan⟧ ⟦Nama Lengkap⟧, "
             "NIM ⟦ISI⟧"))

    add(heading("Lampiran 5. Gambaran Teknologi yang Akan Dikembangkan", 2))
    add(body("Produk adalah aplikasi web yang memisahkan pengolahan data dan pelatihan K-Means (luring) dari "
             "aplikasi yang dipakai wisatawan (daring). Proses luring menghasilkan CSV destinasi, CSV fitur, "
             "manifest, dan berkas JSON model K-Means. Aplikasi membaca artefak tersebut lalu menghitung AHP dan "
             "TOPSIS untuk setiap permintaan."))
    add(figure("rId11", 2))
    add(body("Alur penggunaan: wisatawan mengisi budget tiket per orang, kota asal, provinsi tujuan, kategori "
             "utama dan sekunder, hobi, serta profil prioritas. Sistem kemudian (1) menyaring destinasi di "
             "provinsi tujuan dengan tiket tidak melebihi budget, (2) membentuk matriks C1–C6, (3) menghitung "
             "peringkat TOPSIS dengan bobot AHP, dan (4) menampilkan sepuluh destinasi teratas beserta skor, "
             "alasan per kriteria, sisa alokasi tiket, sumber harga, dan label segmen."))
    add(figure("rId12", 3))
    add(figure("rId13", 4))
    add(table([1029, 2499, 4409], [
        ["Komponen", "Teknologi", "Fungsi"],
        ["Antarmuka", "Django Template, HTML, CSS, JavaScript", "Formulir preferensi, kartu hasil, peta provinsi"],
        ["Pengolahan data", "pandas dan NumPy (pipeline bersama)", "443 destinasi, fitur C1–C6, manifest hash"],
        ["Segmentasi", "K-Means (implementasi NumPy)", "Label segmen dan evaluasi silhouette"],
        ["Keputusan", "AHP dan TOPSIS (implementasi sendiri)", "Bobot, CR, peringkat, dan alasan per kriteria"],
        ["Pengujian", "Django test runner (190 uji otomatis)", "Menjamin hasil konsisten setelah setiap perubahan"],
        ["Hosting", "PythonAnywhere", "Akses daring tanpa instalasi"],
    ]))
    add(empty())
    add(heading("Lampiran 6. Hasil Uji Periksa Similaritas Proposal", 2))
    add(body("⟦Lampirkan hasil uji similaritas bagian inti (Bab 1 sampai Daftar Pustaka) dari Turnitin, "
             "iThenticate, atau sejenisnya. Indeks similaritas maksimum 25%.⟧"))
    return b


REFERENCES = [
    "aprabowo (t.t.) *Indonesia Tourism Destination* [dataset]. Kaggle. Tersedia di: "
    "https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination (Diakses: 1 Oktober 2026).",
    "Arthur, D. dan Vassilvitskii, S. (2007) 'k-means++: the advantages of careful seeding', dalam *Proceedings "
    "of the Eighteenth Annual ACM-SIAM Symposium on Discrete Algorithms*. New Orleans, pp. 1027–1035.",
    "Hwang, C.L. dan Yoon, K. (1981) *Multiple Attribute Decision Making: Methods and Applications*. Berlin: "
    "Springer-Verlag.",
    "Jaccard, P. (1912) 'The distribution of the flora in the alpine zone', *New Phytologist*, 11(2), pp. 37–50.",
    "MacQueen, J. (1967) 'Some methods for classification and analysis of multivariate observations', dalam "
    "*Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability*, Vol. 1. Berkeley: "
    "University of California Press, pp. 281–297.",
    "OpenStreetMap Foundation (t.t.) *Copyright and License*. Tersedia di: https://www.openstreetmap.org/copyright "
    "(Diakses: 1 Oktober 2026).",
    "Pemerintah Kabupaten Lebak (2025) *Peraturan Daerah Kabupaten Lebak Nomor 1 Tahun 2025*. Tersedia di: "
    "https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf (Diakses: 30 September 2026).",
    "Pemerintah Kabupaten Ngawi (2023) *Peraturan Daerah Kabupaten Ngawi Nomor 10 Tahun 2023 tentang Pajak Daerah "
    "dan Retribusi Daerah*. Tersedia di: https://bakeu.ngawikab.go.id/home/public/files/ppd/"
    "PERDA%20NO%2010%20TAHUN%202023.pdf (Diakses: 30 September 2026).",
    "Pemerintah Kabupaten Purworejo (2026) *Peraturan Daerah Kabupaten Purworejo Nomor 1 Tahun 2026*. Tersedia di: "
    "https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf (Diakses: 30 September 2026).",
    "Pemerintah Provinsi Banten (2024) *Peraturan Daerah Provinsi Banten Nomor 1 Tahun 2024*. Tersedia di: "
    "https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf (Diakses: 30 September "
    "2026).",
    "Ricci, F., Rokach, L. dan Shapira, B. (2015) *Recommender Systems Handbook*. Edisi ke-2. New York: Springer.",
    "Rousseeuw, P.J. (1987) 'Silhouettes: a graphical aid to the interpretation and validation of cluster "
    "analysis', *Journal of Computational and Applied Mathematics*, 20, pp. 53–65.",
    "Saaty, T.L. (2008) 'Decision making with the analytic hierarchy process', *International Journal of "
    "Services Sciences*, 1(1), pp. 83–98.",
    "Sinnott, R.W. (1984) 'Virtues of the Haversine', *Sky and Telescope*, 68(2), p. 159.",
    "Wirth, R. dan Hipp, J. (2000) 'CRISP-DM: towards a standard process model for data mining', dalam "
    "*Proceedings of the 4th International Conference on the Practical Applications of Knowledge Discovery and "
    "Data Mining*. Manchester, pp. 29–39.",
]


def front_matter(blocks, pages):
    def page(text):
        return pages.get(text, 0)

    out = [toc_title("DAFTAR ISI")]
    for label, number in (("DAFTAR ISI", "i"), ("DAFTAR GAMBAR", "ii"), ("DAFTAR TABEL", "ii"),
                          ("DAFTAR LAMPIRAN", "ii")):
        out.append(toc_entry(label, number))
    for kind, text in blocks:
        if kind == 1:
            out.append(toc_entry(text, page(text)))
        elif kind == 2 and not text.startswith("Lampiran"):
            out.append(toc_entry(text, page(text), level=2))
    out.append(page_break())
    out.append(toc_title("DAFTAR GAMBAR"))
    out += [toc_plain(caption, page(caption)) for _, caption in IMAGES.values()]
    out.append(toc_title("DAFTAR TABEL"))
    for caption in ("Tabel 1. Rekapitulasi rencana anggaran biaya", "Tabel 2. Jadwal kegiatan"):
        out.append(toc_plain(caption, page(caption)))
    out.append(toc_title("DAFTAR LAMPIRAN"))
    out += [toc_plain(text, page(text)) for kind, text in blocks if kind == 2 and text.startswith("Lampiran")]
    return out


def main():
    template = Path(sys.argv[1])
    pages = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if len(sys.argv) > 2 else {}
    source = zipfile.ZipFile(template)
    original = source.read("word/document.xml").decode("utf-8")
    prefix = original[:original.index("<w:body>") + len("<w:body>")]
    front_sect = re.search(r'<w:p><w:pPr><w:sectPr>.*?</w:sectPr></w:pPr></w:p>', original).group(0)
    final_sect = original[original.rindex("<w:sectPr"):original.rindex("</w:body>")]

    blocks = content()
    headings = [(int(m.group(1)), re.sub(r"<[^>]+>", "", m.group(2)))
                for m in (re.match(r'<w:p><w:pPr><w:pStyle w:val="Heading(\d)"/></w:pPr>(.*)</w:p>$', x) for x in blocks)
                if m]
    document = prefix + "".join(front_matter(headings, pages)) + front_sect + "".join(blocks) + final_sect + \
        "</w:body></w:document>"

    rels = source.read("word/_rels/document.xml.rels").decode("utf-8")
    for rid, (name, _) in IMAGES.items():
        rels = re.sub(rf'(Id="{rid}"[^>]*Target=")media/[^"]+(")', rf"\1media/{name}\2", rels)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = source.read("docProps/core.xml").decode("utf-8")
    core = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>Proposal PKM-KC TravelFit</dc:title>", core)
    core = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator>Kelompok TravelFit</dc:creator>", core)
    core = re.sub(r'(<dcterms:(created|modified) xsi:type="dcterms:W3CDTF">)[^<]+', rf"\g<1>{now}", core)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            if info.filename.startswith("word/media/"):
                continue
            data = source.read(info.filename)
            if info.filename == "word/document.xml":
                data = document.encode("utf-8")
            elif info.filename == "word/_rels/document.xml.rels":
                data = rels.encode("utf-8")
            elif info.filename == "docProps/core.xml":
                data = core.encode("utf-8")
            target.writestr(info, data)
        for name, _ in IMAGES.values():
            target.write(HERE / "img" / name, f"word/media/{name}")
    print(OUTPUT)


if __name__ == "__main__":
    main()
