# Dokumentasi data aktif TravelFit — 466 destinasi Jawa

Status integrasi 19 November 2026: **437 Kaggle + 6 kurasi Jawa + 23 kurasi Jawa
November 2026 = 466**. Seluruh ID 1–466 dipertahankan dalam preprocessing, database, dan training.
Dataset sintetis 1900 tidak menjadi sumber aktif. Folder review menyimpan
snapshot serta catatan pada saat pengumpulan; pernyataan “belum integrasi” di
catatan lama menggambarkan tahap sebelumnya, bukan status aplikasi sekarang.

## Sumber dan bukti

1. [Indonesia Tourism Destination — Kaggle](https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination):
   `data/raw/tourism_with_id.csv` (437 objek) dan `tourism_rating.csv` (interaksi).
   Harga/rating adalah snapshot dataset, bukan pengesahan resmi pemerintah atau
   harga transaksi terkini. Lima **kota** asal dataset tidak sama dengan lima
   provinsi; cakupannya tidak mewakili seluruh destinasi setiap provinsi Jawa.
2. `data/review/gabungan_jawa/destinasi_jawa_review.csv`: 6 tambahan dengan format
   Kaggle. Tarif dasar berasal dari dokumen peraturan; lokasi dari OSM.
   Deskripsi/kategori adalah kurasi, bukan observasi fasilitas di lapangan.

| ID | Destinasi | Tarif dasar | Bukti tarif / halaman PDF | Bukti lokasi lokal |
| --- | --- | --- | --- | --- |
| 438 | Taman Hutan Raya Banten | Rp8.000, umum Nusantara/hari | [Perda Banten 1/2024](https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf), 261 | `banten/sources/osm_balai_tahura.json` |
| 439 | Museum Multatuli | Rp2.000, umum | [Perda Lebak 1/2025](https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf), 232 | `banten/sources/osm_multatuli_full.json` |
| 440 | Goa Seplawan | Rp5.000 | [Perda Purworejo 1/2026](https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf), 242 | `jawa_tambahan/sources/osm_seplawan.json` |
| 441 | Pantai Jatimalang | Rp5.000 | Perda Purworejo 1/2026, 242 | `jawa_tambahan/sources/osm_jatimalang.json` |
| 442 | Kolam Renang Artha Tirta | Rp8.000 hari biasa; Rp10.000 libur/besar | Perda Purworejo 1/2026, 242 | `jawa_tambahan/sources/osm_artha_tirta_full.json` |
| 443 | Museum Trinil | Rp4.000, domestik dewasa/kunjungan | [Perda Ngawi 10/2023](https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf), 122 | `jawa_tambahan/sources/osm_trinil.json` |

Path bukti lokasi relatif terhadap `data/review/`. Salinan PDF dan cuplikan
tarif tersimpan di folder `sources` masing-masing, sehingga bukti tidak hanya
bergantung pada URL. Tanggal/keputusan serta atribusi lengkap:
[Banten](data/review/banten/Dokumentasi.md),
[tambahan Jawa](data/review/jawa_tambahan/Dokumentasi.md),
[gabungan](data/review/gabungan_jawa/Dokumentasi.md).
3. `data/review/tambahan_jawa_2026_11/kandidat_kaggle_review.csv`: 23 tambahan
   (ID 444–466) dengan format Kaggle, dari Banten, Jawa Barat, Jawa Tengah,
   DI Yogyakarta, dan Jawa Timur. Tarif dari Perda retribusi kabupaten/provinsi
   (URL, halaman PDF, dan item tabel di
   [provenance.json](data/review/tambahan_jawa_2026_11/provenance.json)), lokasi dari
   snapshot Nominatim/Overpass OSM. Rincian per destinasi:
   [Dokumentasi tambahan November 2026](data/review/tambahan_jawa_2026_11/Dokumentasi.md).
Lokasi © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright).
Titik representatif bangunan/balai/kolam tidak otomatis pintu masuk wisata.
Dokumen peraturan tidak boleh disamakan dengan lisensi CC BY seluruh situsnya.

## Rating dan nilai kosong

Lima nilai tambahan memakai pengamatan listing Google Maps yang cocok nama dan
lokasi: Multatuli 4,6; Seplawan 4,6; Jatimalang 4,5; Artha Tirta 4,2; Trinil 4,3.
URL listing, tanggal akses, dan keputusan kecocokan ada di
[bukti JSON](data/review/gabungan_jawa/google_maps_rating_review.json) dan
[catatan rating](data/review/gabungan_jawa/Rating_Google_Maps.md).
Ini rating agregat pihak ketiga, bukan rating resmi atau data OSM berlisensi terbuka.

Untuk tambahan November 2026, 16 rating Google Maps yang cocok nama dan lokasi
dipakai ([bukti JSON](data/review/tambahan_jawa_2026_11/google_maps_rating_review.json)).
Tujuh listing belum cocok atau tidak teramati: ID444 Tasikardi, 446 Lokawisata
Baturraden, 447 Taman Botani Baturraden, 451 Pantai Popoh, 459 Ranu Pakis,
462 Waduk Cacaban, dan 463 Objek Wisata Guci. Rating sumbernya tetap kosong.

Rating sumber Tahura tetap kosong. Sesuai persetujuan pengguna, kolom model
`c2_rating_for_model` diisi median **4,5 dari 458 rating teramati** untuk Tahura
dan ketujuh ID di atas. Median dipilih karena distribusi rating miring ke kiri,
sehingga lebih tahan pencilan daripada rata-rata. Hanya ID dengan nama yang cocok
pada daftar `IMPUTED_RATING_NAMES` di `data_pipeline.py` mendapat kebijakan tersebut. Penanda imputasi dan
alasan selalu disimpan. Hilangnya rating lain akan menghentikan pembuatan fitur,
bukan otomatis mendapat median atau dibuang. `Time_Minutes` tambahan tetap kosong.

