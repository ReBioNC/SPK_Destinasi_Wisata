# Spec Desain: Website TravelFit (Django + Django Templates)

- Tanggal: 2026-09-25
- Status: disetujui pengguna (pendekatan A, Bagian 1–4)
- Jalur brainstorming: architectural

## 1. Ringkasan Intent

Membangun website Sistem Pendukung Keputusan rekomendasi destinasi wisata
TravelFit. Pengguna mengisi preferensi (budget maksimal, kota asal, wilayah
tujuan, kategori utama/sekunder, hobi, profil prioritas), sistem meranking
destinasi dengan AHP–TOPSIS lalu menampilkan Top-10 beserta skor Vi dan alasan
per kriteria. Scope versi pertama: form + hasil, peta interaktif, dan slider
sensitivity analysis. Tanpa login. Bahasa Indonesia.

Keputusan pengguna yang mengunci desain:

1. Scope: inti + peta & sensitivitas (tanpa admin CRUD).
2. Data: gabungan — XLSX 38 provinsi (1.900 destinasi) sebagai basis,
   dilengkapi CSV olahan Jawa (437 destinasi + rating agregat).
3. Database & akun: SQLite, publik tanpa login.
4. UI: Bootstrap 5 via CDN, Bahasa Indonesia.

Pendekatan terpilih: **A — Django klasik, engine SPK Python stdlib**
(tanpa numpy/pandas di runtime). Pendekatan B (endpoint JSON real-time) dan
C (stateless tanpa DB) ditolak dengan alasan tercatat di riwayat diskusi.

## 2. Arsitektur & Komponen

```text
SPK_Destinasi_Wisata/
├── config/                  # Django project: settings, urls, wsgi
├── recommender/             # Satu-satunya app
│   ├── models.py            # Model Destination
│   ├── views.py             # rekomendasi, peta, tentang
│   ├── urls.py              # 3 rute
│   ├── forms.py             # Form preferensi + validasi ID
│   ├── spk/                 # Engine murni stdlib (tanpa Django/pandas)
│   │   ├── __init__.py
│   │   ├── geo.py           # haversine(lat1, lon1, lat2, lon2) -> km
│   │   ├── similarity.py    # jaccard(set_a, set_b) -> float
│   │   ├── ahp.py           # bobot_dari_matriks(), uji_konsistensi()
│   │   ├── topsis.py        # rank(matriks, bobot, jenis) -> Vi, D+, D-, kontribusi
│   │   ├── validation.py    # saw.rank(), spearman() — internal saja
│   │   └── profiles.py      # Konstanta 4 profil + matriks pasangannya
│   ├── management/commands/
│   │   └── import_destinations.py
│   ├── tests/
│   │   ├── test_spk.py
│   │   └── test_views.py
│   └── templates/recommender/
│       ├── base.html
│       ├── form_hasil.html
│       ├── peta.html
│       └── tentang.html
├── data/                    # Sumber impor (file yang sudah ada)
└── static/recommender/      # 1 file CSS custom (+ Bootstrap via CDN)
```

Batasan arsitektur:

- `recommender/spk/` tidak boleh mengimpor Django, pandas, atau numpy.
  Alasannya: engine harus dapat diuji dan direproduksi independen
  (kebutuhan validasi Bab 3 laporan).
- Satu halaman form + hasil (`form_hasil.html`): form di atas, kartu hasil
  di bawah. Tidak ada SPA, tidak ada framework JS.

## 3. Aliran Data

1. GET `/` → form kosong (opsi kategori, hobi, profil dari konstanta).
2. POST `/` → validasi form → filter keras di ORM
   (`harga_tiket <= budget`, `provinsi == wilayah`) → matriks C1–C6
   dibangun di memori (C3 via Haversine dari kota asal, C6 via Jaccard).
3. Bobot: preset profil dari `profiles.py`; jika slider disentuh, bobot
   kustom menimpa preset (dinormalisasi ulang ke jumlah 1).
4. `topsis.rank()` → Top-10 + kontribusi per kriteria → render kartu hasil
   (nama, Vi 4 desimal, label cluster, kalimat alasan unggul/tertahan).
5. ID hasil disimpan di session → `/peta/` menampilkan marker dari hasil
   terakhir, fallback ke seluruh dataset bila session kosong.

## 4. Model Database

Model tunggal `Destination` (SQLite):

