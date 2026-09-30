# Pemeriksaan kelengkapan 437 + 6 destinasi

Tanggal: 30 September 2026.

Notebook `notebooks/01_preprocessing_travelfit.ipynb` sekarang membaca kedua
sumber, bukan hanya CSV Kaggle. Hasilnya **443 baris dengan 443 ID unik**.

| Sumber | Baris masuk | Baris dipertahankan | ID |
| --- | ---: | ---: | --- |
| `data/raw/tourism_with_id.csv` | 437 | 437 | 1–437 |
| `data/review/gabungan_jawa/destinasi_jawa_review.csv` | 6 | 6 | 438–443 |
| Total | 443 | 443 | 1–443 |

Jumlah ID hilang: **0**. Tidak ada destinasi yang dihapus karena rating,
durasi, atau informasi fasilitas kosong. Koreksi C4 mengubah fitur, bukan
menghapus objek wisata. ID, nama, harga, rating, koordinat, deskripsi hasil
pembersihan format, dan C4 pada 437 baris dibandingkan dengan hasil sebelum
task ini dan tidak berubah.

## Perlindungan terhadap kehilangan data

- Kedua sumber wajib tersedia. Jika CSV tambahan tidak ditemukan, notebook berhenti; tidak mengekspor hanya 437 baris.
- Jumlah dan ID kedua sumber diperiksa sebelum penggabungan.
- Masalah nilai ditulis pada `data_quality_issues`, bukan menjadi filter penghapusan baris.
- Sebelum ekspor, notebook memeriksa jumlah 443, ID unik, dan kesamaan seluruh ID pada data bersih serta matriks fitur. Jika tidak cocok, ekspor dihentikan.
- Agregasi rating pengguna memakai left join, sehingga destinasi tanpa rating pengguna tetap tersimpan. Pembersihan rating pengguna tidak mengurangi baris destinasi.

## Output untuk dataset Jawa

- `data/processed/destinations_clean_java443.csv`: master preprocessing 443 destinasi.
- `data/processed/destinations_kmeans_features_java443.csv`: matriks fitur 443 baris beserta penanda `model_features_complete`.
- `reports/preprocessing/preprocessing_java443_summary.json`: bukti jumlah sumber, ID hilang, kelengkapan rating, dan status kesiapan training.
- `data/processed/ratings_aggregated.csv`: agregat rating pengguna Kaggle; enam tambahan tidak memiliki interaksi pengguna Kaggle.

File `destinations_clean.csv`, `destinations_kmeans_ready.csv`, dan
`preprocessing_summary.json` lama tetap berisi snapshot 437 baris untuk
kompatibilitas importer website lama. **File tersebut bukan hasil gabungan
443 yang baru.** Jangan memakai file lama saat meninjau dataset Jawa baru.
Website/database belum dialihkan pada task ini.

## Rating tambahan dan kesiapan model

| ID | Destinasi | Rating pada master baru | Status |
| --- | --- | --- | --- |
| 438 | Taman Hutan Raya Banten | rating sumber kosong; nilai perhitungan 4,5 | Imputasi median yang disetujui pengguna; identitas listing Google Maps belum dipastikan |
| 439 | Museum Multatuli | 4,6 | Nama/lokasi cocok pada bukti pengamatan |
| 440 | Goa Seplawan | 4,6 | Nama/lokasi cocok pada bukti pengamatan |
| 441 | Pantai Jatimalang | 4,5 | Nama/lokasi cocok pada bukti pengamatan |
| 442 | Kolam Renang Artha Tirta | 4,2 | Nama/lokasi cocok pada bukti pengamatan |
| 443 | Museum Trinil | 4,3 | Nama/lokasi cocok pada bukti pengamatan |

URL dan tanggal pengamatan rating disimpan per baris melalui
`rating_source_url` serta `rating_access_date`; bukti asal tetap di
`data/review/gabungan_jawa/google_maps_rating_review.json`. Rating Google Maps
merupakan agregat ulasan pihak ketiga, bukan rating resmi pemerintah dan
bukan klaim data berlisensi terbuka. CSV review asli tidak diubah.

