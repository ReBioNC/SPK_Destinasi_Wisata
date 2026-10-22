# TravelFit — Cheatsheet

> Sistem Pendukung Keputusan rekomendasi destinasi wisata Jawa.
> **Django 5.2 + SQLite + Python 3.11** · AHP (bobot) → TOPSIS (peringkat) · K-Means (segmen, bukan peringkat)
> Data aktif **443 destinasi Jawa** (437 Kaggle + 6 kurasi) · branch aktif: `new`
> Teori lengkap: [README.md](../README.md) · Sumber & batasan atribut: [Dokumentasi.md](../Dokumentasi.md)

---

## 1. Setup

```powershell
# dari root repo
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Aktifkan venv (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\.venv\Scripts\Activate.ps1
```

Atau tanpa aktivasi, pakai path langsung: **`.venv/Scripts/python.exe`** — dipakai di semua perintah di bawah.

### Environment variables (`config/settings.py`)

| Var | Default | Catatan |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | key dev lokal | **Wajib** kalau `DEBUG` dimatikan, kalau tidak `ImproperlyConfigured` |
| `DJANGO_DEBUG` | `1` | Isi `0` untuk non-debug |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Pisahkan dengan koma |

---

## 2. Perintah harian

```powershell
# jalankan server
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000

# tes (188 test method, DB sementara)
.venv/Scripts/python.exe manage.py test recommender.tests --noinput

# sanity check
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run

# shell interaktif
.venv/Scripts/python.exe manage.py shell

# admin
.venv/Scripts/python.exe manage.py createsuperuser   # app 'admin' TIDAK terpasang
```

### Halaman

| URL | Nama route | View | Isi |
| --- | --- | --- | --- |
| `/` | `beranda` | `views.rekomendasi` | Form preferensi + hasil TOP 10 |
| `/peta/` | `peta` | `views.peta` | Peta SVG Jawa + hasil terakhir |
| `/tentang/` | `tentang` | `views.tentang` | Metodologi + tautan bukti |

---

## 3. Pipeline data (3 langkah, urut)

Jalankan ulang **preprocess → import → train** setiap sumber data berubah.
Importer & trainer **menolak artifact usang** (fingerprint tidak cocok).

```powershell
# 1) Preprocessing -> CSV + manifest
.venv/Scripts/python.exe manage.py preprocess_destinations

# 2) Backup DB (WAJIB sebelum migrate pada DB lama)
.venv/Scripts/python.exe manage.py import_destinations --backup-only
.venv/Scripts/python.exe manage.py migrate

# 3) Impor (upsert atomik + hapus ID di luar daftar aktif)
.venv/Scripts/python.exe manage.py import_destinations --dry-run
.venv/Scripts/python.exe manage.py import_destinations

# 4) Training K-Means -> label cluster
.venv/Scripts/python.exe manage.py train_clusters --dry-run
.venv/Scripts/python.exe manage.py train_clusters
```

Ketiga command menerima `--project-root PATH`.
`--dry-run` tidak mengubah destinasi/label; preprocessing tetap mengekspor output.

### Flag management command

| Command | Flag |
| --- | --- |
| `preprocess_destinations` | `--project-root` |
| `import_destinations` | `--project-root`, `--dry-run`, `--backup-only` |
| `train_clusters` | `--dry-run`, `--project-root` |

### Artifact hasil pipeline

| Path | Isi |
| --- | --- |
| `data/processed/destinations_clean_java443.csv` | 443 destinasi (master) |
| `data/processed/destinations_kmeans_features_java443.csv` | 8 fitur pelatihan |
| `reports/preprocessing/preprocessing_java443_manifest.json` | fingerprint + retensi ID |
| `reports/clustering/kmeans_evaluation.json` | label cluster + metrik evaluasi |

> Kunci join: `place_id` (CSV) = `source_id` (Destination) = `source_id` (JSON assignment).

### Kurasi open data (terpisah dari pipeline app)

```powershell
.venv/Scripts/python.exe -m scripts.open_data_review.cli `
  --osm-json <overpass.json> `
  --geonames-zip <ID.zip> `
  --evidence-csv <evidence.csv> `
  --output-dir data/review
```

Default: `--legacy-xlsx archive/legacy/Dataset_Wisata_38_Provinsi.xlsx`,
`--kaggle-csv data/raw/tourism_with_id.csv`.

