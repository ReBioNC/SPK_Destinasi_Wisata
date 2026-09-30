# Tambahan destinasi Banten untuk TravelFit

Tanggal penelitian dan akses: **30 September 2026**.

## 1. Hasil dan batasan

File `banten_kaggle_review.csv` berisi **2 destinasi kurasi awal**, bukan data sintetis hasil pengacakan. Nama destinasi dan tarif masuk mempunyai bukti dokumen peraturan pemerintah. Koordinat berasal dari pemetaan komunitas OpenStreetMap (OSM), **bukan koordinat resmi hasil survei pemerintah**. Jangan menyebut keseluruhan file sebagai dataset resmi pemerintah.

File ini sengaja terpisah: dataset Kaggle 437 baris, data sintetis lama, hasil preprocessing, model K-Means, dan website tidak diubah. Jika kelak kedua baris disetujui dan digabung ke Kaggle tanpa eliminasi, jumlah aritmetisnya 439; itu **belum** jumlah data yang digunakan website saat ini.

**Status: draft review; belum lolos verifikasi seluruh kriteria rekomendasi.** Rating dan durasi tidak tersedia dari sumber terbuka yang digunakan. Koordinat adalah titik representatif, bukan titik pintu masuk terverifikasi. Kebutuhan skor fasilitas/C2 pengganti dan kriteria lain tetap perlu diperiksa sebelum masuk pipeline produksi. Tidak ada nama reviewer manusia atau persetujuan yang direkayasa.

## 2. Struktur persis mengikuti CSV Kaggle

Header disamakan dengan `data/raw/tourism_with_id.csv`, termasuk urutan dan dua kolom tanpa nama:

```text
Place_Id,Place_Name,Description,Category,City,Price,Rating,Time_Minutes,Coordinate,Lat,Long,,
```

| Field | Kebijakan |
| --- | --- |
| `Place_Id` | ID lokal 438 dan 439, di luar rentang Kaggle 1-437. Bukan ID pemerintah. Belum dipastikan unik terhadap dataset sintetis lama; jangan gabungkan secara buta ke dataset tersebut. |
| `Place_Name` | Nama destinasi yang tercantum di dokumen peraturan. |
| `Description` | Kalimat baru yang dirangkai dari fakta sumber, ditambah penjelasan asal titik lokasi; bukan salinan artikel promosi. |
| `Category` | Pemetaan ke kategori Kaggle oleh penyusun: Tahura ke `Cagar Alam`, museum ke `Budaya`. `Cagar Alam` di sini kategori dataset, **bukan klaim bahwa status hukum Tahura adalah cagar alam**. |
| `City` | Kabupaten lokasi titik: Pandeglang dan Lebak; bukan nama provinsi. Province Banten dicatat di dokumentasi karena CSV Kaggle tidak memiliki field Province. |
| `Price` | Tarif dasar pengunjung umum domestik, dalam rupiah per orang. Bukan total biaya perjalanan. |
| `Rating` | Kosong: tidak ada rating resmi terverifikasi yang dapat digunakan dari sumber terbuka terpilih. Tidak diisi 0 atau angka buatan. |
| `Time_Minutes` | Kosong: belum ada durasi kunjungan yang dibuktikan. Jam buka tidak dianggap durasi kunjungan. |
| `Coordinate` | Representasi dictionary latitude/longitude yang konsisten dengan `Lat` dan `Long`. |
| `Lat`, `Long` | Titik representatif OSM; rincian metode di bagian destinasi. |
| Dua kolom terakhir | Tetap kosong demi kesamaan header. Di pandas biasanya menjadi `Unnamed: 11` dan `Unnamed: 12`; bukan fitur wisata. |

