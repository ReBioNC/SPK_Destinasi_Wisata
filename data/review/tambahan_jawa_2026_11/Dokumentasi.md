# Kandidat tambahan destinasi Jawa — November 2026

Tanggal penelitian: **16 November 2026**. Status: **draft review, belum diimpor**.

File `kandidat_kaggle_review.csv` berisi **23 kandidat** (batch 1: ID 444–453; batch 2: ID 454–459; batch 3: ID 460–466) dengan header 13 kolom yang sama persis dengan CSV Kaggle. Data utama 443 destinasi, preprocessing, database, model K-Means, dan website **tidak diubah**. ID 444–466 hanya ID lokal untuk review.

Setiap kandidat wajib punya tiga bukti yang bisa diakses publik: tarif dari dokumen peraturan resmi, lokasi dari OpenStreetMap, dan pemeriksaan nama terhadap 443 destinasi yang sudah ada. Rating diperiksa terpisah di Google Maps. Kandidat yang lokasinya tidak bisa dipastikan **ditunda**, bukan ditebak.

## Hasil

| ID | Destinasi | Kabupaten | Provinsi | Kategori | Price (Rp/orang) | Rating Google Maps |
| --- | --- | --- | --- | --- | --- | --- |
| 444 | Situs Taman Tasikardi | Serang | Banten | Budaya | 5.000 | 4,0 (1.059) — perlu keputusan |
| 445 | Taman Hutan Raya Gunung Kunci | Sumedang | Jawa Barat | Cagar Alam | 10.000 | 4,4 (1.733) — cocok |
| 446 | Lokawisata Baturraden | Banyumas | Jawa Tengah | Taman Hiburan | 20.000 | 4,5 (30.310) — perlu keputusan |
| 447 | Taman Botani Baturraden | Banyumas | Jawa Tengah | Cagar Alam | 15.000 | Tidak teramati |
| 448 | Waduk Sermo | Kulon Progo | DI Yogyakarta | Cagar Alam | 10.000 | 4,6 (2.651) — cocok |
| 449 | Puncak Suroloyo | Kulon Progo | DI Yogyakarta | Cagar Alam | 10.000 | 4,5 (1.347) — cocok |
| 450 | Pantai Trisik | Kulon Progo | DI Yogyakarta | Bahari | 10.000 | 4,1 (625) — cocok |
| 451 | Pantai Popoh | Tulungagung | Jawa Timur | Bahari | 8.500 | 3,9 (2.858) — perlu keputusan |
| 452 | Pantai Sine | Tulungagung | Jawa Timur | Bahari | 8.500 | 4,4 (6.040) — cocok |
| 453 | Taman Rekreasi Tawun | Ngawi | Jawa Timur | Taman Hiburan | 10.000 | 4,2 (2.007) — cocok |
| 454 | Taman Krida Wisata | Kudus | Jawa Tengah | Taman Hiburan | 3.000 | 4,2 (2.084) — cocok |
| 455 | Museum Kretek | Kudus | Jawa Tengah | Budaya | 4.000 | 4,3 (4.206) — cocok |
| 456 | Menara Pandang Teratai | Banyumas | Jawa Tengah | Taman Hiburan | 20.000 | 4,6 (8.798) — cocok |
| 457 | Pemandian Alam Selokambang | Lumajang | Jawa Timur | Taman Hiburan | 7.000 | 4,4 (2.712) — cocok |
| 458 | Ranu Klakah | Lumajang | Jawa Timur | Cagar Alam | 4.000 | 4,4 (1.517) — cocok |
| 459 | Ranu Pakis | Lumajang | Jawa Timur | Cagar Alam | 4.000 | 4,5 (133) — perlu keputusan |
| 460 | Makam Sunan Pandanaran | Klaten | Jawa Tengah | Tempat Ibadah | 2.000 | 4,5 (1.786) — cocok |
| 461 | Taman Nyi Ageng Rakit | Klaten | Jawa Tengah | Taman Hiburan | 10.000 | 4,5 (1.047) — cocok |
| 462 | Waduk Cacaban | Tegal | Jawa Tengah | Cagar Alam | 8.400 | 4,4 (682) — perlu keputusan |
| 463 | Objek Wisata Guci | Tegal | Jawa Tengah | Taman Hiburan | 14.400 | 4,3 (14.547) — perlu keputusan |
| 464 | Pantai Prigi | Trenggalek | Jawa Timur | Bahari | 10.000 | 4,3 (4.760) — cocok |
| 465 | Pantai Pelang | Trenggalek | Jawa Timur | Bahari | 10.000 | 4,4 (2.089) — cocok |
| 466 | Taman Mas Kemambang | Banyumas | Jawa Tengah | Taman Hiburan | 2.000 | 4,5 (8.932) — cocok |