| Field | Tipe | Keterangan |
|---|---|---|
| nama | CharField(200) | bagian natural key |
| kota | CharField(100) | bagian natural key |
| provinsi | CharField(100), db_index | filter keras wilayah |
| kategori | CharField(50), db_index | kategori utama |
| sub_kategori | CharField(100), null | detail |
| harga_tiket | IntegerField, db_index | C1 (Rp) |
| rating | FloatField | C2 (1–5) |
| latitude, longitude | FloatField | C3 |
| fas_toilet, fas_parkir, fas_warung, fas_mushola, fas_penginapan | BooleanField | C4 |
| tag_aktivitas | TextField | pipe-separated, C6 |
| cluster_label | CharField(100), null | label K-Means interpretatif |
| sumber_data | CharField(20) | `xlsx38` atau `csv_jawa` |

Natural key unik: `(nama, kota)`. Tidak ada model User (tanpa login).

## 5. Impor Data

Command `python manage.py import_destinations`:

1. Baca `Dataset_Wisata_38_Provinsi.xlsx` (sheet `Destinasi_TravelFit_Ready`)
   → 1.900 baris basis (`sumber_data='xlsx38'`).
2. Baca `data/processed/destinations_clean.csv` + rating agregat → timpa/
   lengkapi baris yang cocok natural key (`sumber_data='csv_jawa'`).
3. Idempoten: rerun menimpa, tidak menduplikasi.
4. Cetak ringkasan (jumlah baris, provinsi, per sumber) untuk dikutip di
   laporan Bab 3.
5. Dependensi impor (openpyxl/pandas) hanya dipakai di command ini, bukan
   di runtime web.

## 6. Views, URL, Template

Rute (`config/urls.py` → `recommender/urls.py`):

| Rute | View | Fungsi |
|---|---|---|
| `/` | `rekomendasi` | GET form kosong; POST hitung + render hasil |
| `/peta/` | `peta` | Peta interaktif + marker hasil terakhir |
| `/tentang/` | `tentang` | Metodologi singkat + link spreadsheet/README |

Template (Bootstrap 5 CDN + `static/recommender/custom.css`):

- `base.html`: navbar (Beranda, Peta, Tentang), container, footer.
- `form_hasil.html`: form (budget, kota asal, wilayah, kategori
  utama/sekunder, hobi checkboxes, profil radio, slider bobot opsional)
  + kartu Top-10 (nama, Vi, label cluster, alasan per kriteria).
- `peta.html`: adaptasi `index.html` yang ada ke sintaks
  `{% static %}` + marker dinamis.
- `tentang.html`: ringkasan CRISP-DM/AHP/TOPSIS + tautan file bukti.

## 7. Detail Engine SPK

- `ahp.bobot_dari_matriks(matriks)`: normalisasi kolom + rata-rata baris.
- `ahp.uji_konsistensi()`: CI, CR dengan RI(n=6)=1,24; valid jika CR < 0,1.
- Profil Seimbang memakai angka aktual spreadsheet
  (C1=0,2693; C2=0,1785; C3=0,1567; C4=0,0820; C5=0,1567; C6=0,1567;
  CR=0,0084). Tiga profil lain (Hemat, Kualitas, Petualang) memakai matriks
  rancangan dan **otomatis dinonaktifkan** bila CR ≥ 0,1.
- `topsis.rank()`: normalisasi vektor, pembobotan, A+/A− (cost/benefit),
  D+/D− Euclidean, Vi; kembalikan juga kontribusi per kriteria untuk
  explainability.
- `validation.py` (SAW + Spearman) hanya dipakai di test/cangkang Django,
  tidak diekspos ke pengguna.

## 8. Error Handling

1. Budget non-angka/negatif → error form Bahasa Indonesia, tanpa 500.
2. Kandidat kosong setelah filter → hasil ramah ("longgarkan
   budget/wilayah") + saran konkret.
3. Jumlah bobot slider 0 → tolak dengan pesan, pakai preset profil.
4. Session peta kosong → fallback seluruh dataset.
5. CR profil rancangan ≥ 0,1 → profil nonaktif + peringatan console.

## 9. Testing & Kriteria Lolos

- `tests/test_spk.py`: data A1–A10 spreadsheet — assert urutan TOPSIS sama
  dengan Excel (10/10), CR Seimbang ≈ 0,0084, Jaccard contoh = 0,5,
  Haversine A1 ≈ 36,57 km.
- `tests/test_views.py`: POST valid → 200 + 10 hasil; POST budget tak valid
  → pesan ramah; GET `/peta/`, `/tentang/` → 200.
- Kriteria lolos: `python manage.py test` hijau + cek manual
  form → hasil → peta di browser.

## 10. Di Luar Scope (YAGNI)

Login/register, admin CRUD destinasi, endpoint JSON/real-time tanpa reload,
multi-bahasa, PostgreSQL, framework JS. Semua dapat ditambah kemudian tanpa
mengubah `recommender/spk/` karena engine terisolasi.
