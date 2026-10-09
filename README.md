# TravelFit — Sistem Pendukung Keputusan Rekomendasi Destinasi Wisata Jawa

TravelFit membantu wisatawan memilih destinasi berdasarkan batas harga tiket,
kota asal, kategori, hobi, dan profil prioritas. Data aktif berjumlah **443
destinasi: 437 dari Kaggle dan 6 hasil kurasi Jawa**, dengan label tujuan pada
Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, Daerah Istimewa Yogyakarta, dan
Jawa Timur. CRISP-DM menjadi kerangka pengolahan data, K-Means mengelompokkan
destinasi, dan AHP–TOPSIS menghasilkan rekomendasi.

## Identitas kelompok

| Nama | NIM |
| --- | --- |
| Kristofer Ryan Giggs Eka Saputra | 412024005 |
| Cristian Dion | 412024006 |
| Reynard Liu | 412025022 |
| Justin Augusto Liustri | 412025029 |

## Metode SPK dan alasan pemilihan

Metode SPK yang digunakan adalah **AHP untuk pembobotan kriteria** dan
**TOPSIS untuk pemeringkatan destinasi**.

- **AHP** membandingkan enam kriteria secara berpasangan dan memeriksa
  konsistensi matriks. Yang dibandingkan adalah kriteria, bukan seluruh destinasi.
- **TOPSIS** menilai alternatif berdasarkan kedekatan terhadap solusi ideal
  dengan mempertimbangkan kriteria cost dan benefit. Tahap perhitungannya dapat
  ditelusuri dari matriks keputusan sampai skor akhir.

Bobot berasal dari empat profil preset rancangan pengembang, bukan hasil survei.
Setiap profil memiliki consistency ratio (CR) kurang dari 0,1.

| Profil | Prioritas utama | CR |
| --- | --- | --- |
| Seimbang | Mempertimbangkan seluruh kriteria; bobot tidak sama rata | 0,008418 |
| Hemat | Harga tiket | 0,002559 |
| Kualitas | Rating | 0,012159 |
| Petualang | Jarak serta kecocokan kategori dan hobi | 0,004431 |

**K-Means bukan metode pemeringkatan SPK.** Algoritma ini memberi label segmen
berdasarkan kemiripan fitur. Label cluster tidak menyaring kandidat TOPSIS dan
tidak menentukan bobot AHP.

## Kriteria pengambilan keputusan

Cost mengutamakan nilai lebih kecil, sedangkan benefit mengutamakan nilai lebih besar.

| Kode | Kriteria | Jenis | Arti nilai pada aplikasi |
| --- | --- | --- | --- |
| C1 | Harga tiket | Cost | Harga sumber satu destinasi per orang, tanpa pembatasan P99 |
| C2 | Rating model | Benefit | Rating sumber atau nilai imputasi yang diberi penanda |
| C3 | Jarak garis lurus | Cost | Jarak Haversine dari kota asal ke koordinat destinasi, dalam km |
| C4 | Indikator fasilitas | Benefit | Jumlah kelompok penyebutan fasilitas yang diterima dari deskripsi, dibagi 6 |
| C5 | Kecocokan kategori | Benefit | Kategori utama bernilai 1, sekunder 0,5, dan lainnya 0 |
| C6 | Kecocokan hobi | Benefit | Kemiripan Jaccard antara hobi pengguna dan tag aktivitas destinasi |

C4 mencakup toilet, parkir, makanan, tempat ibadah, aksesibilitas, dan pusat
informasi. Nilai 0 berarti tidak ditemukan penyebutan yang diterima, bukan
fasilitas pasti tidak tersedia. Jika pengguna tidak memilih hobi, C6 ditetapkan 0.

Budget hanya membatasi **harga tiket satu destinasi per orang**. Kandidat harus
memenuhi `harga_tiket <= budget`; budget Rp0 tetap menerima destinasi gratis.
Sisa alokasi tiket adalah budget dikurangi harga tiket, bukan estimasi sisa uang
perjalanan. Jarak tidak menambah harga tiket.

## Rumus utama

### AHP

Untuk matriks perbandingan $A=[a_{ij}]$ dengan $n=6$ kriteria, normalisasi kolom
dan rata-rata baris menghasilkan bobot:

$$
b_{ij}=\frac{a_{ij}}{\sum_{p=1}^{n}a_{pj}},\qquad
w_i=\frac{1}{n}\sum_{j=1}^{n}b_{ij}
$$

Uji konsistensi mengikuti perhitungan pada aplikasi:

$$
\lambda_{\max}\approx\frac{1}{n}\sum_{i=1}^{n}\frac{(Aw)_i}{w_i},\qquad
CI=\frac{\lambda_{\max}-n}{n-1},\qquad CR=\frac{CI}{RI}
$$

Untuk enam kriteria, $RI=1{,}24$. Matriks preset digunakan jika $CR<0{,}1$.
Implementasi: [ahp.py](recommender/spk/ahp.py) dan
[profiles.py](recommender/spk/profiles.py).

### TOPSIS