DKI Jakarta tidak mendapat kandidat. Museum yang tarifnya disebut untuk Perda DKI 1/2024 (Museum Bahari, Wayang, Tekstil, Seni Rupa dan Keramik, Joang 45, Taman Prasasti, Sumpah Pemuda) **sudah ada** di data Kaggle, dan lampiran tarif Perda tersebut tidak berhasil diperoleh dari sumber resmi.

## Struktur dan asal field

| Field | Asal / aturan |
| --- | --- |
| `Place_Id` | ID lokal 444–466, tidak berbenturan dengan 1–443. |
| `Place_Name` | Nama objek pada tabel tarif atau nama OSM bila tabel memakai nama umum (mis. "Wisata Tawun"). |
| `Description` | Kalimat baru: jenis objek, wilayah, dasar tarif, dan batasan koordinat. Tidak menyalin teks situs lain. Karena tidak menyebut fasilitas, C4 kandidat akan bernilai 0 bila diimpor. |
| `Category` | Crosswalk penyusun ke kategori Kaggle, bukan label resmi pemerintah. |
| `City` | Nama kabupaten. "Serang" berarti Kabupaten Serang, bukan Kota Serang. |
| `Price` | Tarif dasar per orang dari dokumen peraturan; detail item dan halaman di `provenance.json`. Untuk tarif berbeda per hari dipakai tarif hari kerja. |
| `Rating`, `Time_Minutes` | Sengaja kosong di CSV, sama seperti kurasi sebelumnya. Rating ada di `google_maps_rating_review.json` dan hanya boleh dipakai bila `integration_allowed` bernilai `true`. |
| `Coordinate`, `Lat`, `Long` | Titik OSM yang tercatat di snapshot `sources/`. Bukan otomatis pintu masuk. |

## Sumber tarif

Semua tarif diperiksa langsung pada halaman PDF resmi, dan halaman tersebut disimpan sebagai gambar di `sources/`.

