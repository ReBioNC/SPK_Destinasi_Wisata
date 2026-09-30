# Gabungan tambahan destinasi Jawa untuk review

Tanggal penggabungan: 30 September 2026.

`destinasi_jawa_review.csv` menggabungkan **2 destinasi Banten + 4 destinasi tambahan Jawa = 6 baris**. Nilai setiap field dipertahankan persis dari file asal; hanya header yang ditulis sekali. ID lokal tetap 438-443 dan struktur 13 kolom sama dengan CSV Kaggle, termasuk dua kolom tanpa nama.

**Ini hanya gabungan enam data tambahan, bukan gabungan dengan 437 baris Kaggle.** File asal, bukti sumber, dataset utama, preprocessing, model dan website tidak diubah atau dihapus. Jangan mengimpor file gabungan bersama kedua file asal sekaligus karena akan menggandakan enam destinasi yang sama.

## Isi dan sumber

| ID | Destinasi | Kabupaten | Provinsi | Price (Rp/orang) | Bukti tarif |
| --- | --- | --- | --- | --- | --- |
| 438 | Taman Hutan Raya Banten | Pandeglang | Banten | 8.000 | Perda Banten 1/2024, halaman PDF 261, pengunjung umum Nusantara per hari |
| 439 | Museum Multatuli | Lebak | Banten | 2.000 | Perda Lebak 1/2025, halaman PDF 232, umum |
| 440 | Goa Seplawan | Purworejo | Jawa Tengah | 5.000 | Perda Purworejo 1/2026, halaman PDF 242 |
| 441 | Pantai Jatimalang | Purworejo | Jawa Tengah | 5.000 | Perda Purworejo 1/2026, halaman PDF 242 |
| 442 | Kolam Renang Artha Tirta | Purworejo | Jawa Tengah | 8.000 | Perda Purworejo 1/2026, halaman PDF 242, hari biasa; hari besar/libur 10.000 |
| 443 | Museum Trinil | Ngawi | Jawa Timur | 4.000 | Perda Ngawi 10/2023, halaman PDF 122, domestik dewasa per kunjungan |

Dokumentasi lengkap dan salinan sumber tetap berada di folder asal, ditautkan secara relatif agar bisa dibuka dari repo:

- [Dokumentasi Banten](../banten/Dokumentasi.md), [CSV asal](../banten/banten_kaggle_review.csv), [folder bukti](../banten/sources/).
- [Dokumentasi tambahan Jawa](../jawa_tambahan/Dokumentasi.md), [CSV asal](../jawa_tambahan/jawa_kaggle_review.csv), [provenance per destinasi](../jawa_tambahan/provenance.json), [folder bukti](../jawa_tambahan/sources/).

URL utama tarif:

- [Perda Banten 1/2024](https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf).
- [Perda Lebak 1/2025](https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf).
- [Perda Purworejo 1/2026](https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf).
- [Perda Ngawi 10/2023](https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf).

## Batasan yang tetap berlaku

- Status **draft review**, bukan seluruh enam kriteria sudah terverifikasi. Penggabungan tidak meningkatkan status verifikasi atau memberi persetujuan reviewer manusia.
- `Rating` dan `Time_Minutes` tetap kosong, bukan 0. Tidak ada imputasi atau angka sintetis baru.
- Harga adalah tarif dasar menurut dokumen yang diperiksa, bukan total budget perjalanan dan bukan jaminan tarif transaksi terkini. Kondisi hari biasa Artha Tirta harus diperhatikan saat integrasi.
- Koordinat dari OpenStreetMap adalah titik representatif; Tahura memakai Balai Tahura, Multatuli titik tengah bounding box bangunan, Artha Tirta titik tengah bounding box kolam. Goa Seplawan memakai titik mulut goa. Titik-titik ini tidak otomatis pintu/loket wisata terverifikasi.
- Kategori merupakan pemetaan penyusun ke kategori Kaggle, bukan label resmi status hukum kawasan. `City` menggunakan kabupaten; provinsi dicatat di dokumentasi.
- Dasar penggunaan dokumen peraturan dan batasannya mengikuti dokumentasi asal, bukan klaim bahwa seluruh situs pemerintah berlisensi CC BY. Data OSM berlisensi **ODbL 1.0**, atribusi **© OpenStreetMap contributors**; pertahankan ketentuannya ([lisensi OSM](https://www.openstreetmap.org/copyright)).
- ID tidak berbenturan dengan Kaggle 1-437, tetapi belum diaudit terhadap dataset sintetis lama. Belum digabung ke Kaggle, belum dilatih K-Means dan belum diberi cluster.

## Pemeriksaan

### Integrasi preprocessing 443 (30 September 2026)

Notebook `01_preprocessing_travelfit.ipynb` kini menggabungkan CSV review ini
dengan 437 baris Kaggle menjadi **443 destinasi**, tanpa mengubah CSV review
asli. Lima rating yang berstatus `matched_name_location` pada bukti Google
Maps dimasukkan hanya ke output preprocessing baru; rating Tahura tetap kosong
karena identitas listing belum dipastikan. `Time_Minutes` tambahan tetap kosong.

Hasil disimpan di `data/processed/destinations_clean_java443.csv` dan
`data/processed/destinations_kmeans_features_java443.csv`. Ini belum integrasi
database website atau training K-Means. Lihat [laporan retensi](../../../reports/preprocessing/retention_java443.md)
untuk jumlah/ID dan batasan kelengkapan fitur. Pernyataan draft/kosong di atas
tetap menjelaskan **CSV review asal**, bukan output baru.

`validate_gabungan.py` memeriksa header, kesamaan persis keenam baris terhadap kedua file asal, ID/nama unik, konsistensi koordinat, nilai kosong serta ID yang tidak berbenturan dengan Kaggle. Pemeriksaan sumber lebih lanjut tetap tersedia melalui validator masing-masing folder asal.

```powershell
& '.\.venv\Scripts\python.exe' data/review/gabungan_jawa/validate_gabungan.py
```
