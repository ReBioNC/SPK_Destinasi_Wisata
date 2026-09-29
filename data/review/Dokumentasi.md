# Dokumentasi kurasi terbuka TravelFit — untuk ditinjau

Tanggal audit: 29 September 2026. Semua berkas di folder ini **terpisah dari dataset dan website aktif**. Tidak ada data yang diimpor ke Django, tidak ada bobot AHP yang diubah, dan K-Means belum dilatih ulang.

## Hasil aktual

| Asal | Jumlah | Perlakuan |
| --- | ---: | --- |
| `Dataset_Wisata_38_Provinsi.xlsx` | 1.900 | Kandidat sintetis lama; angka generator bukan bukti fakta. |
| `data/raw/tourism_with_id.csv` | 437 | Kandidat Kaggle lama; atributnya perlu pembuktian ulang. |
| GeoNames Indonesia | 1.878 | Kandidat landmark baru, bukan otomatis objek wisata siap rekomendasi. |
| **Total audit** | **4.215** | **4.215 pending; 0 terverifikasi.** |

GeoNames menyumbang 1.547 danau, 99 pantai, 80 air terjun, 41 taman, 41 tempat ibadah, 20 kawasan lindung, 19 gunung berapi, dan sejumlah landmark budaya/rekreasi lain menurut *feature code* sumber. Puncak dan gunung generik (19.169 entri) sengaja tidak dimasukkan agar jumlah besar tidak disalahartikan sebagai objek wisata. Bahkan kandidat yang dimasukkan belum tentu bisa dikunjungi atau memiliki tiket/fasilitas; semua tetap `pending` sampai lolos pemeriksaan per tempat.

`destinations_verified_open.csv` sengaja hanya berisi header karena belum ada destinasi yang memenuhi seluruh syarat. Ini **bukan** dataset pengganti siap latih/siap tampil. Harga 0 dan rating dari generator tidak dipromosikan menjadi bukti, dan rating tidak lagi digunakan sebagai C2 pada rancangan baru.

## Sumber, lisensi, dan jejak berkas