Sumber gratis bukan otomatis memiliki lisensi terbuka. Dokumen peraturan yang dipakai mempunyai dasar penggunaan publik karena peraturan perundang-undangan termasuk objek yang tidak memiliki hak cipta menurut **UU No. 28 Tahun 2014 Pasal 42 huruf b** ([dokumen UU](https://www.peraturan.go.id/files/uu28-2014bt.pdf)). Ini dasar domain publik untuk dokumen hukumnya, **bukan klaim lisensi CC BY untuk seluruh situs pemerintah**, dan berbeda dari lisensi terbuka eksplisit. Jika gate internal hanya menerima identifier lisensi seperti CC BY/ODbL, status domain publik berdasarkan undang-undang perlu ditinjau manusia; jangan otomatis menandai lolos.

Bagian geometri OSM tersedia dengan **ODbL 1.0**, dengan atribusi **© OpenStreetMap contributors**. Pertahankan atribusi dan ketentuan ODbL jika data ini didistribusikan atau dikembangkan. Lihat [copyright OSM](https://www.openstreetmap.org/copyright) dan [teks lisensi ODbL](https://opendatacommons.org/licenses/odbl/1-0/). Dokumentasi ini tidak mengubah lisensi dataset Kaggle atau mengklaim seluruh gabungan otomatis memiliki satu lisensi.

## 3. Bukti per destinasi

### ID 438 - Taman Hutan Raya Banten

**Identitas, deskripsi dan wilayah:** [Perda Provinsi Banten No. 7 Tahun 2023 tentang Pengelolaan Taman Hutan Raya Banten](https://jdih.bantenprov.go.id/storage/places/peraturan/2023pd0036007_1705639297.pdf). Halaman PDF 1 memuat identitas dan wilayah Pandeglang serta Serang; halaman PDF 5 menjelaskan fungsi kawasan; halaman PDF 28 menjelaskan kawasan Carita di Pandeglang. Wilayah keseluruhan Tahura lintas kabupaten; `City=Pandeglang` mengacu titik Balai Tahura, bukan membatasi seluruh kawasan ke satu kabupaten.

**Harga 8000:** [Perda Provinsi Banten No. 1 Tahun 2024 tentang Pajak Daerah dan Retribusi Daerah](https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf), **halaman PDF 261** (nomor tercetak lampiran **4**), bagian E.a, karcis masuk pengunjung umum wisatawan Nusantara: **Rp8.000/orang/hari**. Tarif wisatawan mancanegara Rp100.000 berbeda dan tidak digunakan. Tarif parkir, tracking, camping, canopy trail, penginapan, serta jasa lain tidak dijumlahkan ke `Price`.

Bukti visual: `sources/tarif_tahura.png`; PDF utuh: `sources/perda_banten_1_2024.pdf`.

**Koordinat:** [OSM node 6728713222 - Balai Tahura](https://www.openstreetmap.org/node/6728713222), [API objek](https://www.openstreetmap.org/api/0.6/node/6728713222.json). Node v1, waktu perubahan sumber `2019-08-21T04:45:08Z`, memuat nama Balai Tahura, alamat Kabupaten Pandeglang/Banten, serta latitude **-6.2926599**, longitude **105.8412076**. Pencarian terbatasi Carita juga mencocokkan Balai Tahura di Jalan Curug Putri. Snapshot: `sources/osm_balai_tahura.json` dan `sources/nominatim_tahura_bounded.json`.

**Keterbatasan penting:** titik ini lokasi balai/objek attraction yang dipetakan, belum dibuktikan sebagai loket/pintu wisata; jangan mengklaim jarak rute ke pintu masuk sudah akurat. Perubahan OSM terakhir lama, sehingga akurasi lokasi terkini masih perlu pengecekan. Rating, durasi, dan inventaris fasilitas tidak tersedia dari bukti ini.

### ID 439 - Museum Multatuli

**Nama dan harga 2000:** [Perda Kabupaten Lebak No. 1 Tahun 2025, perubahan atas Perda No. 8 Tahun 2023 tentang Pajak Daerah dan Retribusi Daerah](https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf), **halaman PDF 232** (nomor tercetak **232**), tabel objek retribusi nomor 9: umum **Rp2.000/orang**; anak/pelajar Rp1.000/orang; mancanegara Rp15.000/orang. Dataset menggunakan tarif umum domestik. Tarif sewa pendopo, area museum, foto/video pada halaman lain bukan harga tiket dan tidak digunakan.

Bukti visual: `sources/tarif_multatuli.png`; PDF utuh: `sources/perda_lebak_1_2025.pdf`.

**Koordinat, pengelola dan tipe:** [OSM way 1050591125 - Museum Multatuli](https://www.openstreetmap.org/way/1050591125), [API geometri lengkap](https://www.openstreetmap.org/api/0.6/way/1050591125/full.json). Way v3, waktu perubahan sumber `2023-09-03T10:48:05Z`, memuat nama, `addr:city=Lebak`, `tourism=museum`, `museum=history`, serta operator Unit Pelayanan Teknis Dinas Kebudayaan dan Pariwisata Kabupaten Lebak. Snapshot: `sources/osm_multatuli_full.json`.

Titik **-6.36052505, 106.24725905** dihitung dari tengah bounding box node-node bangunan: `(min_lat + max_lat) / 2` dan `(min_lon + max_lon) / 2`. Ini transformasi geometri yang bisa direproduksi, **bukan pengukuran baru atau koordinat pintu masuk**.

**Pengecekan silang resmi:** [profil Museum Multatuli Kementerian Kebudayaan](https://museum.kemenbud.go.id/museum/profile/museum%2Bmultatuli) mencantumkan Kabupaten Lebak/Banten, pengelola UPT museum, dan tiket Rp2.000 saat buka. [Situs pengelola museum](https://museummultatuli.id/) juga menampilkan tarif umum Rp2.000. Halaman tersebut hanya sebagai pengecekan silang; tidak diasumsikan berlisensi terbuka dan artikel/fotonya tidak disalin menjadi dataset. Nilai utama tarif bersumber dokumen peraturan dan fakta pengelola/geometri bersumber OSM.

Rating dan durasi kunjungan tidak diisi. Angka 0 pada jadwal hari tutup bukan bukti tiket gratis.

## 4. Jejak penelitian dan validasi

- Tahura dan museum dipilih karena tarif masuk dapat dibaca dan dicocokkan secara visual di dokumen resmi, bukan karena jumlah destinasi harus banyak.
- Cisolong dan Cikoromoy dipertimbangkan. Nama keduanya ada di tabel 2.18 [Lampiran Perbup Pandeglang No. 66 Tahun 2024](https://peraturan.bpk.go.id/Download/379746/No.66%20Tahun%202024%20Lampiran.pdf), halaman PDF 42. Tetapi PDF Perda Pandeglang No. 4 Tahun 2023 yang berhasil terbaca dari BPK tidak menyertakan tabel lampiran tarif yang diperlukan. Karena belum membuktikan tarif tepat untuk objeknya, keduanya **tidak ditambahkan** dan harga dari artikel tidak ditebak.
- Dua permintaan terbatas Overpass gagal (504/timeout). Alternatif yang berhasil ialah API satu objek OSM dan pencarian Nominatim terbatas Carita. Tidak dilakukan crawl besar, scraping Google Maps, atau pengambilan Sisparnas.
- Pencarian Nominatim pertama menghasilkan Taman dan Hutan Kota Sangga Buana di Jakarta. Hasil tersebut **ditolak karena salah objek**, tersimpan hanya sebagai jejak penelitian (`sources/nominatim_tahura.json`), tidak dipakai untuk data.
- URL pencarian terbatasi: `https://nominatim.openstreetmap.org/search?q=Tahura&viewbox=105.82,-6.23,105.90,-6.31&bounded=1&format=jsonv2&limit=3`.
- Harga adalah tarif **menurut dokumen yang diperiksa**, bukan jaminan tarif transaksi aktual sepanjang waktu. Sebelum publikasi, cek pembaruan peraturan dan konfirmasi operasional pengelola. Draft belum menyatakan semua kemungkinan perubahan regulasi sudah tercakup.
- `validate_banten.py` menguji kesamaan header mentah Kaggle, jumlah kolom, ID, kategori, tarif, nilai kosong, dan konsistensi koordinat terhadap snapshot. Lolos uji struktur bukan pengesahan semua kriteria atau kebenaran operasional lapangan.

Jalankan dari root repo:

```powershell
& '.\.venv\Scripts\python.exe' data/review/banten/validate_banten.py
```

## 5. Integritas bukti unduhan

SHA-256 berikut mengidentifikasi salinan yang diperiksa. Tanggal perubahan pada objek OSM bukan tanggal akses.

| File sumber | SHA-256 |
| --- | --- |
| `perda_banten_1_2024.pdf` | `A20E0577E219E130BCB6E444085909647E735DB7547CB44FB18867F73ED7DC43` |
| `perda_banten_7_2023.pdf` | `E634A1C7D0AEDAE52197FE766BB2DF74AA06B2E12A8E357E0F3AD1643158FFE4` |
| `perda_lebak_1_2025.pdf` | `AEB134F4C12B56779C5DB3EEC217A510ED314803EEE401B08416DC885F26EE1C` |
| `osm_balai_tahura.json` | `154403C6B70CD7C9E98EEF68D31E7D98703EEB63FF1E1F91B1582DE8CAA153FF` |
| `osm_multatuli_full.json` | `0350F62EC3A99CC4C34478E73978CAC17384012ED42276C2A010EF9C84FC9BDB` |
| `nominatim_tahura_bounded.json` | `7508B3C70B0C760843E256B2F0954B64F2C912BD9901C97BB8D86D245B0FDA0C` |

## 6. Penggunaan dalam laporan dan model

Kalimat yang aman: **"Data utama berasal dari Kaggle dan dilengkapi dua calon destinasi Banten hasil kurasi dokumen peraturan serta OpenStreetMap; atribut yang belum tersedia tidak direkayasa."** Jangan menulis semua data sintetis kini resmi, semua destinasi Jawa telah terwakili, atau semua enam kriteria telah terverifikasi.

Jangan mengisi rating kosong dengan nol atau menyamakan C2 pengganti dengan rating Google. Dataset ini belum diimputasi, belum digabung, belum dilatih, dan belum diberi cluster. Untuk produksi, putuskan fitur model sesuai bukti yang benar-benar tersedia, selesaikan kriteria wajib dan review lokasi, serta pertahankan asal setiap atribut.