---

## 4. Struktur direktori

```text
config/            settings.py, urls.py, wsgi/asgi       # proyek Django
recommender/       app utama
  models.py        Destination, JarakCache
  views.py         rekomendasi, peta, tentang
  forms.py         PreferensiForm (budget, kota, provinsi, kategori, hobi, profil, slider w1..w6)
  urls.py          3 route
  data_pipeline.py preprocess bersama (PIPELINE_VERSION = "java443-v1")
  kota_asal.py     muat data/kota_indonesia.csv -> KOTA_ASAL, PROVINSI_KOTA
  spk/             ahp, topsis, geo, similarity, profiles, validation, biaya
  management/commands/  preprocess_destinations, import_destinations, train_clusters
  templates/ static/    HTML/CSS/JS native (tanpa framework)
  tests/           20 file, 188 test method
scripts/open_data_review/   CLI kurasi OSM + GeoNames
data/raw|review|processed|  sumber, bukti kurasi, output pipeline
data/kota_indonesia.csv     koordinat kota asal
notebooks/         01 (Colab), 02 (cleaning lengkap), 03 (simple)
reports/           laporan audit, clustering, preprocessing
outputs/           laporan UTS, Excel AHP-TOPSIS, jadwal, QA page PNG
docs/              keputusan, desain, rencana, specs/  ← file ini
archive/legacy/    dataset & kode versi lama (jangan diedit)
```

---

## 5. Kriteria SPK (C1–C6)

`IS_COST = [True, False, True, False, False, False]` di `spk/profiles.py`.
`NAMA_KRITERIA = ["Harga tiket", "Rating", "Jarak", "Fasilitas", "Kategori", "Hobi"]`.

| Kode | Kriteria | Jenis | Sumber nilai | Implementasi |
| --- | --- | --- | --- | --- |
| C1 | Harga tiket | cost | `harga_tiket` (snapshot sumber) | field DB |
| C2 | Rating model | benefit | `rating_model`, fallback `rating`; harus 1–5 | `Destination.calculation_rating()` |
| C3 | Jarak garis lurus | cost | Haversine, R = 6371 km | `spk/geo.py` |
| C4 | Fasilitas | benefit | 6 grup penyebutan / 6 | `Destination.facility_score()` |
| C5 | Kecocokan kategori | benefit | utama 1, sekunder 0,5, lain 0 | `views._skor_c5()` |
| C6 | Kecocokan hobi | benefit | Jaccard; **0 jika user tidak pilih hobi** | `spk/similarity.py` |

Fasilitas (C4): `toilet, parkir, warung, mushola, accessibility, information_center`
— `fas_penginapan` ada di model tapi **tidak** masuk hitungan C4.

### Rumus (ringkas)

```text
AHP :  wij = 1/n * Σj (aij / Σp apj)
      λmax ≈ (1/n) Σi (Aw)i / wi ;  CI = (λmax - n)/(n-1) ;  CR = CI / RI
      n = 6  ->  RI = 1,24  ;  matriks dipakai bila CR < 0,1

TOPSIS: rij = xij / sqrt(Σp xpj²)   (penyebut 0 -> 0)
        vij = wj * rij
        A+ = max benefit / min cost      A- = kebalikan
        Vi = D- / (D+ + D-)              (D+ + D- = 0 -> Vi = 1)
```

### Profil bobot preset

| Key | Label | Dominan | CR |
| --- | --- | --- | --- |
| `seimbang` | Seimbang (kuesioner 28 responden) | Kategori 26% | 0,060147 |
| `hemat` | Hemat | Harga tiket | 0,002559 |
| `kualitas` | Kualitas | Rating | 0,012159 |
| `petualang` | Petualang | Jarak / kategori / hobi | 0,004431 |

Matriks Saaty ada di `spk/profiles.py::PROFILE_UPPERS` (segitiga atas; bawah resiprokal).
Tambah profil baru → cukup isi `PROFILE_UPPERS` + `PROFILE_LABELS`; `ACTIVE_PROFILES`
hanya memuat profil dengan `CR < 0,1`.

### Slider bobot

`w1..w6` + hidden `sentuh_bobot`. Jika `sentuh_bobot == "1"`:
bobot slider dipakai langsung (dinormalisasi jumlah 1) → **bukan AHP baru, CR preset tidak berlaku**.
Semua slider nol → jatuh ke bobot profil.