`Time_Minutes` keenam tambahan tetap kosong. C4 tambahan tetap memakai
deskripsi dan koreksi konteks, bukan fasilitas yang dikarang. Nilai C4 0 tidak
berarti pasti tidak memiliki fasilitas.

### Pembaruan setelah persetujuan imputasi

Pengguna kemudian menyetujui imputasi median untuk Tahura. `rating` dan
`c2_rating` tetap kosong, tetapi `c2_rating_for_model` bernilai **4,5**,
dihitung dari 442 rating valid. `rating_imputed=True` dan catatan perhitungan
membedakan nilai tersebut dari rating yang teramati. Kolom model ini dipakai
untuk standardisasi C2; bukan perubahan rating sumber. Tidak ada imputasi
otomatis untuk destinasi lain.

Seluruh **443 baris** sekarang memiliki fitur numerik/kategori lengkap,
sehingga ringkasan menandai `kmeans_training_ready: true`. Ini menyatakan
kelengkapan matriks fitur, bukan bahwa training atau integrasi aplikasi telah
selesai. Tidak ada destinasi yang dihapus dan belum dilakukan pelatihan ulang.

Pelabuhan Marina (ID 9) tetap dimasukkan sesuai keputusan pengguna, dengan
koordinat sumber `1.07888, 103.931398`. Konflik dengan label Jakarta dicatat
pada `coordinate_review_required`, `coordinate_review_note`, dan
`data_quality_issues`. Koordinat tidak diganti dengan tebakan. Kelengkapan
fitur K-Means tidak membuktikan kualitas lokasi untuk perhitungan jarak.

## Menjalankan di Colab

Selain notebook dan data Kaggle, salin folder `data/review/gabungan_jawa`
ke `Drive Saya/TravelFit`, minimal CSV tambahan dan JSON bukti rating.
Struktur proyek yang sama dipakai di lokal dan Drive. Output berada di
`TravelFit/data/processed`, dengan nama berakhiran `java443` di atas.

## Verifikasi

Lima tes retensi awal menjalankan sel notebook nyata untuk memeriksa jumlah/ID,
matriks fitur, rating Tahura yang tetap kosong, lima rating yang boleh
dipindahkan, dan nilai tidak valid yang ditandai tanpa membuang destinasi.
Kelima tes gagal pada implementasi sebelumnya dan lolos setelah perbaikan.

Uji integrasi awal menemukan empat error pada tes importer lama karena
kolom database `rating` menolak nilai kosong. Output Jawa kemudian dipisahkan
agar dataset lengkap tetap dipertahankan tanpa merusak importer tersebut.
Setelah pemisahan output, seluruh **126 tes Django lolos** (32,559 detik).
Eksekusi ulang notebook dari awal sampai akhir berhasil; kedua CSV baru
memiliki 443 ID unik yang sama. Laporan DOCX tidak diubah.

Lima tes tambahan dibuat gagal sebelum implementasi imputasi: nilai median
hanya pada kolom model, matriks numerik tanpa nilai kosong, rating teramati
tidak ditimpa, Marina dipertahankan dengan penanda review, serta median
dihitung dari data (fixture median 4,2, bukan angka 4,5 yang di-hardcode).
Catatan hasil 126 tes di atas adalah hasil sebelum lima tes tambahan ini.

Verifikasi setelah pembaruan imputasi: **131 tes Django lolos** (33,679 detik).
Notebook dijalankan ulang; 443 ID tetap lengkap, seluruh nilai numerik pada
matriks fitur finite, standardisasi C2 memakai nilai perhitungan yang benar,
dan seluruh field sumber tetap sama. Satu-satunya rating yang diimputasi adalah
ID 438; satu penanda review koordinat yang ditambahkan adalah ID 9.
