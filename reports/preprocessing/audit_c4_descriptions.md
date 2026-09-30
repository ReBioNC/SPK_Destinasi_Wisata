# Audit konteks fasilitas (C4)

Tanggal: 30 September 2026. Sumber pemeriksaan: kolom `Description` pada
`data/raw/tourism_with_id.csv`. Tidak ada informasi fasilitas baru yang dikarang
atau deskripsi sumber yang diganti.

## Definisi dan batasan

C4 tetap dihitung dari enam kelompok penyebutan fasilitas: toilet, parkir,
tempat makan, tempat ibadah, aksesibilitas, dan pusat informasi.

`C4 = jumlah kelompok dengan penyebutan yang diterima / 6`.

Ini adalah **indikator informasi dalam deskripsi**, bukan pengukuran kelengkapan
fasilitas aktual. Skor 0 berarti tidak ditemukan penyebutan yang diterima;
bukan bukti bahwa destinasi tidak memiliki fasilitas. Kata yang merujuk cerita
sejarah, bangunan tetangga, nama objek, rencana, atau perbandingan desain tidak
otomatis menjadi bukti fasilitas destinasi.

Pemeriksaan ini terbatas pada konteks yang ditemukan keliru. Deskripsi lain
masih memakai heuristik kata kunci; hasilnya tidak diklaim telah terverifikasi
seluruhnya. Penyebutan ambigu tidak ditambahkan sebagai fakta baru.

## Hasil preprocessing 437 baris

| Ukuran | Hasil |
| --- | ---: |
| Destinasi dengan C4 positif sebelum koreksi | 82 |
| Destinasi dengan kecocokan kata kunci setelah penambahan `parkiran`, sebelum koreksi konteks | 83 |
| Destinasi yang diberi catatan koreksi konteks | 15 |
| Destinasi dengan C4 positif setelah koreksi | 69 |
| Destinasi dengan skor berubah | 17 |
| Deskripsi kosong | 0 |

Penambahan kata `parkiran` memperbaiki deteksi pada Taman Spathodea (ID 79,
1/6 menjadi 2/6) dan Air Terjun Semirang (ID 386, 0 menjadi 1/6).
Deskripsi Semirang menyebut jarak lokasi parkiran ke air terjun, bukan fasilitas
yang diasumsikan dari kategori wisata.

## Koreksi konteks

| ID | Destinasi | Skor lama → baru | Alasan menolak kecocokan tertentu |
| --- | --- | --- | --- |
| 18 | Museum Bank Indonesia | 1/6 → 0 | Gereja dalam cerita sejarah telah dibongkar. |
| 57 | Taman Lapangan Banteng | 1/6 → 0 | Gereja Katedral merupakan lokasi lain di dekat taman. |
| 94 | Sumur Gumuling | 1/6 → 0 | Fungsi ibadah masa lalu tidak memastikan fasilitas aktif. |
| 115 | Monumen Sanapati | 1/6 → 0 | Gereja menjadi penanda lokasi di luar monumen. |
| 149 | Goa Cerme | 1/6 → 0 | Masjid disebut dalam cerita sejarah. |
| 176 | Museum Gunung Merapi | 2/6 → 0 | Parkir masih disebut sebagai rencana; pusat layanan informasi juga dijelaskan sebagai fungsi museum yang diharapkan, bukan fasilitas terpisah yang dipastikan. |
| 213 | Gedung Sate | 1/6 → 0 | Pura disebut sebagai perbandingan arsitektur atap. |
| 232 | Bukit Moko | 1/6 → 0 | Kuliner dibahas sebagai daya tarik Bandung secara umum. |
| 249 | Upside Down World Bandung | 1/6 → 0 | Kamar mandi adalah ruangan bertema untuk berfoto. |
| 254 | Teras Cikapundung BBWS | 1/6 → 0 | Warung muncul dalam cerita kondisi sebelumnya, bukan fasilitas saat ini yang dipastikan. |
| 270 | Bukit Bintang | 1/6 → 0 | Deskripsi membahas Kuala Lumpur, bukan objek Bandung. Deskripsi asli dipertahankan untuk audit; koreksi ini tidak menyelesaikan masalah identitas record. |
| 295 | Museum Nike Ardilla | 1/6 → 0 | Hard Rock Cafe disebut sebagai perbandingan konsep desain. |
| 298 | Gunung Lalakon | 1/6 → 0 | Batu Warung adalah nama batu, bukan tempat makan. |
| 347 | Taman Pandanaran | 2/6 → 1/6 | Kesulitan mencari parkir tidak memastikan area parkir destinasi; penyebutan tempat makan tetap dipertahankan. |
| 353 | Taman Srigunting | 1/6 → 0 | Gereja Blenduk merupakan bangunan tetangga. |

Aturan koreksi hanya diterapkan jika ID, nama, dan frasa konteks cocok. Jika
deskripsi sumber diperbarui, aturan perlu ditinjau lagi; aturan ini bukan
pengganti pemahaman bahasa otomatis yang menyeluruh.

Satu aturan tambahan diuji untuk Pantai Jatimalang (ID 441) pada file review:
frasa “bukan pintu masuk atau area parkir terverifikasi” adalah batasan
verifikasi koordinat, bukan bukti fasilitas parkir. Enam baris file review
belum digabungkan ke hasil preprocessing 437 baris pada task ini.

## Artefak dan verifikasi

- Notebook `notebooks/01_preprocessing_travelfit.ipynb` dijalankan ulang dari awal sampai akhir.
- `destinations_clean.csv` menyimpan skor kata kunci sebelum koreksi, catatan review, indikator deskripsi kosong, dan C4 setelah koreksi.
- `destinations_kmeans_ready.csv` serta statistik standardisasi C4 dihitung ulang. Ini bukan pelatihan ulang model K-Means.
- ID, nama, deskripsi sumber, harga, rating, koordinat, C1, C2, dan tag aktivitas dibandingkan dengan versi Git sebelum task ini dan tetap sama.
- Tujuh tes C4 menguji salah deteksi, penyebutan yang benar, deskripsi tidak berubah, serta perlindungan terhadap ID yang dipakai ulang oleh tempat lain. Tes dibuat gagal pada implementasi lama sebelum perbaikan diterapkan.
- Seluruh 121 tes Django lolos pada 30 September 2026. Percobaan pertama dalam sandbox mengalami delapan error izin folder sementara; menjalankan ulang dengan izin yang sesuai menghasilkan 0 kegagalan/error.

Database website belum diimpor ulang. Implementasi runtime masih memakai
definisi C4 lama dengan empat kelompok; penyamaan runtime dan notebook adalah
task pipeline berikutnya. Laporan DOCX tidak diubah.
