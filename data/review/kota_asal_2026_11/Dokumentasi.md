# Tambahan registry kota asal — November 2026

Tanggal akses: **19 November 2026**. Status: **terintegrasi** ke `data/kota_indonesia.csv` (339 menjadi 347 baris).

Audit website menemukan delapan kabupaten lokasi destinasi yang belum bisa dipilih sebagai kota asal.
Koordinat yang dipakai adalah titik pusat ibu kota kabupaten dari OpenStreetMap Nominatim, dibulatkan
empat desimal seperti baris registry lain. Koordinat Google tidak dipakai.

| Nama registry | Provinsi | Lat | Lon | Titik OSM yang dipilih | Snapshot |
| --- | --- | --- | --- | --- | --- |
| Sumedang | Jawa Barat | -6.8598 | 107.9207 | Alun-Alun Sumedang (leisure=park) | `sources/nominatim_sumedang.json` |
| Kudus | Jawa Tengah | -6.8078 | 110.8417 | place=city Kudus | `sources/nominatim_kudus.json` |
| Purworejo | Jawa Tengah | -7.7131 | 110.0091 | boundary administrative Purworejo | `sources/nominatim_purworejo.json` |
| Tegal | Jawa Tengah | -6.9829 | 109.1364 | place=town Slawi (ibu kota Kabupaten Tegal) | `sources/nominatim_tegal_slawi.json` |
| Lumajang | Jawa Timur | -8.1352 | 113.2244 | place=city Lumajang | `sources/nominatim_lumajang.json` |
| Ngawi | Jawa Timur | -7.4036 | 111.4446 | Alun-alun Merdeka Ngawi (leisure=park) | `sources/nominatim_ngawi_alun_alun.json` |
| Trenggalek | Jawa Timur | -8.0491 | 111.7091 | place=city Trenggalek | `sources/nominatim_trenggalek.json` |
| Tulungagung | Jawa Timur | -8.0661 | 111.9009 | boundary administrative Tulungagung | `sources/nominatim_tulungagung.json` |

Query Ngawi pertama (`sources/nominatim_ngawi.json`) hanya mengembalikan jalan tol dan jembatan, sehingga
diganti dengan alun-alun ibu kota. "Tegal" di registry berarti Kabupaten Tegal (lokasi Guci dan Waduk
Cacaban), bukan Kota Tegal.

Jalankan ulang pengambilan bukti dari root repo: `python data/review/kota_asal_2026_11/fetch_kota.py`
(snapshot yang sudah ada tidak diunduh ulang).

Lokasi © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright).