---

## 6. Alur request `rekomendasi()`

```text
GET/POST /
  ├─ _dataset_state()        -> data_count, source_counts, dataset_fingerprint, province_count
  ├─ _sync_session()         -> cache state di session
  ├─ _daftar_pilihan()       -> daftar provinsi / kategori / tag Dari DB
  ├─ form valid?
  │    └─ tidak -> render beranda (atau JSON 400 bila AJAX)
  ├─ bobot = profil preset; slider bisa override
  ├─ kandidat = Destination.filter(provinsi=..., harga_tiket__lte=budget,
  │                                latitude__isnull=False, longitude__isnull=False)
  ├─ matriks [C1..C6] per kandidat
  ├─ topsis.rank(... )[:10]  (TOP_N = 10)
  └─ simpan session: preference_input, hasil_terakhir, flash_hasil
       POST-redirect-GET  -> hasil tampil sekali, refresh bersih
```

Session keys: `preference_input`, `flash_hasil` (sekali pakai), `hasil_terakhir`.

### AJAX

Header `X-Requested-With: XMLHttpRequest` → `JsonResponse`:
`{ok, count, html, map_html}`. Error form → `{ok:false, errors, labels, pesan}` status 400.

---

## 7. Model

`Destination` — kunci alami unik `(nama, kota)`; `source_id` unique nullable.
Kelompok field: identitas (`nama, kota, provinsi, kategori, sub_kategori`), harga/rating,
`provenance` & `data_quality` (JSONField), `pipeline_fingerprint`,
koordinat, 7 flag fasilitas, `tag_aktivitas` (string dipisah `|`),
`cluster_label`, `sumber_data`.

`JarakCache` — cache jarak darat (OSRM, throttle 1 req/detik), unik `(asal, tujuan, moda)`.

Method penting: `facility_score()`, `calculation_rating()` (validasi 1–5, else `ValueError`), `tag_set()`.

---

## 8. K-Means (clustering, bukan SPK)

| Parameter | Nilai |
| --- | --- |
| Fitur | 8 = harga (cap **P99 Rp275.800** + Z-score), rating (Z-score), 6 one-hot kategori |
| Z-score | `(x - μ)/σ`, σ populasi (`ddof=0`) |
| Inisialisasi | k-means++, 10 inisialisasi, **seed 42** |
| Kandidat k | 2–6, pilih silhouette tertinggi |
| Syarat | ukuran minimum cluster **22 anggota** |
| Hasil aktif | **2 cluster (414 & 29)**, silhouette **0,54302** |

> Cap P99 **hanya untuk fitur pelatihan**, bukan untuk C1 TOPSIS.
> Label cluster tidak menyaring kandidat TOPSIS dan tidak menentukan bobot AHP.

---

## 9. Testing & QA

```powershell
.venv/Scripts/python.exe manage.py test recommender.tests --noinput     # 188 test
.venv/Scripts/python.exe manage.py test recommender.tests.test_spk      # satu modul
.venv/Scripts/python.exe manage.py test recommender.tests.test_java443_workflow -v 2
```

| File test | Fokus |
| --- | --- |
| `test_spk.py` | AHP, TOPSIS, geometri, Jaccard |
| `test_data_pipeline.py`, `test_preprocessing_*.py` | Preprocessing, retensi ID, entrypoint |
| `test_import.py`, `test_java443_import.py` | Impor atomik, backup, fingerprint |
| `test_java443_training.py`, `test_clustering.py` | Latih K-Means, evaluasi |
| `test_views.py`, `test_java_ui.py`, `test_java_map.py`, `test_java_map.py` | View, template, peta |
| `test_ticket_budget.py`, `test_biaya.py`, `test_jarak.py` | Budget tiket, biaya, jarak |
| `test_transport.py`, `test_pulau_cache.py` | Transport & cache pulau |
| `test_open_data_review.py` | Kurasi OSM/GeoNames |

Lolos tes = fungsi aplikasi benar, **bukan** bukti tarif terkini atau kepuasan pengguna.

---

## 10. Jebakan yang sering terjadi

