# Keputusan pengguna: pertahankan C4 dari deskripsi

Tanggal: 30 September 2026. Branch kerja: `new`.

## Keputusan yang disetujui

Pengguna memilih tetap memakai C4 fasilitas berdasarkan ekstraksi kata kunci dari deskripsi, mengikuti pendekatan yang sudah dibuat. Usulan menonaktifkan C4 dan mengurangi AHP–TOPSIS menjadi lima kriteria **tidak dipakai**.

C4 tetap merupakan indikator turunan teks, bukan hasil survei atau pemeriksaan fasilitas di lapangan. Nilai 1 pada flag berarti kata kunci terdeteksi; nilai 0 berarti tidak terdeteksi, bukan bukti fasilitas tidak tersedia. Deskripsi kosong harus dapat dibedakan dari deskripsi yang sudah dipindai tetapi tidak menghasilkan kecocokan. Penyebutan dengan negasi juga tidak otomatis membuktikan ketersediaan.

Tidak boleh menambahkan kalimat fasilitas pada deskripsi tanpa bukti hanya untuk menghasilkan skor yang lebih tinggi. Sumber deskripsi dan asal fitur turunan perlu dipertahankan.

## Temuan audit untuk rancangan berikutnya

- `notebooks/01_preprocessing_travelfit.ipynb` saat ini menghitung rata-rata enam kelompok: toilet, parkir, makanan, tempat ibadah, aksesibilitas, dan pusat informasi.
- `Destination.facility_score()` saat ini menghitung empat kelompok: toilet, parkir, warung, dan musala. Dengan demikian, hasil notebook dan website belum memakai definisi C4 yang sama.
- Penyamaan definisi, penamaan indikator, dan penjelasan keterbatasannya masuk ke rancangan pembaruan pipeline. Catatan keputusan ini **belum mengubah** notebook, model database, AHP, TOPSIS, atau UI.
- Pemakaian C4 pada SPK tidak otomatis menentukan fitur K-Means; fitur clustering harus ditetapkan dan dilaporkan tersendiri.

## Alur commit

Sesuai permintaan pengguna, setiap task yang selesai dan sudah diperiksa disimpan sebagai commit lokal terpisah. Task belum selesai tidak dinyatakan selesai hanya karena file telah dibuat. Push ke remote bukan bagian dari instruksi commit ini.

Laporan DOCX tetap di luar ruang lingkup perubahan.
