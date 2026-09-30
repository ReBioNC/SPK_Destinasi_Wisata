# Hasil pemeriksaan rating Google Maps

Tanggal akses: **30 September 2026** (Asia/Jakarta).

Rating dibaca langsung dari panel tempat Google Maps, bukan ditebak atau disalin dari situs agregator. Catatan terstruktur beserta URL tempat, nama listing, alamat, jumlah ulasan yang terlihat, serta keputusan pencocokan ada di [google_maps_rating_review.json](google_maps_rating_review.json).

| ID | Destinasi | Rating terlihat / 5 | Ulasan terlihat | Status pencocokan |
| --- | --- | --- | --- | --- |
| 438 | Taman Hutan Raya Banten | 4,4 | 331 | Kandidat: listing **Forest Park (Tahura)** memakai subjudul Curug Putri Carita; belum disetujui untuk dipindahkan ke record kawasan Tahura |
| 439 | Museum Multatuli | 4,6 | Tidak ditampilkan | Nama dan lokasi cocok |
| 440 | Goa Seplawan | 4,6 | 1.332 | Nama dan lokasi cocok |
| 441 | Pantai Jatimalang | 4,5 | 1.227 | Nama dan lokasi cocok |
| 442 | Kolam Renang Artha Tirta | 4,2 | 1.102 | Nama dan lokasi cocok |
| 443 | Museum Trinil | 4,3 | 1.475 | Nama dan lokasi cocok |

## Penggunaan dan batasan

- Berkas ini adalah **hasil riset**, belum mengubah CSV sumber, notebook, database, atau model. Dataset review sebelumnya tetap utuh.
- Lima rating cocok dengan nama dan lokasi record. Rating Tahura adalah observasi nyata pada listing kandidat, **bukan rating kawasan yang sudah dipastikan cocok**. Jangan mengisi record 438 secara otomatis sebelum identitasnya diputuskan.
- `Time_Minutes` tetap kosong. Banyaknya ulasan yang tidak terlihat juga tetap kosong, bukan diisi dari listing lain.
- Rating merupakan agregat pendapat pengguna Google Maps, bukan nilai resmi pemerintah atau bukti mutu objektif. Rating dan jumlah ulasan bisa berubah; simpan tanggal akses.
- Sumber tarif tetap dokumen peraturan yang ada dalam [Dokumentasi.md](Dokumentasi.md). Koordinat sumber CSV tetap OSM; koordinat pin Maps pada catatan hanya membantu pencocokan identitas dan tidak menggantikan koordinat sumber.
- Permintaan penggunaan Google Maps merupakan perubahan pilihan sumber untuk rating. Tidak ada klaim bahwa konten Google Maps berlisensi terbuka atau mengikuti lisensi ODbL milik OSM. Periksa ketentuan Google yang berlaku sebelum redistribusi atau penggunaan produksi.
- Pengumpulan dilakukan satu kali untuk enam kandidat. Tidak ada pemanggilan Maps tambahan pada setiap rekomendasi website.
