# Cleanup Java443 — 30 September 2026

Status: workflow aktif hanya Java443. Semua file di bawah diarsipkan, bukan dihapus permanen.
Target setiap baris: `archive/legacy/<path-asal>`; struktur relatif dipertahankan.
Audit `git ls-files` dan `rg` pada config/recommender/scripts/notebooks dilakukan sebelum pemindahan.

| Path asal | Keputusan / dependensi |
| --- | --- |
| `Dataset_Wisata_38_Provinsi.xlsx` | Arsip; fixture inventaris review historis, CLI/tes diarahkan ke lokasi arsip |
| `Dataset_Wisata_Gabungan_2337.xlsx` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `Dataset_Wisata_Terverifikasi.xlsx` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `Dataset_Wisata_Terverifikasi_OpsiB.xlsx` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `Dataset_Wisata_Terverifikasi_Validated.xlsx` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `Design.html` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `Design.md` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `index.html` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `IMPLEMENTATION_PLAN_BUDGET_TOTAL.md` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `notebooks/02_preprocessing_travelfit_full.ipynb` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `notebooks/03_preprocessing_full_2337.ipynb` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `outputs/travelfit_2337/TravelFit_Dataset_2337_Tervalidasi.xlsx` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `outputs/travelfit_2337/preprocessing_output/destinations_clean_2337.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `outputs/travelfit_2337/preprocessing_output/kmeans_ready_2337.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/destinations_audited_verified.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/destinations_clean.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/destinations_full_clean.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/destinations_full_kmeans_ready.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/destinations_kmeans_ready.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/ratings_aggregated.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/ratings_aggregated_full.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `data/processed/tourism_indonesia_38_provinsi.csv` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/audit_verification_pipeline_report.md` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/methodology_audit.md` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/synthetic_data_report.json` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/validated_major_landmarks_report.md` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/preprocessing/preprocessing_quality_report.json` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/preprocessing/preprocessing_summary.json` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/preprocessing/preprocessing_summary_full.json` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `reports/preprocessing/scaler_metadata.json` | Arsip; output/prototipe/alur lama, tidak dikonsumsi importer/trainer aktif |
| `scripts/all_provinces_registry.py` | Arsip; generator/audit lama, bukan command produksi |
| `scripts/process_audit_pipeline.py` | Arsip; generator/audit lama, bukan command produksi |
| `scripts/validate_major_landmarks.py` | Arsip; generator/audit lama, bukan command produksi |
| `scripts/__pycache__/build_full_dataset.cpython-311.pyc` | Arsip; generator/audit lama, bukan command produksi |
| `recommender/static/recommender/custom.css` | Arsip; tidak dirujuk template/views aktif sesudah Task6–7 |
| `recommender/static/recommender/nusantara.css` | Arsip; tidak dirujuk template/views aktif sesudah Task6–7 |
| `recommender/static/recommender/nusantara.js` | Arsip; tidak dirujuk template/views aktif sesudah Task6–7 |
| `recommender/templates/recommender/form_hasil.html` | Arsip; tidak dirujuk template/views aktif sesudah Task6–7 |

## Dipertahankan

- `Laporan_SPK_TravelFit.docx` tidak diubah. SHA256: `34ee9ed27a65ce2233d0a58b04519119debf5411f42f2f4347ef81c2e7259304`.
- `Perhitungan_SPK_TravelFit.xlsx` dan `data/processed/decision_matrix_example.csv`: referensi perhitungan, bukan sumber importer.
- Seluruh `data/raw/`, bukti `data/review/`, keputusan Tahura/Marina/C4, laporan retensi dan audit C4.
- `scripts/open_data_review/` dan tesnya: alat review terisolasi, bukan bagian website/training; default XLSX historis sekarang di arsip.
- `reports/audit_biaya.md`: audit parameter biaya tetap relevan; bukan validasi tarif seluruh destinasi.

## Pemulihan

File arsip bisa dibuka langsung; untuk mengaktifkan workflow lama perlu penyesuaian sumber dan dependensi. Jangan menjalankan generator lama sebagai pipeline Java443. Mengembalikan file tidak otomatis mengembalikan database.
Snapshot Git sebelum cleanup: `2f22dac`. Tidak memakai reset hard, clean, recursive delete, atau force push.
Backup SQLite sebelum migrasi/impor: `archive/local_backups/travelfit-before-java443-20260930T125839Z-120cd361.sqlite3` (diabaikan Git).
Untuk pemulihan database: hentikan server, simpan salinan DB saat ini, baru salin backup yang dipilih; backup sebelum migrasi memiliki schema lama sehingga jangan langsung mengimpor tanpa menjalankan migration. Operasi pemulihan tidak dilakukan pada task ini.

## Batasan

Data historis bernama “terverifikasi” tidak otomatis terverifikasi: nilai sintetis dahulu tidak menjadi pengamatan resmi. File lama tidak lagi dibaca aplikasi. Dataset Java443 tetap mengandung calon alias dan label kota yang bukan audit batas provinsi; retensi ID tidak sama dengan 443 objek unik terverifikasi.