Untuk $m$ alternatif dan enam kriteria, $x_{ij}$ adalah nilai alternatif $i$
pada kriteria $j$. Normalisasi dan pembobotan dihitung sebagai berikut:

$$
r_{ij}=\frac{x_{ij}}{\sqrt{\sum_{p=1}^{m}x_{pj}^{2}}},\qquad
v_{ij}=w_jr_{ij}
$$

Jika penyebut sebuah kolom nol, nilai normalisasi kolom tersebut ditetapkan 0.
Solusi ideal positif ($A^+$) mengambil nilai maksimum untuk benefit dan minimum
untuk cost; solusi ideal negatif ($A^-$) mengambil nilai sebaliknya.

$$
D_i^+=\sqrt{\sum_{j=1}^{6}(v_{ij}-A_j^+)^2},\qquad
D_i^-=\sqrt{\sum_{j=1}^{6}(v_{ij}-A_j^-)^2}
$$

$$
V_i=\frac{D_i^-}{D_i^++D_i^-}
$$

Alternatif diurutkan berdasarkan $V_i$ terbesar. Implementasi:
[topsis.py](recommender/spk/topsis.py).

### Pembentukan nilai kriteria

- **C1:** harga tiket sumber; sisa alokasi = budget − harga tiket.
- **C2:** rating model; Tahura menggunakan median 4,5, sementara rating sumber
  tetap kosong dan status imputasi ditampilkan.
- **C3:** $d=2R\arcsin(\sqrt{a})$, dengan
  $a=\sin^2(\Delta\varphi/2)+\cos\varphi_1\cos\varphi_2\sin^2(\Delta\lambda/2)$.
  Sudut dalam radian dan $R=6371$ km. Implementasi: [geo.py](recommender/spk/geo.py).
- **C4:** jumlah kelompok penyebutan fasilitas yang diterima / 6.
- **C5:** utama = 1; sekunder = 0,5; lainnya = 0. Jika kedua pilihan sama,
  kategori utama diperiksa lebih dahulu.
- **C6:** $J(H,T)=|H\cap T|/|H\cup T|$, dengan $H$ hobi pengguna dan $T$ tag
  destinasi. Alur website menetapkan C6 = 0 saat hobi pengguna kosong.
  Implementasi: [similarity.py](recommender/spk/similarity.py).

## Tahapan algoritma

### Pengolahan data dan K-Means secara offline

1. Gabungkan 437 destinasi Kaggle dan 6 kurasi Jawa, bersihkan data, bentuk
   indikator fasilitas dan tag aktivitas, lalu periksa retensi seluruh 443 ID.
2. Ekspor CSV master dan matriks fitur beserta manifest untuk validasi sumber.
3. Bentuk delapan fitur K-Means: harga dibatasi P99 Rp275.800 dan distandardisasi
   Z-score, rating model distandardisasi, serta enam kolom one-hot kategori.
   Z-score menggunakan $z=(x-\mu)/\sigma$ dengan simpangan baku populasi (`ddof=0`).
   Pembatasan P99 hanya berlaku untuk fitur pelatihan, bukan C1 TOPSIS.
4. Latih seluruh 443 destinasi dengan k-means++, 10 inisialisasi, seed 42, dan
   kandidat $k=2$ sampai $k=6$. Pilih silhouette tertinggi pada konfigurasi yang
   memenuhi ukuran minimum cluster 22 anggota. Pada data aktif, semua kandidat
   memenuhi batas tersebut.
5. Simpan label dan evaluasi model. Hasil saat ini adalah **2 cluster dengan
   414 dan 29 anggota**, serta silhouette **0,54302**. Label tersimpan dalam
   [kmeans_evaluation.json](reports/clustering/kmeans_evaluation.json).

### Perhitungan rekomendasi secara online

1. Validasi kota asal, provinsi tujuan, budget tiket, kategori, hobi, dan profil.
2. Ambil kandidat pada provinsi tujuan dengan harga tiket tidak melebihi budget.
3. Gunakan bobot AHP profil pilihan dan bentuk matriks keputusan C1–C6.
4. Normalisasi matriks, kalikan dengan bobot, dan tentukan solusi ideal TOPSIS.
5. Hitung $D_i^+$, $D_i^-$, dan $V_i$, lalu urutkan dari skor tertinggi.
6. Tampilkan maksimal 10 rekomendasi beserta rincian kriteria, sisa alokasi tiket,
   catatan kualitas data, label segmen, dan hasil pada peta.

Website juga menyediakan slider bobot. Jika diubah, bobotnya dinormalisasi agar
berjumlah 1 dan menjadi bobot langsung kustom, **bukan perhitungan AHP baru**.
CR preset tidak berlaku untuk bobot slider. Jika semua slider nol, aplikasi
kembali menggunakan bobot profil. Penjelasan profil dan contoh di atas memakai
bobot preset.

## Interpretasi hasil SPK

- **Skor lebih tinggi** berarti alternatif lebih dekat dengan solusi ideal
  relatif terhadap kandidat, bobot, dan preferensi pada permintaan tersebut.
  Skor 0,8 tidak berarti akurasi atau kepuasan pengguna sebesar 80%.