| Jebakan | Aturan |
| --- | --- |
| Mengira skor = akurasi | `Vi = 0,8` bukan "80% puas". Skor relatif terhadap kandidat & bobot.request |
| Mengira cluster = peringkat | K-Means hanya label kemiripan fitur |
| Mengubah budget jadi total perjalanan | Budget = **harga tiket 1 destinasi/orang**; sisa = budget − tiket, bukan sisa uang perjalanan |
| Menambah tarif transport ke C1 | Jarak tidak menambah harga tiket; C3 murni Haversine |
| Slider dianggap AHP | Slider = bobot langsung, CR preset tidak berlaku |
| Menghapus `fas_penginapan` | Field ada tapi sengaja di luar 6 penyebut C4 |
| Lupa `--backup-only` sebelum `migrate` | Urutan backup penting untuk DB lama |
| Impor tanpa `--dry-run` dulu | Cek jumlah kandidat & fingerprint sebelum menulis |
| Mengedit `archive/legacy/` | Arsip read-only; importer baca default `--legacy-xlsx` dari sana |
| Menghapus `tmp*` tapi belum dicek | 30+ folder `tmp*` kosong di root — sisa proses, aman dihapus |

---

## 11. Modul yang ada tapi tidak dipakai alur ranking

| Modul | Fungsi | Status |
| --- | --- | --- |
| `recommender/jarak.py` | Jarak darat OSRM + cache | tidak dipakai C3 (C3 = Haversine) |
| `recommender/transport.py` | Rencana perjalanan (darat/pesawat/feri) | tidak dipakai di `views.py` |
| `spk/biaya.py` | Tarif & estimasi biaya | tidak dipakai di `views.py` |
| `spk/validation.py` | `saw_rank`, `spearman` (cross-check) | bukan metode output |

`views.py` hanya mengimpor `geo, profiles, similarity, topsis`.

---

## 12. Peta (SVG skematis, bukan GIS)

`views._map_context()` memproyeksikan koordinat affine di вокруг Monas:

```text
x = 260 + (lon - 106.827153) * 21.3
y = 309 + (-lat - 6.175392) * 24.3
bingkai: 220 <= x <= 462,  287 <= y <= 384
```

Koordinat tampilan **tidak** menimpa koordinat geografis di DB.
443 destinasi tetap terdaftar; 442 titik dalam bingkai (Pelabuhan Marina di luar).

---

## 13. Git

```powershell
git status                     # harus bersih sebelum commit
git log --oneline -10
git switch new                 # branch aktif
```

`.gitignore`: `.venv/`, `.superpowers/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `node_modules/`, `archive/local_backups/`.
`db.sqlite3` **tidak** di-commit — backup lokal dibuat oleh `import_destinations --backup-only`.

---

## 14. Dokumen penting

| File | Isi |
| --- | --- |
| [README.md](../README.md) | Teori lengkap, rumus, cara menjalankan |
| [Dokumentasi.md](../Dokumentasi.md) | Sumber data & batasan atribut |
| [docs/decisions/2026-10-05-ticket-budget.md](../docs/decisions/2026-10-05-ticket-budget.md) | Keputusan budget tiket |
| [docs/decisions/2026-09-30-c4-description-indicator.md](../docs/decisions/2026-09-30-c4-description-indicator.md) | C4 dari deskripsi |
| [docs/decisions/2026-09-30-tahura-median-and-marina-retention.md](../docs/decisions/2026-09-30-tahura-median-and-marina-retention.md) | Imputasi rating Tahura, retensi Marina |
| [docs/design/travelfit-java-ui.md](../docs/design/travelfit-java-ui.md) | Desain UI |
| [docs/maintenance/java443-cleanup.md](../docs/maintenance/java443-cleanup.md) | Catatan cleanup Java443 |
| `docs/superpowers/specs/` + `plans/` | Spec & rencana 3 iterasi (Django, kurasi, Java443) |
| `outputs/excel_spk_20261005/Perhitungan_AHP_TOPSIS_TravelFit.xlsx` | Bukti hitung AHP–TOPSIS |
| `outputs/uts_travelfit*/` | Laporan UTS (.docx) |

### Identitas kelompok

| Nama | NIM |
| --- | --- |
| Kristofer Ryan Giggs Eka Saputra | 412024005 |
| Cristian Dion | 412024006 |
| Reynard Liu | 412025022 |
| Justin Augusto Liustri | 412025029 |