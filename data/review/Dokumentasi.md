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

- [GeoNames Free Gazetteer Data](https://www.geonames.org/export/) menyediakan unduhan negara gratis dengan atribusi. [Readme skema dan lisensi GeoNames](https://download.geonames.org/export/dump/readme.txt) menyatakan CC BY 4.0. Arsip yang dibaca: `https://download.geonames.org/export/dump/ID.zip`, diunduh 29 September 2026, SHA-256 `13ef08cb535b85053afdebdc9268caa2408b749f5d6f8721dda64c4b8f0b13a6`. Arsip lokal `ID.zip` tidak dimasukkan Git agar repo tidak membengkak; `ID.source.json` dan manifest menyimpan URL, tanggal akses, dan hash, serta memaksa arsip yang dipakai cocok dengan hash tersebut. Beri atribusi **GeoNames, CC BY 4.0** bila hasil turunannya digunakan.
- Filter fitur mengacu ke [daftar kode resmi GeoNames](https://www.geonames.org/export/codes.html). Kode dan kategorinya tersimpan di `scripts/open_data_review/geonames.py`; `feature_code` asli dan `geonameid` dipertahankan untuk setiap baris.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) berlisensi ODbL dengan kewajiban atribusi/share-alike sesuai penggunaan. Skor C2 dirancang dari snapshot OSM bertanggal, tetapi **tidak ada snapshot OSM yang berhasil diperoleh dalam run ini**. Dua query Overpass yang dibatasi di Bali mendapat HTTP 504, termasuk area sangat kecil. Pemeriksaan unduhan ekstrak regional [Geofabrik Maluku](https://download.geofabrik.de/asia/indonesia/maluku.html) juga timeout; tidak dilakukan pengambilan massal atau bypass batas server. Karena itu C2 untuk seluruh 4.215 kandidat **belum dihitung**, bukan bernilai 0.
- Asal 1.900 lama adalah `scripts/generate_synthetic_tourism_dataset.py`, bukan hasil penyalinan 1.900 baris resmi Sisparnas. Asal 437 lama adalah berkas Kaggle lokal; lisensi dan nilai lapangan per baris tidak diasumsikan terverifikasi. Hash ketiga input run ada di `source_manifest.json`.

## Aturan kelulusan

Baris baru masuk `destinations_verified_open.csv` hanya bila bukti item-spesifik dengan URL/ID, tanggal akses, referensi lisensi spesifik, dan **persetujuan peninjau manusia** tersedia untuk identitas, lokasi dan titik masuk, C1 harga tiket WNI saat berlaku atau bukti eksplisit gratis, snapshot C2 dengan cakupan seluruh radius 2 km, C4 toilet/parkir/warung/musala (masing-masing `ya` **atau** `tidak` harus eksplisit), C5 kategori dari taksonomi TravelFit, serta C6 aktivitas. Nama tempat dari GeoNames hanya menjadi **catatan belum ditinjau** tentang identitas kandidat dan kode fitur menjadi kategori awal. Koordinat gazetteer belum cukup untuk menyatakan posisi pintu masuk. Kekosongan tag tidak membuktikan fasilitas tidak ada. Sumber yang bisa dibaca gratis tetapi hak pakai ulangnya tidak jelas tidak otomatis diterima. Kolom `reviewer`/`review_decision` merekam keputusan manusia, bukan pembuktian otomatis isi halaman.

C2 baru = jumlah dari empat jenis layanan **terpetakan** dalam garis lurus 2 km: transportasi umum, layanan kesehatan, ATM/bank, dan penginapan (skor 0–4). C2 hanya dihitung dari **koordinat lokasi yang sudah disetujui**, bukan titik mentah atau bukti yang belum ditinjau. Sebuah snapshot berbatas koordinat hanya boleh dipakai bila **seluruh lingkaran 2 km** di sekitar tempat berada dalam batas query yang tercatat dan query-nya cocok dengan templat lengkap semua kelas layanan (tanpa pembatas jumlah hasil). Bukti `c2_snapshot` harus menunjuk endpoint yang sama dengan snapshot; untuk endpoint Overpass resmi di pipeline ini, lisensinya merujuk halaman ODbL OSM. Jika snapshot lengkap kelak menghasilkan 0, maknanya hanya “tidak ada objek cocok yang terpetakan pada snapshot tersebut”, bukan tidak ada layanan di lapangan. Setiap scan nantinya diekspor ke berkas bukti dengan ID objek dan hash snapshot. Bobot AHP dan fitur K-Means perlu ditinjau/dilatih ulang **setelah** ada data yang lolos, bukan pada tahap audit ini.

## Pemeriksaan sampel dan risiko

- `geonames:11054658` Echo Beach, Bali (pantai), `geonames:11696116` Bali Zoo (rekreasi), `geonames:12069296` Monumen Trikora (budaya), dan `geonames:1960432` Kebun Binatang Ragunan telah diperiksa sebagai sampel lintas kategori/wilayah pada data mentah. Kode fitur dan titik sumber tercatat, tetapi harga, C2, C4, dan aktivitas belum terbukti.
- `geonames:12024132` Pura Puseh Desa Adat Datah memiliki label administrasi “Sulawesi Tengah” sementara koordinat sumbernya `-8.34119, 115.59513` berada di area Bali. Ini **indikasi konflik yang perlu pemeriksaan manual**, sehingga label provinsi GeoNames tidak otomatis diterima sebagai bukti lokasi.
- Kebun Binatang Ragunan muncul juga sebagai `kaggle_437:7` dengan titik mentah yang berdekatan. Keduanya ditandai `possible_duplicate`; tidak dihapus atau digabung otomatis. Total 80 kandidat terkena penanda duplikat potensial. Nama provinsi sumber belum dinormalisasi (misalnya `North Sumatra`/`Sumatera Utara`), sehingga penanda duplikat mungkin belum lengkap.
- GeoNames memakai nama/provinsi yang sebagian berbahasa Inggris atau historis, dan cakupan landmark sangat timpang (didominasi danau). Inventaris ini belum memenuhi definisi dataset wisata representatif untuk evaluasi model.

## Berkas dan cara melanjutkan

- `destinations_candidate_audit.csv`: 4.215 kandidat, asal, seluruh atribut mentah di `raw_json` dengan `untrusted_fields`, status dan alasan.
- `destination_evidence.csv`: 3.756 catatan sumber otomatis yang hanya menyangkut identitas/kategori awal GeoNames; semuanya **belum ditinjau**. Tidak ada bukti tiket/fasilitas yang dibuat-buat.
- `destinations_verified_open.csv`: hanya baris lolos (saat ini 0); `Rating` sengaja kosong karena C2 baru memakai `c2_services`.
- `audit_summary.md`: hitungan alasan dan cakupan mentah; `source_manifest.json`: URL, lisensi, parameter, dan SHA-256 input.

Jalankan ulang setelah mengunduh `ID.zip` dari URL di atas (hash dapat berubah pada rilis harian):

```powershell
& '.\.venv\Scripts\python.exe' -m scripts.open_data_review.cli --geonames-zip data/review/ID.zip --output-dir data/review
```

Untuk mengisi bukti manual, sediakan CSV dengan kolom `candidate_id,field,value,source_ref,accessed_at,reuse_status,note,license_ref,reviewer,reviewed_at,review_decision,valid_on`, kemudian tambahkan `--evidence-csv PATH`. Nilai `location` ditulis sebagai JSON `{"lat":...,"lon":...,"city":"...","province":"..."}`; boolean C4 sebagai `true`/`false`. Catatan C1 harus menjelaskan `ticket_kind=domestic;currency=IDR` dan, jika 0, `explicit free`; isi `valid_on` dengan tanggal harga ditinjau (maksimal 365 hari lalu). Catatan C4 harus menyebut `explicit present` atau `explicit absent`; kategori menyertakan `source tag=...`; aktivitas `explicit activity`. Bukti lokasi titik gazetteer harus menyatakan `entrance_checked` setelah verifikasi independen; jika label provinsi/koordinat lama keliru, tulis `province_corrected`/`coordinate_corrected` dengan sumber independen. `reuse_status` hanya menerima lisensi spesifik seperti `cc-by-4.0`, `odbl`, `cc0`, atau `public-domain`, bersama `license_ref` HTTPS **berupa halaman hak pakai pada situs sumber yang sama** (atau halaman resmi OSM/GeoNames/Geofabrik yang sudah dikenal), bukan tautan umum ke teks CC BY. Setiap atribut memerlukan `reviewer`, `reviewed_at`, dan `review_decision=approved`. Sekadar mengisi CSV tidak menggantikan audit manual atas halaman sumber, masa berlaku tiket, dan izin penggunaannya.

Untuk pasangan `possible_duplicate`, tambahkan baris bukti `field=duplicate_resolution` yang ditinjau. Nilai JSON dapat berupa `{"decision":"distinct","peer_ids":["id_lawan"]}` **pada kedua tempat** bila memang berbeda; atau satu baris `{"decision":"alias","canonical_id":"id_utama","peer_ids":["id_utama"]}` pada alias dan `{"decision":"canonical","peer_ids":["id_alias"]}` pada tempat utama. Alias ditolak dari subset siap pakai; identitas utama baru dapat lolos bila semua alias berpasangan sudah diselesaikan. Keputusan yang saling bertentangan tetap `pending`. Semua keputusan tetap tercatat dalam audit.

Jangan memindahkan `destinations_verified_open.csv` ke website atau melatih K-Means sebelum ada baris yang lolos dan rancangan C2/AHP disepakati untuk integrasi.
