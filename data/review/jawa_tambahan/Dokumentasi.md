# Tambahan destinasi Jawa di luar Banten

Tanggal penelitian: **30 September 2026**. File: `jawa_kaggle_review.csv`.

## Hasil

Empat destinasi kurasi awal yang tidak muncul sebagai destinasi bernama sama dalam dataset Kaggle 437 baris maupun tambahan Banten. Pengecekan nama dinormalisasi (termasuk Gua/Goa), lalu dicocokkan objek dan kabupatennya. Ini bukan inventaris seluruh destinasi Jawa dan bukan klaim bahwa semua calon tambahan telah ditemukan.

| ID lokal | Destinasi | Kabupaten | Provinsi | Tarif yang disimpan |
| --- | --- | --- | --- | --- |
| 440 | Goa Seplawan | Purworejo | Jawa Tengah | Rp5.000/orang |
| 441 | Pantai Jatimalang | Purworejo | Jawa Tengah | Rp5.000/orang |
| 442 | Kolam Renang Artha Tirta | Purworejo | Jawa Tengah | Rp8.000/orang, hari biasa |
| 443 | Museum Trinil | Ngawi | Jawa Timur | Rp4.000/kunjungan/orang, domestik dewasa |

Semua titik berada di daratan Pulau Jawa. File dipisahkan untuk review; data utama, tambahan Banten, dataset sintetis lama, preprocessing, model K-Means, website dan laporan yang sudah ada **tidak diubah**. Jika seluruhnya kelak disetujui dan digabung tanpa eliminasi: 437 + 2 Banten + 4 tambahan = **443 baris secara aritmetis**, bukan jumlah saat ini di website. Dataset Kaggle masih perlu audit ruang lingkup sendiri karena memuat destinasi pulau lepas pantai dan kemungkinan duplikasi; jangan menyebut 443 sebagai jumlah final khusus daratan Jawa sebelum audit itu.

**Status: draft review, bukan lolos verifikasi seluruh enam kriteria.** Harga bersumber peraturan resmi; koordinat berasal pemetaan komunitas OSM, bukan survei resmi pemerintah. Rating dan durasi kosong. Fasilitas/C2 pengganti serta kriteria lain belum dibuktikan dalam paket ini. Tidak ada harga, rating, atau durasi yang disimulasikan agar terlihat lengkap.

## Struktur dan asal tiap field

Header mentah sama persis dengan Kaggle, termasuk dua kolom tanpa nama:

```text
Place_Id,Place_Name,Description,Category,City,Price,Rating,Time_Minutes,Coordinate,Lat,Long,,
```

| Field | Asal / aturan |
| --- | --- |
| `Place_Id` | ID lokal 440-443, tidak berbenturan dengan Kaggle 1-437 atau Banten 438-439. Bukan ID pemerintah; jangan gabungkan ke dataset sintetis lama tanpa audit ID. |
| `Place_Name` | Nama objek pada tabel tarif peraturan; alias OSM dicocokkan di bawah. |
| `Description` | Kalimat baru, hanya jenis objek, kabupaten/provinsi, kondisi tarif, dan batasan koordinat yang dibuktikan; bukan salinan artikel promosi. |
| `Category` | Crosswalk penyusun ke kategori Kaggle, bukan label resmi pemerintah: goa ke Cagar Alam, pantai ke Bahari, kolam renang ke Taman Hiburan, museum ke Budaya. Cagar Alam di sini tidak menyatakan status hukum perlindungan Goa Seplawan. |
| `City` | Nama kabupaten, bukan kota administratif atau provinsi. Konteks kabupaten dari dokumen hukumnya, lokasi titik dicocokkan dengan hasil OSM/Nominatim. |
| `Price` | Tarif dasar dalam rupiah per orang menurut dokumen yang diperiksa; detail satuan/jenis pengunjung di `provenance.json`. Tidak termasuk parkir, transportasi, makan, penginapan, outbound atau wahana tambahan. |
| `Rating`, `Time_Minutes` | Kosong, bukan 0; tidak ada sumber terbuka terpilih untuk mengisi keduanya. Jam buka dan durasi sewa wahana bukan durasi kunjungan. |
| `Coordinate`, `Lat`, `Long` | Node OSM atau hasil transformasi geometri yang dapat direproduksi; rincian per objek di bawah. Bukan otomatis koordinat pintu masuk. |
| Dua kolom terakhir | Sengaja kosong untuk mempertahankan header Kaggle; di pandas biasanya menjadi `Unnamed: 11` dan `Unnamed: 12`. |

