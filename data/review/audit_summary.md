# TravelFit — audit kandidat sumber terbuka

Kandidat: **4215**; terverifikasi: **0**; pending: **4215**; ditolak: **0**.

File ini untuk peninjauan. Website, dataset produksi, bobot AHP, dan K-Means **belum diubah**.
Harga/rating berlabel `raw_unverified` tidak boleh dipakai sebagai fakta. Rating di hasil siap pakai sengaja kosong karena C2 baru adalah layanan sekitar terpetakan.
Skor C2=0 berarti tidak ada layanan dalam empat kelas yang *terpetakan* pada snapshot dan radius 2 km, bukan tidak ada layanan di dunia nyata.

## Asal kandidat

- geonames: 1878
- kaggle_437: 437
- synthetic_1900: 1900

## Alasan tertahan

- missing:c1_ticket_price: 4215
- missing:c2_service_scan: 4215
- missing:c2_snapshot: 4215
- missing:c4_food: 4215
- missing:c4_parking: 4215
- missing:c4_prayer: 4215
- missing:c4_toilet: 4215
- missing:c5_category: 2337
- missing:c6_activity: 4215
- missing:identity: 2337
- missing:location: 4215
- possible_duplicate: 80
- unreviewed:c5_category: 1878
- unreviewed:identity: 1878

## Cakupan kandidat per provinsi

- (unknown): 602
- Aceh: 50
- Bali: 50
- Banten: 75
- Bengkulu: 50
- Central Papua: 8
- DKI Jakarta: 50
- Daerah Istimewa Yogyakarta: 222
- Daerah Khusus Ibukota Jakarta: 30
- East Nusa Tenggara: 211
- Gorontalo: 50
- Highland Papua: 2
- Jambi: 50
- Jawa Barat: 337
- Jawa Tengah: 50
- Jawa Timur: 275
- Kalimantan Barat: 50
- Kalimantan Selatan: 50
- Kalimantan Tengah: 50
- Kalimantan Timur: 50
- Kalimantan Utara: 50
- Kepulauan Bangka Belitung: 50
- Kepulauan Riau: 50
- Lampung: 50
- Maluku: 50
- Maluku Utara: 50
- Nanggroe Aceh Darussalam Province: 34
- North Maluku: 21
- North Sumatra: 30
- Nusa Tenggara Barat: 50
- Nusa Tenggara Timur: 50
- Papua: 50
- Papua Barat: 50
- Papua Barat Daya: 50
- Papua Pegunungan: 50
- Papua Selatan: 50
- Papua Tengah: 50
- Propinsi Bengkulu: 2
- Provinsi Bali: 40
- Provinsi Gorontalo: 8
- Provinsi Jambi: 27
- Provinsi Jawa Tengah: 152
- Provinsi Kalimantan Barat: 37
- Provinsi Kalimantan Selatan: 5
- Provinsi Kalimantan Tengah: 5
- Provinsi Kalimantan Timur: 13
- Provinsi Kepulauan Riau: 1
- Provinsi Lampung: 45
- Provinsi Maluku: 18
- Provinsi Papua: 7
- Provinsi Papua Barat: 15
- Provinsi Riau: 86
- Provinsi Sulawesi Barat: 1
- Provinsi Sulawesi Selatan: 17
- Provinsi Sumatera Barat: 9
- Riau: 50
- South Papua: 9
- Southwest Papua: 9
- Sulawesi Barat: 50
- Sulawesi Selatan: 50
- Sulawesi Tengah: 85
- Sulawesi Tenggara: 54
- Sulawesi Utara: 96
- Sumatera Barat: 50
- Sumatera Selatan: 68
- Sumatera Utara: 50
- West Nusa Tenggara: 59

## Cakupan kandidat per kategori mentah

- Bahari: 47
- Budaya: 406
- Cagar Alam: 2101
- Gunung: 399
- Pantai: 631
- Pusat Perbelanjaan: 167
- Taman Hiburan: 292
- Tempat Ibadah: 172

## Batasan

OSM tidak lengkap secara merata. Harga, fasilitas onsite, aktivitas, dan lokasi masuk membutuhkan bukti item-spesifik dengan hak pakai jelas. Kandidat tanpa bukti tetap pending.

Tidak ada snapshot layanan OSM pada run ini: C2 **belum dihitung** untuk kandidat mana pun; jangan membaca nilai kosong sebagai skor 0.

GeoNames mengidentifikasi landmark, bukan otomatis objek wisata yang terbuka, memiliki tiket, atau memenuhi fasilitas. Nama provinsi dan titik koordinatnya perlu konfirmasi independen.
