# Keputusan: imputasi rating Tahura dan retensi Pelabuhan Marina

Tanggal: 30 September 2026. Branch: `new`.

## Persetujuan pengguna

Pengguna mengizinkan penggunaan median untuk rating Tahura dan meminta
Pelabuhan Marina tetap dimasukkan. Target jumlah tetap 437 baris Kaggle dan
enam tambahan, yaitu 443 destinasi. Tidak ada izin untuk mengarang koordinat
pengganti atau mengklaim nilai imputasi sebagai rating terverifikasi.

## Implementasi task preprocessing

- `rating` dan `c2_rating` Tahura (ID 438) tetap kosong.
- `c2_rating_for_model` Tahura diisi median 442 rating destinasi valid yang teramati, yaitu **4,5** pada snapshot saat ini. Median dihitung dari data, bukan angka tetap di kode dan bukan dari agregat penilaian pengguna Kaggle.
- `rating_imputed=True` serta `rating_model_note` menandai nilai turunan tersebut. Rating destinasi lain tidak ditimpa. Imputasi otomatis untuk destinasi lain tidak diaktifkan.
- Standardisasi C2 memakai kolom perhitungan tersebut; seluruh 443 baris tetap disimpan. Flag imputasi adalah metadata audit, bukan fitur jarak clustering.
- Pelabuhan Marina (ID 9) tetap memiliki label sumber Jakarta, lintang `1.07888`, dan bujur `103.931398`. Konflik lokasi diberi `coordinate_review_required=True`, catatan, dan kode `coordinate_location_conflict` pada kualitas data. Retensi baris tidak menyatakan koordinatnya benar.
- Notebook dan keluaran Jawa diperbarui, tetapi database/importer website lama, model K-Means tersimpan, dan runtime TOPSIS belum berubah pada task ini.

## Kontrak untuk integrasi berikutnya

Importer harus mempertahankan rating sumber dan nilai perhitungan secara
terpisah, bukan mengisi kolom sumber kosong dengan 4,5. K-Means dan TOPSIS harus
menggunakan nilai perhitungan yang sama, bukan mengimputasi ulang dari kandidat
hasil filter. UI harus menampilkan “Imputasi median 4,5; rating belum
terverifikasi” saat memakai nilai tersebut, bukan menyebutnya rating Google Maps.

Pelabuhan Marina harus tetap tersedia dalam data aplikasi. Peta yang berfokus
ke Jawa tidak boleh menggeser titik sumber ke Jakarta dengan koordinat
tebakan; titik di luar area tampilan dan peringatan kualitas harus ditangani
secara eksplisit pada rancangan peta. Perhitungan jarak/biaya dari koordinat
tersebut perlu diberi peringatan karena dapat tidak mewakili lokasi destinasi.

Penyatuan notebook, database, training, dan runtime berikutnya merupakan task
lintas komponen dengan rancangan tersendiri. Dokumen ini mencatat keputusan
data yang telah disetujui, bukan menyatakan seluruh integrasi selesai.

Laporan DOCX tidak diubah. Commit dilakukan lokal per task; tidak ada push.