`provenance.json` menyimpan provinsi, objek sumber, URL, halaman tarif, satuan, metode koordinat dan kondisi khusus tanpa menambah kolom baru ke CSV Kaggle.

## Sumber tarif resmi dan bukti visual

### Purworejo: gunakan perubahan tahun 2026

Sumber utama: [Perda Kabupaten Purworejo No. 1 Tahun 2026 tentang Perubahan atas Perda No. 11 Tahun 2023 tentang Pajak Daerah dan Retribusi Daerah](https://peraturan.bpk.go.id/Details/351048/perda-kab-purworejo-no-1-tahun-2026).

- [PDF yang diperiksa](https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf), salinan `sources/perda_purworejo_1_2026.pdf`.
- **Halaman PDF 242 (nomor tercetak 226)**, bagian 6, I Pariwisata: nomor 2 Goa Seplawan Rp5.000/orang; nomor 3 Pantai Jatimalang Rp5.000/orang; nomor 4 Artha Tirta hari biasa Rp8.000/orang, hari besar/libur Rp10.000/orang.
- Bukti visual diperiksa: `sources/tarif_purworejo-242.png`.
- Halaman PDF 243 (tercetak 227) menunjukkan tarif Museum Tosan Aji Rp10.000 untuk masyarakat umum, tetapi destinasi itu ditunda karena lokasi yang ditemukan mengarah alamat lama. Bukti tersimpan `sources/tarif_purworejo-243.png`.
- [Perda lama 11/2023](https://peraturan.bpk.go.id/Details/276973/perda-kab-purworejo-no-11-tahun-2023) ditemukan sebagai dokumen yang diubah. Tarif lama Artha Tirta hari biasa Rp5.000 dan Tosan Aji umum Rp5.000 **tidak digunakan**. Perubahan 2026 telah dicek; jangan mengisi tarif hanya dari hasil pencarian lama.

CSV menyimpan satu `Price`, sehingga harga Artha Tirta hanya sesuai **hari biasa**, bukan seluruh kalender. Untuk penggunaan website, perubahan tarif berdasarkan hari harus ditangani secara eksplisit sebelum integrasi.

### Ngawi: Museum Trinil

Sumber: [Perda Kabupaten Ngawi No. 10 Tahun 2023 tentang Pajak Daerah dan Retribusi Daerah](https://jdih.ngawikab.go.id/peraturan/view/526).

- [PDF resmi pada situs Badan Keuangan Ngawi](https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf), salinan `sources/perda_ngawi_10_2023.pdf`.
- **Halaman PDF 122, nomor tercetak 3 pada Lampiran II**, bagian E.1.b Wisata Museum Trinil: wisatawan domestik dewasa **Rp4.000/kunjungan/orang**.
- Tarif pelajar/anak Rp2.000, mancanegara Rp10.000, serta biaya outbound berbeda dan tidak dimasukkan ke `Price` umum domestik dewasa.
- Bukti visual diperiksa: `sources/tarif_ngawi.png`. Biaya kios dan parkir pada halaman sebelumnya bukan harga tiket masuk.

Tarif adalah nilai dokumen hukum yang berhasil diperiksa, bukan jaminan tarif transaksi aktual hari ini. Pencarian perubahan dokumen dilakukan tetapi tidak membuktikan tidak mungkin ada pembaruan lain. Sebelum publikasi, verifikasi aturan terbaru dan kondisi operasional pengelola.

## Bukti lokasi per destinasi

### ID 440 - Goa Seplawan

- [OSM node 3375853628](https://www.openstreetmap.org/node/3375853628), [API](https://www.openstreetmap.org/api/0.6/node/3375853628.json), snapshot `sources/osm_seplawan.json`.
- Nama OSM **Gua Seplawan**, tag `natural=cave_entrance`: -7.7727565, 110.1101132. Ini titik mulut goa yang dipetakan, bukan loket wisata.
- Pencocokan wilayah: hasil kedua pada `sources/nominatim_seplawan_short.json` mencantumkan Donorejo, Kaligesing, Purworejo, Jawa Tengah.
- Hasil pertama bernama **Gunung Seplawan**, berjenis viewpoint dan berada di Kulonprogo, ditolak karena objek dan wilayah berbeda.
- Pengecekan silang nama serta wilayah menggunakan [E-Wisata Dinporapar Purworejo](https://ewisata.purworejokab.go.id/main/depan), yang menempatkan Goa Seplawan di Donorejo/Kaligesing. Tidak disalin artikel/deskripsi/foto situs tersebut.

### ID 441 - Pantai Jatimalang

- [OSM node 10062766524](https://www.openstreetmap.org/node/10062766524), [API](https://www.openstreetmap.org/api/0.6/node/10062766524.json), snapshot `sources/osm_jatimalang.json`.
- Nama OSM **Pantai Dewaruci Jatimalang**, tag `natural=beach`: -7.8792731, 109.9832511. Ini titik representatif pantai, bukan titik masuk atau parkir.
- `sources/nominatim_jatimalang.json` mencantumkan Jatimalang, Purwodadi, Purworejo, Jawa Tengah.
- [E-Wisata Dinporapar Purworejo](https://ewisata.purworejokab.go.id/main/depan) mencocokkan alias Dewaruci/Jatimalang, kabupaten dan tiket Rp5.000. Situs itu hanya pengecekan silang; nilai utama tarif dari Perda 2026.

### ID 442 - Kolam Renang Artha Tirta

- [OSM way 211416682](https://www.openstreetmap.org/way/211416682), [API geometri lengkap](https://www.openstreetmap.org/api/0.6/way/211416682/full.json), snapshot `sources/osm_artha_tirta_full.json`.
- Tag nama **Artha Tirta Swimming Pool**, designation **Kolam Renang Artha Tirta**, `leisure=swimming_pool`; jenis dan nama cocok tabel hukum.
- `sources/nominatim_artha_tirta.json` menempatkannya di Baledono/Purworejo, Jawa Tengah. Nama kecamatan dari geocoder tidak dijadikan field baru yang mengklaim telah divalidasi administrasi.
- Koordinat -7.7010424, 110.0253756 berasal **tengah bounding box node-node geometri kolam**: `(min_lat + max_lat) / 2`, `(min_lon + max_lon) / 2`, dibulatkan 7 desimal. Bukan gerbang kompleks dan bukan hasil ukur pemerintah. Ketepatan jarak ke loket belum terbukti.

### ID 443 - Museum Trinil

- [OSM node 2376812002](https://www.openstreetmap.org/node/2376812002), [API](https://www.openstreetmap.org/api/0.6/node/2376812002.json), snapshot `sources/osm_trinil.json`.
- Nama OSM **Museum Trinil Ngawi**, tag `tourism=museum`: -7.3743213, 111.357806. Pintu tiket belum dikonfirmasi.
- `sources/nominatim_trinil.json` mencantumkan Kabupaten Ngawi/Jawa Timur. CSV hanya menggunakan kabupaten, tidak mengklaim desa/kecamatan yang dapat berbeda antara sumber sudah tervalidasi.

Geocoder dan API OSM berasal basis pemetaan yang sama, sehingga kesesuaian keduanya **bukan dua bukti independen** akurasi lapangan. Snapshot API menyimpan versi objek dan timestamp perubahan; tanggal perubahan itu berbeda dari tanggal akses. Nama dan tarif dibuktikan dokumen resmi, tetapi keakuratan koordinat terkini tetap perlu review lokasi.

## Lisensi dan penggunaan ulang

Kebijakan sama dengan tambahan Banten: gunakan dokumen peraturan dan OSM; tidak scraping Google Maps, tidak menggunakan Sisparnas, tidak membayar API.

- Dokumen peraturan: dasar penggunaan publik **UU No. 28 Tahun 2014 Pasal 42 huruf b**, bahwa peraturan perundang-undangan tidak memiliki hak cipta. [UU resmi](https://www.peraturan.go.id/files/uu28-2014bt.pdf). Ini **bukan lisensi CC BY eksplisit** dan tidak melisensikan seluruh konten situs pemerintah. Gate yang mewajibkan identifier lisensi terbuka masih memerlukan review manusia atas dasar domain publik tersebut.
- Geometri/fakta OSM: **ODbL 1.0**, atribusi **© OpenStreetMap contributors**. [Copyright OSM](https://www.openstreetmap.org/copyright), [teks lisensi ODbL](https://opendatacommons.org/licenses/odbl/1-0/). Pertahankan atribusi dan ketentuan share-alike yang berlaku ketika mendistribusikan basis data turunan. Tidak otomatis melabeli seluruh dataset Kaggle gabungan sebagai ODbL.
- Situs resmi pariwisata atau berita dipakai hanya untuk pengecekan silang, bukan diasumsikan memiliki lisensi terbuka. Deskripsi baru di CSV tidak menyalin paragraf/foto situs-situs itu.

## Kandidat yang belum dimasukkan

| Kandidat | Alasan ditunda |
| --- | --- |
| Museum Tosan Aji, Purworejo | Tarif baru Rp10.000 terbukti, tetapi hasil OSM way 1124582142 masih menunjuk Jalan Mayjen Sutoyo 10. [Berita DPRD 9 September 2026](https://dprd.purworejokab.go.id/komisi-iii-dprd-purworejo-dorong-museum-tosan-aji-dan-art-center-lebih-gencar-promosi) menempatkan museum di kompleks rumah dinas bupati. Titik alamat lama tidak dipakai untuk lokasi sekarang. |
| Kawasan Geger Menjangan | Tarif Rp2.500/orang terbukti pada Perda 2026, tetapi dua pencarian lokasi tidak menghasilkan objek yang dapat dicocokkan. Koordinat tidak ditebak. |
| Wisata Tawun, Ngawi | Tarif Rp10.000/orang terbukti, tetapi hasil OSM hanya desa Tawun. Pusat desa bukan titik destinasi pemandian, sehingga tidak dimasukkan. |

Pencarian lokasi dilakukan berurutan dengan jeda setidaknya 1,1 detik dan cache: 7 nama terarah + 3 variasi nama terbatasi wilayah. `fetch_locations.py` menyimpan URL, timestamp akses, hash respons dan hasil, tanpa otomatis menerima hasil pertama. File hasil kosong serta hasil salah objek tetap disimpan sebagai jejak audit.

## Validasi dan integritas

Jalankan dari root repo:

```powershell
& '.\.venv\Scripts\python.exe' data/review/jawa_tambahan/validate_jawa.py
```

Uji mencakup header 13 kolom persis Kaggle, jumlah 4 baris, ID/nama unik dibanding Kaggle dan Banten, kategori tersedia di Kaggle, manifest harga, lokasi sesuai snapshot, provinsi/kabupaten pada geocoder, nilai kosong dan hash PDF. Lolos uji **bukan** pengesahan semua kriteria, lisensi seluruh gabungan, harga operasional terkini, atau koordinat pintu tiket.

| Salinan sumber | SHA-256 |
| --- | --- |
| `perda_purworejo_1_2026.pdf` | `14BBACA980EC61BF5D80DE14A22AF3C928DB155E0A518C1E3B16C490DFD89F9E` |
| `perda_ngawi_10_2023.pdf` | `17734B346CCCC24EACC9DCDB3BFBD520F17C4B317DE6314A7BD3CF8EAF1B4B4C` |

Belum diimputasi, digabung, dilatih atau diberi cluster. Jangan mengisi rating kosong dengan 0; jangan menyamakan C2 pengganti dengan rating Google. Selesaikan atribut wajib dan review sebelum integrasi produksi.