- **Peringkat dapat berubah** jika budget, wilayah, kategori, hobi, kota asal,
  atau profil berubah. Hasil bukan penilaian destinasi terbaik untuk semua orang.
- **Label cluster** menjelaskan kemiripan destinasi, bukan urutan rekomendasi.
  Silhouette 0,54302 adalah ukuran evaluasi internal clustering, bukan akurasi SPK.
- **Kandidat kosong** menghasilkan pesan tanpa rekomendasi. Jika hanya satu
  kandidat atau semua kandidat identik, implementasi memberi $V_i=1$ untuk
  menghindari pembagian nol; nilai itu bukan kualitas sempurna.
- **Catatan kualitas** tetap perlu dibaca: rating Tahura diimputasi, koordinat
  Pelabuhan Marina perlu ditinjau, fasilitas dan tag aktivitas berasal dari
  deskripsi, serta harga merupakan snapshot sumber.

## Data dan status implementasi

- [CSV hasil preprocessing](data/processed/destinations_clean_java443.csv)
  memuat seluruh 443 destinasi; [CSV fitur K-Means](data/processed/destinations_kmeans_features_java443.csv)
  memuat fitur pelatihan.
- [JSON model](reports/clustering/kmeans_evaluation.json) memuat label seluruh
  destinasi. `place_id` pada CSV cocok dengan `source_id` pada assignment JSON.
- Website saat ini menggunakan **Django + SQLite + Python**, dengan Django
  Template, HTML, CSS, dan JavaScript native. CSV menjadi artefak preprocessing
  yang diimpor ke database; hasil cluster juga disimpan ke database.
- Pembacaan CSV + JSON langsung tanpa database sudah menjadi rencana perubahan,
  tetapi **belum diterapkan pada kode website**. Status ini tidak mengubah rumus SPK.

Sumber dan batasan atribut tersedia di [Dokumentasi.md](Dokumentasi.md).
Bukti perhitungan tersedia pada [Excel AHP–TOPSIS](outputs/excel_spk_20261005/Perhitungan_AHP_TOPSIS_TravelFit.xlsx)
dan [laporan UTS](outputs/uts_travelfit/Laporan_UTS_TravelFit.docx).

<details>
<summary>Panduan menjalankan aplikasi dan preprocessing</summary>

## Menjalankan lokal

Python 3.11+ diperlukan; gunakan virtual environment yang tersedia atau buat baru.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe manage.py preprocess_destinations
.venv/Scripts/python.exe manage.py import_destinations --backup-only
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py import_destinations --dry-run
.venv/Scripts/python.exe manage.py import_destinations
.venv/Scripts/python.exe manage.py train_clusters --dry-run
.venv/Scripts/python.exe manage.py train_clusters
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000
```

Urutan backup sebelum migrate penting untuk database lama. Impor nyata menulis
backup SQLite lokal sebelum upsert dan menghapus record di luar ID aktif secara
atomik. Impor ulang tidak menggandakan destinasi. Jika sumber berubah, ulangi
preprocessing → impor → training; importer/trainer menolak artifact yang usang.
`--project-root PATH` tersedia untuk ketiga command pipeline. `--dry-run` tidak
mengubah destinasi/label/laporan; preprocessing memang mengekspor output.

Halaman: [rekomendasi](http://127.0.0.1:8000/),
[peta Jawa](http://127.0.0.1:8000/peta/), [metode & data](http://127.0.0.1:8000/tentang/).
Server development bukan konfigurasi deployment publik; jangan mengaktifkan
DEBUG atau memakai secret development sebagai konfigurasi produksi.

## Google Colab / Drive Saya → TravelFit

Buka `notebooks/01_preprocessing_travelfit.ipynb`. Di Colab folder dasar:
`/content/drive/MyDrive/TravelFit`. Pertahankan struktur berikut, bukan hanya upload
notebook atau CSV tunggal:

```text
TravelFit/
  recommender/data_pipeline.py
  data/raw/tourism_with_id.csv
  data/raw/tourism_rating.csv
  data/review/gabungan_jawa/destinasi_jawa_review.csv
  data/review/gabungan_jawa/google_maps_rating_review.json
  notebooks/01_preprocessing_travelfit.ipynb
```

Notebook memanggil modul yang sama dengan aplikasi, tidak mengunduh kode remote.
Jika modul/sumber belum tersedia, notebook berhenti dengan pesan file wajib.
File sumber disimpan di Drive sehingga tidak perlu upload ulang setiap runtime.
Mount Drive tetap memerlukan login/otorisasi Colab. Output disimpan ke
`data/processed/` dan `reports/preprocessing/` di folder TravelFit.

## Pengujian

```powershell
.venv/Scripts/python.exe manage.py test recommender.tests --noinput
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

Tes menggunakan database sementara dan mencakup preprocessing, impor, training,
serta rekomendasi/peta. Kelulusan tes memeriksa fungsi aplikasi, bukan membuktikan
tarif terkini atau kepuasan pengguna. Peta SVG merupakan visualisasi skematis;
daftar tetap memuat 443 destinasi, dengan 442 titik dalam bingkai Jawa karena
koordinat Marina berada di luar bingkai.

</details>