- [GeoNames Free Gazetteer Data](https://www.geonames.org/export/) menyediakan unduhan negara gratis dengan atribusi. [Readme skema dan lisensi GeoNames](https://download.geonames.org/export/dump/readme.txt) menyatakan CC BY 4.0. Arsip yang dibaca: `https://download.geonames.org/export/dump/ID.zip`, diunduh 29 September 2026, SHA-256 `13ef08cb535b85053afdebdc9268caa2408b749f5d6f8721dda64c4b8f0b13a6`. Arsip lokal `ID.zip` tidak dimasukkan Git agar repo tidak membengkak; manifest menyimpan URL, tanggal akses, dan hash. Beri atribusi **GeoNames, CC BY 4.0** bila hasil turunannya digunakan.
- Filter fitur mengacu ke [daftar kode resmi GeoNames](https://www.geonames.org/export/codes.html). Kode dan kategorinya tersimpan di `scripts/open_data_review/geonames.py`; `feature_code` asli dan `geonameid` dipertahankan untuk setiap baris.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) berlisensi ODbL dengan kewajiban atribusi/share-alike sesuai penggunaan. Skor C2 dirancang dari snapshot OSM bertanggal, tetapi **tidak ada snapshot OSM yang berhasil diperoleh dalam run ini**. Dua query Overpass yang dibatasi di Bali mendapat HTTP 504, termasuk area sangat kecil. Pemeriksaan unduhan ekstrak regional [Geofabrik Maluku](https://download.geofabrik.de/asia/indonesia/maluku.html) juga timeout; tidak dilakukan pengambilan massal atau bypass batas server. Karena itu C2 untuk seluruh 4.215 kandidat **belum dihitung**, bukan bernilai 0.
- Asal 1.900 lama adalah `scripts/generate_synthetic_tourism_dataset.py`, bukan hasil penyalinan 1.900 baris resmi Sisparnas. Asal 437 lama adalah berkas Kaggle lokal; lisensi dan nilai lapangan per baris tidak diasumsikan terverifikasi. Hash ketiga input run ada di `source_manifest.json`.

## Aturan kelulusan

Baris baru masuk `destinations_verified_open.csv` hanya bila bukti item-spesifik dengan URL/ID, tanggal akses, dan hak pakai jelas tersedia untuk identitas, lokasi dan titik masuk, C1 harga tiket WNI saat berlaku atau bukti eksplisit gratis, snapshot C2 dan empat kelas layanan dalam radius 2 km, C4 toilet/parkir/warung/musala (masing-masing `ya` **atau** `tidak` harus eksplisit), C5 kategori, serta C6 aktivitas. Nama tempat dari GeoNames hanya menjadi bukti identitas kandidat dan kode fitur menjadi bukti kategori awal. Koordinat gazetteer belum cukup untuk menyatakan posisi pintu masuk. Kekosongan tag tidak membuktikan fasilitas tidak ada. Sumber yang bisa dibaca gratis tetapi hak pakai ulangnya tidak jelas tidak otomatis diterima.

C2 baru = jumlah dari empat jenis layanan **terpetakan** dalam garis lurus 2 km: transportasi umum, layanan kesehatan, ATM/bank, dan penginapan (skor 0–4). Jika snapshot lengkap kelak menghasilkan 0, maknanya hanya “tidak ada objek cocok yang terpetakan pada snapshot tersebut”, bukan tidak ada layanan di lapangan. Bobot AHP dan fitur K-Means perlu ditinjau/dilatih ulang **setelah** ada data yang lolos, bukan pada tahap audit ini.

## Pemeriksaan sampel dan risiko

- `geonames:11054658` Echo Beach, Bali (pantai), `geonames:11696116` Bali Zoo (rekreasi), `geonames:12069296` Monumen Trikora (budaya), dan `geonames:1960432` Kebun Binatang Ragunan telah diperiksa sebagai sampel lintas kategori/wilayah pada data mentah. Kode fitur dan titik sumber tercatat, tetapi harga, C2, C4, dan aktivitas belum terbukti.
- `geonames:12024132` Pura Puseh Desa Adat Datah memiliki label administrasi “Sulawesi Tengah” sementara koordinat sumbernya `-8.34119, 115.59513` berada di area Bali. Ini **indikasi konflik yang perlu pemeriksaan manual**, sehingga label provinsi GeoNames tidak otomatis diterima sebagai bukti lokasi.
- Kebun Binatang Ragunan muncul juga sebagai `kaggle_437:7` dengan titik mentah yang berdekatan. Keduanya ditandai `possible_duplicate`; tidak dihapus atau digabung otomatis. Total 80 kandidat terkena penanda duplikat potensial. Nama provinsi sumber belum dinormalisasi (misalnya `North Sumatra`/`Sumatera Utara`), sehingga penanda duplikat mungkin belum lengkap.
- GeoNames memakai nama/provinsi yang sebagian berbahasa Inggris atau historis, dan cakupan landmark sangat timpang (didominasi danau). Inventaris ini belum memenuhi definisi dataset wisata representatif untuk evaluasi model.

## Berkas dan cara melanjutkan

- `destinations_candidate_audit.csv`: 4.215 kandidat, asal, atribut mentah berlabel `unverified`, status dan alasan.
- `destination_evidence.csv`: 3.756 rekaman bukti otomatis yang hanya menyangkut identitas/kategori awal GeoNames. Tidak ada bukti tiket/fasilitas yang dibuat-buat.
- `destinations_verified_open.csv`: hanya baris lolos (saat ini 0); `Rating` sengaja kosong karena C2 baru memakai `c2_services`.
- `audit_summary.md`: hitungan alasan dan cakupan mentah; `source_manifest.json`: URL, lisensi, parameter, dan SHA-256 input.

Jalankan ulang setelah mengunduh `ID.zip` dari URL di atas (hash dapat berubah pada rilis harian):

```powershell
& '.\.venv\Scripts\python.exe' -m scripts.open_data_review.cli --geonames-zip data/review/ID.zip --output-dir data/review
```

Untuk mengisi bukti manual, sediakan CSV dengan kolom `candidate_id,field,value,source_ref,accessed_at,reuse_status,note`, kemudian tambahkan `--evidence-csv PATH`. Nilai `location` ditulis sebagai JSON `{"lat":...,"lon":...,"city":"...","province":"..."}`; boolean C4 sebagai `true`/`false`. Catatan C1 harus menjelaskan `ticket_kind=domestic;currency=IDR` dan, jika 0, `explicit free`. Catatan C4 harus menyebut `explicit present` atau `explicit absent`; kategori menyertakan `source tag=...`; aktivitas `explicit activity`. Bukti lokasi titik gazetteer harus menyatakan `entrance_checked` setelah verifikasi independen. `reuse_status` hanya boleh lisensi terbuka yang jelas. Sekadar mengisi CSV tidak menggantikan audit manual atas halaman sumber dan izin penggunaannya.

Jangan memindahkan `destinations_verified_open.csv` ke website atau melatih K-Means sebelum ada baris yang lolos dan rancangan C2/AHP disepakati untuk integrasi.
