# TravelFit — Rekomendasi Destinasi Wisata Jawa

TravelFit membantu memilih tujuan berdasarkan budget tiket dan preferensi menggunakan
CRISP-DM, K-Means, serta AHP–TOPSIS. Stack tetap **Django + SQLite + Python**,
frontend template HTML, CSS dan JavaScript native. Branch integrasi: `new`.

Dataset aktif **443 = 437 Kaggle + 6 kurasi Jawa**; semua ID dipertahankan dan
semuanya dilatih K-Means. Data sintetis 1900/2337 sudah menjadi arsip, tidak lagi
dibaca website. “Kurasi” tidak berarti seluruh atribut resmi atau terverifikasi
lapangan. Penjelasan sumber/bukti/keterbatasan: [Dokumentasi.md](Dokumentasi.md).

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

## Alur perhitungan

1. **Business Understanding:** memilih tujuan Jawa sesuai preferensi, bukan satu
   destinasi terbaik untuk semua wisatawan.
2. **Data Understanding:** pahami snapshot Kaggle, tarif peraturan, lokasi OSM,
   rating Google Maps, nilai kosong dan konflik sumber.
3. **Data Preparation:** normalisasi, agregat interaksi, fitur deskripsi, median
   model Tahura, Z-score dan one-hot; tetap443 ID dan manifest ber-hash.
4. **Modeling:** K-Means443 offline untuk segmen, AHP preset untuk bobot,
   TOPSIS untuk ranking kandidat sesuai budget/wilayah. K-Means tidak menggantikan
   TOPSIS atau menentukan bobot pengguna.
5. **Evaluation:** k2–6/inertia/silhouette/ukuran cluster, retensi, idempotensi,
   rollback, edge cases dan sensitivitas. Evaluasi survei belum dilakukan.
6. **Deployment:** Django membaca artifact pipeline tervalidasi, menampilkan
   hasil, sumber dan catatan kualitas; map/form server tetap berguna tanpa JS.

Fitur K-Means: harga tiket p99+Z-score, rating model+Z-score, one-hot kategori.
C4 bukan fitur clustering. Snapshot menghasilkan k2, silhouette0,54302,
cluster414/29; **bukan akurasi rekomendasi**.

| Kriteria SPK runtime | Jenis | Nilai |
| --- | --- | --- |
| C1 Harga tiket | Cost | Harga sumber satu destinasi per orang, tanpa cap p99 |
| C2 Rating | Benefit | Rating teramati atau imputasi model yang ditandai |
| C3 Jarak garis lurus | Cost | Haversine dari koordinat kota asal, bukan jarak jalan |
| C4 Fasilitas | Benefit | Penyebutan deskripsi diterima /6, bukan kelengkapan lapangan |
| C5 Kategori | Benefit | Utama1, sekunder0,5, lainnya0 |
| C6 Hobi | Benefit | Jaccard hobi dan tag aktivitas |

Budget adalah **batas harga tiket satu destinasi per orang**, bukan budget perjalanan.
Kandidat harus memenuhi `harga_tiket <= budget`. Nilai0 menerima destinasi gratis.
Sisa alokasi tiket = budget − tiket, bukan estimasi uang perjalanan yang tersisa.
Transportasi, makan, penginapan dan moda tidak digunakan. Jarak garis lurus tidak
menjadi estimasi ongkos. Harga snapshot perlu diperiksa sebelum berkunjung.
Tahura: rating sumber kosong, median4,5 hanya untuk model. MarinaID9 tetap ada,
koordinat luar Jawa ditandai; jaraknya perlu review. AHP empat preset
pengembang CR<0,1 **belum hasil survei**; slider merupakan uji sensitivitas.

## Struktur aktif

```text
recommender/data_pipeline.py                 # satu transformasi bersama
recommender/management/commands/             # preprocess/import/train
recommender/spk/                             # AHP, TOPSIS, geografi, kemiripan
recommender/templates/recommender/           # base, form, hasil, peta, metode
recommender/static/recommender/              # travelfit dan java-map lokal
notebooks/01_preprocessing_travelfit.ipynb    # notebook tipis
data/raw/                                   # sumber Kaggle tidak diubah
data/review/                                 # kurasi + salinan bukti
data/processed/destinations_*_java443.csv     # master dan fitur aktif
reports/preprocessing/preprocessing_java443* # summary & manifest
reports/clustering/kmeans_evaluation.json    # evaluasi/label seluruh443
archive/legacy/                             # workflow/prototipe/output lama
archive/local_backups/                      # backup DB, tidak masuk Git
```

Peta memuat enam provinsi; SVG dan posisi titik adalah pendekatan visual, bukan
GIS/navigasi atau audit batas. Daftar tetap443, titik442 karena Marina di luar
bingkai. Kota asal di seluruh Indonesia masih sah meskipun tujuan hanya Jawa.
Retensi ID tidak menghapus alias atau membuktikan data representatif seluruh Jawa.

## Pengujian / keamanan data

```powershell
.venv/Scripts/python.exe manage.py test recommender.tests --noinput
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

Tes menggunakan database sementara, termasuk alur preprocessing → impor →
training → rekomendasi/peta. Website tidak memanggil routing eksternal untuk rekomendasi. Tes modul biaya dan
routing lama tetap disimpan sebagai pengujian kode historis yang tidak aktif;
kelulusan tes tidak membuktikan tarif terkini atau hasil survei.
Hash file sumber/bukti dan DOCX dijaga. CSRF tetap aktif; data JSON memakai
`json_script`, bukan interpolasi HTML yang tidak di-escape.

Desain mengikuti UI-UX Pro Max: hierarki krem–teal, label native, fokus/error yang
jelas, progressive enhancement; [keputusan & verifikasi UI](docs/design/travelfit-java-ui.md).
[Daftar cleanup dan recovery](docs/maintenance/java443-cleanup.md).

Laporan aktif: [Laporan UTS](outputs/uts_travelfit/Laporan_UTS_TravelFit.docx).
Bukti formula aktif: [Excel AHP–TOPSIS](outputs/excel_spk_20261005/Perhitungan_AHP_TOPSIS_TravelFit.xlsx).
[Keputusan budget tiket](docs/decisions/2026-10-05-ticket-budget.md) dan
[rencana pengelompokan pengalaman](docs/IMPLEMENTATION_PLAN_ONTOLOGY.md).
`Laporan_SPK_TravelFit.docx` di root tetap merupakan dokumen historis, bukan laporan aktif.
`Perhitungan_SPK_TravelFit.xlsx` tetap sebagai referensi historis, bukan input produksi.
Review open-data historis ada di `scripts/open_data_review`, terisolasi dari website;
default fixture1900 berada di arsip. Tidak ada push/deploy otomatis pada task ini.