| Dokumen | Halaman PDF | Kandidat | Catatan |
| --- | --- | --- | --- |
| [Perda Kab. Serang 7/2023](https://peraturan.bpk.go.id/Download/349067/PERDA%20NOMOR%207%20TAHUN%202023%20TENTANG%20PAJAK%20DAERAH%20DAN%20RETRIBUSI%20DAERAH%20FIX%20(2).pdf) | 821 | Tasikardi Rp5.000 dewasa | Menggantikan Perbup Serang 271/2023 (Rp10.000), yang tetap disimpan sebagai jejak riwayat. |
| [Perda Sumedang 1/2024](https://portal-skpd.sumedangkab.go.id/storage/regulasi/PERDA%20NO%201%20TAHUN%202024.070224_07_33_59pdf.pdf) | 164 (Lampiran VIII) | Tahura tiket umum Rp10.000 | Lampiran menyebut "Taman Hutan Raya" tanpa nama kawasan. |
| [Perbup Banyumas 41/2023](https://peraturan.bpk.go.id/Download/326447/Perbup%20Bms%2041_2023.pdf) | 4 | Lokawisata Baturraden dan Menara Teratai Rp20.000 (Sabtu–Minggu Rp25.000); Taman Botani Rp15.000; Taman Maskemambang Rp2.000 | Perubahan kelima Perbup 81/2021. |
| [Perda Kulon Progo 6/2023](https://peraturan.bpk.go.id/Download/336306/Perda%20Kulon%20Progo%20No%206%20Tahun%202023.pdf) | 373 | Waduk Sermo, Puncak Suroloyo, Pantai Trisik Rp10.000 | Rp9.500 jasa sarana + Rp500 asuransi. Perubahan Perda 1/2026 belum diperiksa. |
| [Perda Tulungagung 11/2023](https://peraturan.go.id/files/perda-kabupaten-tulung-agung-no-11-tahun-2023.pdf) | 123 (Lampiran X) | Pantai Popoh, Pantai Sine Rp8.500 (Sabtu–Minggu Rp10.000) | Popoh dan Sidem berbagi satu baris tarif. |
| [Perda Ngawi 10/2023](https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf) | 122 (Lampiran II) | Wisata Tawun Rp10.000 | Dokumen sama dengan sumber Museum Trinil. Wahana dikenai tarif terpisah. |
| [Perda Kudus 4/2023](https://peraturan.go.id/files/perda-kabupaten-kudus-no-4-tahun-2023.pdf) | 120 (Bagian 5) | Taman Krida Wisata Rp3.000; Museum Kretek Rp4.000 | Tarif selain hari Minggu/besar; Minggu/besar Rp4.000 dan Rp5.000. |
| [Perda Lumajang 1/2024](https://www.peraturan.go.id/files/perda-kabupaten-lumajang-no-1-tahun-2024.pdf) | 141 | Selokambang Rp7.000; Ranu Klakah dan Ranu Pakis Rp4.000 | Tarif dewasa; Selokambang hari tertentu Rp15.000. |
| [Perda Klaten 15/2023](https://peraturan.bpk.go.id/Download/335721/2023pd3310015.pdf) | 187–188 | Makam Sunan Pandanaran Rp2.000; Taman Nyi Ageng Rakit Rp10.000 | Tarif domestik; Bukit Sidoguro dan Taman Nyi Ageng Rakit satu baris tarif. |
| [Perda Tegal 11/2023](https://peraturan.bpk.go.id/Download/335762/1705299302_2023pd3328011.pdf) | 240 (Lampiran X) | Guci Rp14.400; Cacaban Rp8.400 | Dewasa hari biasa; hari libur Rp19.400 dan Rp9.400. |
| [Perda Trenggalek 8/2023](https://peraturan.bpk.go.id/Download/350255/Peraturan%20Daerah%20Kabupaten%20Trenggalek%20Nomor%208%20Tahun%202023%20tentang%20Pajak%20Daerah%20dan%20Retribusi%20Daerah.pdf) | 504 | Pantai Prigi dan Pantai Pelang Rp10.000 | Tarif dewasa sudah termasuk asuransi. |

SHA-256 setiap PDF ada di `provenance.json`. PDF tidak disalin ke repo karena ukurannya besar (sampai 12,5 MB); unduh ulang dari URL di atas dan cocokkan hash-nya.

Tarif adalah nilai dokumen hukum yang diperiksa, bukan jaminan harga transaksi hari ini. Pencarian perubahan aturan dilakukan, tetapi tidak membuktikan bahwa tidak ada perubahan lain.

## Lokasi

- `fetch_locations.py` (Nominatim) dan `fetch_overpass.py` (Overpass, pencarian nama dalam kotak wilayah) menyimpan setiap respons beserta URL, waktu akses, dan hash di `sources/`. Hasil kosong juga disimpan sebagai jejak audit.
- Jeda antarpermintaan di atas 1 detik dan hasil di-cache, sesuai kebijakan Nominatim.
- Titik yang dipakai bukan selalu objeknya sendiri: Puncak Suroloyo dan Pantai Popoh memakai titik area parkir bernama objek, karena objeknya sendiri tidak dipetakan. Ini tercatat di `coordinate_method`.
- Data OSM berlisensi **ODbL 1.0**, atribusi **© OpenStreetMap contributors**.

## Rating Google Maps

`google_maps_rating_review.json` mencatat hasil observasi manual melalui browser: nama listing, rating, jumlah ulasan, URL tempat, koordinat listing, dan keputusan pencocokan. Tidak memakai API atau scraper massal.

Enam belas rating cocok nama dan lokasi (`matched_name_location`). Tujuh lainnya **jangan dipakai otomatis**:

| ID | Alasan |
| --- | --- |
| 444 Tasikardi | Listing danau di kawasan yang sama, tetapi listing "Recreation Tasikardi" ditandai Google *Permanently closed*. Status operasional unit rekreasi berbayar perlu dicek. |
| 446 Lokawisata Baturraden | Listing bernama "Baturraden" (pemandian air panas dan air terjun). Lokasinya cocok, namanya berbeda. |
| 447 Taman Botani Baturraden | Panel tempat tidak tampil di browser. Dua listing "Baturraden Botanical Garden" kemungkinan objek lain. |
| 451 Pantai Popoh | Koordinat listing cocok, tetapi alamat listing menyebut Watulimo (Trenggalek). |
| 459 Ranu Pakis | Ada beberapa listing kecil (133, 83, dan 17 ulasan) tanpa listing utama yang jelas. |
| 462 Waduk Cacaban | Dua listing besar (waduk 682 ulasan, taman 562 ulasan) di titik berbeda. |
| 463 Objek Wisata Guci | Kawasan punya beberapa listing besar (14.547, 12.041, dan 8.870 ulasan). |

Rating Google Maps adalah agregat ulasan pihak ketiga, bukan data resmi atau data terbuka, dan nilainya bisa berubah.

## Kandidat yang ditunda

| Kandidat | Alasan |
| --- | --- |
| Goa Kiskendo, Kulon Progo | Tarif Rp10.000 terbukti (halaman yang sama dengan Waduk Sermo), tetapi tidak ada objek OSM di Kulon Progo; hasil bernama Kiskendo berada di Kendal dan Serang. |
| Pantai Sidem, Tulungagung | Tarif terbukti bersama Pantai Popoh, tetapi tidak ada objek OSM. Koordinat Google Maps tidak dipakai sebagai sumber lokasi. |
| Pantai Pangandaran, Batu Hiu, Green Canyon, dll. | Perda Pangandaran 8/2023 hanya menetapkan tarif per kelas (Rp6.000–Rp20.000); kelas tiap objek ditetapkan Keputusan Bupati yang belum ditemukan. |
| Kebun Raya Bogor, Cibodas, Purwodadi | Harga resmi hanya tampil di sistem tiket yang memerlukan login. |
| Mini Zoo dan Art Centre Purworejo | Tarif terbukti di Perda Purworejo 1/2026, tetapi tidak ditemukan di OSM. |
| Kawah Sikidang/Candi Arjuna, Bromo, Goa Gong, Pantai Klayar | Sumber tarif resmi terbaru tidak ditemukan; yang ada berita atau aturan lama. |
| Pantai Congot | Sudah ada di data Kaggle (ID 210). |
| Objek Wisata Colo dan Taman Ria, Kudus | Tarif terbukti di Perda Kudus 4/2023; OSM hanya punya desa Colo dan tidak punya Taman Ria. |
| Batu Seribu dan Makam Balakan, Sukoharjo | Tarif terbukti di Perda Sukoharjo 10/2023 (halaman PDF 143); tidak ada objek OSM. |
| Pesanggrahan Argowilis, Tulungagung | Tarif Rp5.000 terbukti; tidak ada objek OSM. |
| Linggoasri dan Pantai Depok, Pekalongan | Tarif terbukti di Perda Pekalongan 11/2023 (Rp7.250 dan Rp4.750); OSM hanya punya titik desa. |
| Mata Air Cokro, Bukit Sidoguro, Umbul Jolotundo, Deles Indah (Klaten) | Tarif terbukti di Perda Klaten 15/2023; tidak ada objek OSM (Deles hanya dusun). |
| Purwahamba Indah (Pur'in), Tegal | Tarif Rp4.400 terbukti; tidak ada objek OSM. |
| Gedung Naskah Linggarjati dan Kebun Raya Kuningan | Tarif terbukti di Perda Kuningan 1/2024 (Rp10.000 dan Rp9.000); OSM hanya punya desa dan Taman Wisata Alam Linggarjati, bukan objeknya. |
| Goa Lowo dan Pantai Karanggongso, Trenggalek | Tarif terbukti (Rp10.000 dan Rp15.000); tidak ada objek OSM. Karanggongso punya listing Google Maps (4,6; 6.180 ulasan). |
| Jawa Barat dan Banten tambahan | Perda Kota Bogor 11/2023 tidak memuat tarif objek wisata, teks Perda Kota Bandung 1/2024 tidak terbaca (hasil pindai), dan PDF resmi Cianjur serta Cilegon tidak bisa diunduh. |

## Validasi

```powershell
& '.\.venv\Scripts\python.exe' data/review/tambahan_jawa_2026_11/validate.py
```

Uji mencakup header Kaggle, ID unik, tidak ada bentrok nama dengan 443 destinasi, kategori valid, harga dan bukti halaman, titik OSM cocok dengan snapshot dan berada di Pulau Jawa, Rating/Time_Minutes kosong di CSV, serta rating hanya boleh dipakai bila cocok nama dan lokasi.

## Jika kelak diintegrasikan

Integrasi mengubah jumlah destinasi dari 443, sehingga perlu: memperbarui `data_pipeline.py` (`_check_ids`, sumber, `CITY_TO_PROVINCE` untuk Serang, Sumedang, Banyumas, Kulon Progo, Tulungagung), menjalankan ulang preprocessing, impor, dan training, lalu memperbarui test, README, Dokumentasi, laporan, dan Excel. Putuskan dulu empat rating yang belum cocok.