Pelabuhan Marina ID9 tetap ada. Label Jakarta berkonflik dengan koordinat
1,07888 / 103,931398. Koordinat tidak dipindahkan; perhitungan jarak record
ini perlu review. Di peta, Marina tidak dipaksakan masuk bingkai Jawa.

Kebun Tanaman Obat Sari Alam ID323 juga diberi flag review. Deskripsinya menyebut
Jl. Raya Ciwidey, Bandung, tetapi koordinat Kaggle -6,601321 / 106,632734 berada
di sekitar Bogor, sekitar 114 km dari Bandung. Koordinat tidak dipindahkan karena
belum ada sumber lokasi terbuka yang terverifikasi; jarak, pin peta, dan rute
record ini perlu review. Daftar flag ada di `COORDINATE_REVIEW` pada `data_pipeline.py`.

Registry kota asal (`data/kota_indonesia.csv`) berisi 347 kota/kabupaten. Delapan
kabupaten lokasi destinasi (Sumedang, Kudus, Purworejo, Tegal, Lumajang, Ngawi,
Trenggalek, Tulungagung) ditambahkan 19 November 2026 dengan titik pusat ibu kota
kabupaten dari OSM Nominatim; bukti di
[kota_asal_2026_11](data/review/kota_asal_2026_11/Dokumentasi.md).

## Preprocessing dan metode

- Rapikan teks, angka, kategori/wilayah; flag nilai/koordinat bermasalah, tanpa
  `dropna` destinasi. ID stabil dan unik tepat 1–466, meskipun nama bisa berupa alias.
- Interaksi pengguna Kaggle divalidasi dan agregat dihitung terpisah. Rating
  interaksi tidak ditukar dengan rating destinasi Google/Kaggle.
- C4 = jumlah penyebutan fasilitas yang diterima / **6**: toilet, parkir,
  warung/makan, tempat ibadah, aksesibilitas, pusat informasi. Koreksi konteks
  menolak negasi, rencana, fasilitas tetangga, dan perbandingan arsitektur.
  0 berarti tidak ada bukti deskripsi yang diterima, **bukan tidak ada fasilitas**.
  [Audit C4](reports/preprocessing/audit_c4_descriptions.md).
- K-Means: seluruh 466; harga tiket dicap p99 hanya untuk fitur, Z-score harga
  dan rating model, one-hot kategori. Harga master tetap utuh. C4 dan metadata
  kualitas tidak dimasukkan dalam jarak clustering. Seed42, 10 starts, k2–6.
- Hasil snapshot: k2; silhouette **0,57581**, cluster **441 / 25**. Ini pemisahan
  fitur, bukan akurasi rekomendasi. Semua 466 mendapat label; bukan 1900 proyeksi.
- SPK memakai C1 harga tiket sumber (cost), C2 rating model (benefit), C3 jarak garis lurus Haversine
  (cost), C4 indikator deskripsi, C5 kecocokan kategori, C6 Jaccard hobi (benefit).
  Label cluster tidak menjadi filter keras rekomendasi.
- Empat profil AHP konsisten CR<0,1. **Seimbang** dari kuesioner 28 responden
  ([rekap anonim](data/survey/kuesioner_bobot_rekap.csv)); Hemat, Kualitas, Petualang
  preset pengembang. Slider hanya sensitivitas bobot yang dinormalisasi, bukan AHP baru.

## Budget tiket, geografi, dan batasan

Budget adalah batas harga tiket masuk **satu destinasi per orang**. Filter:
`harga_tiket <= budget`; harga asli tetap utuh dan tidak dicap p99 dalam SPK.
Budget0 memperbolehkan tiket gratis. Sisa alokasi tiket bukan sisa anggaran
perjalanan. Tidak ada estimasi transportasi, makan, inap, atau biaya berbasis moda.
C3 memakai Haversine (jarak garis lurus), bukan jarak jalan dan bukan ongkos.
Harga tetap snapshot sesuai sumber; periksa tarif sebelum berkunjung. Hari biasa
Artha Tirta menjadi tarif dasar, bukan penentuan tanggal otomatis.

Tujuan hanya enam provinsi Jawa; kota asal luar Jawa tetap boleh dipilih. Peta
SVG adalah pendekatan visual dari aset enam provinsi lama, bukan proyeksi GIS
terverifikasi atau navigasi jalan. Seluruh 466 tercantum, 465 titik dalam bingkai.
Pemeriksaan satu contoh Monas tidak membuktikan akurasi seluruh437 atau cakupan
seluruh kabupaten/provinsi. Survei kegunaan dan verifikasi lapangan belum dilakukan.

## Traceability / integritas

`reports/preprocessing/preprocessing_java443_manifest.json` menyimpan hash sumber,
output, versi, urutan ID, parameter scaler/p99/imputasi, dan fingerprint.
Importer/trainer menolak artifact usang atau berbeda sebelum mengubah database.
Git attributes mengunci newline sumber sesuai snapshot; ekspor JSON/CSV aktif
memakai LF konsisten. Tes hash menjaga byte raw/bukti/DOCX tidak berubah.

Alur aktif dan file Drive: [README](README.md). Daftar arsip dan pemulihan:
[cleanup](docs/maintenance/java443-cleanup.md). Laporan dan Excel aktif berada di `outputs/uts_travelfit/` dan
`outputs/excel_spk_20261005/`. DOCX/XLSX lama di root tetap arsip historis.
Keputusan 5 Oktober 2026: [budget tiket](docs/decisions/2026-10-05-ticket-budget.md).
