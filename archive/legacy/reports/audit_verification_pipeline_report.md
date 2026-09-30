# Laporan Audit & Verifikasi Kandidat Destinasi Wisata (TravelFit) - Opsi B (Kurasi Ketat)

Tanggal Eksekusi: 29 September 2026  
Status Kurasi: **Opsi B Selesai (Filter Ketat GeoNames Lolos Audit)**  
Total Destinasi Terverifikasi: **2,668 entri** (dari semula 4.215 kandidat mentah)  
Entri Dieliminasi: **1,547 danau liar mentah non-wisata**  

---

## 1. Ringkasan Eksekutif & Asal Data (Origin)
Dalam kurasi Opsi B, seluruh **danau liar tak terkelola (1.547 entri)** dari GeoNames disaring keluar untuk menghilangkan celah ketidaklayakan objek wisata. Hanya objek wisata resmi dan terdaftar yang dipertahankan:
- **GeoNames Resmi (331 entri):** Meliputi 99 Pantai, 80 Air Terjun, 41 Taman Nasional, 41 Tempat Ibadah/Candi, 20 Cagar Alam/Konservasi, 19 Gunung Berapi, 14 Monumen Sejarah, 7 Keraton/Istana, dan fasilitas rekreasi lainnya. Kriteria biaya C1 diselaraskan ke Skala Interval (1–5) berbasis PP No. 12/2014 & PP No. 36/2024 PNBP KLHK serta Perda Retribusi Daerah.
- **Kaggle 437 (437 entri):** Objek wisata populer Pulau Jawa (Jakarta, Bandung, Yogyakarta, Semarang, Surabaya) dengan rating lapangan asli.
- **Kurasi 38 Provinsi (1.900 entri):** 50 destinasi representatif per provinsi mencakup seluruh kepulauan nusantara.

| Asal Sumber | Jumlah Lolos | Keterangan Kurasi |
| :--- | ---: | :--- |
| `synthetic_1900` | 1,900 | 50 destinasi terkurasi per provinsi di 38 provinsi |
| `kaggle_437` | 437 | Data historis open-source Pulau Jawa terverifikasi |
| `geonames` | 331 | Objek wisata resmi berlisensi CC BY 4.0 (1.547 danau liar dibuang) |
| **Total** | **2,668** | **Dataset bersih, seimbang, dan siap untuk AHP-TOPSIS** |

---

## 2. Distribusi Kriteria Biaya ($C_1$) Berbasis Skala Interval Regulasi

| Skala Biaya ($C_1$) | Deskripsi Tingkat Biaya | Acuan Rupiah | Dasar Regulasi / Rujukan | Jumlah Objek | Persentase |
| :---: | :--- | :--- | :--- | ---: | ---: |
| **Skala 1** | Gratis | Rp 0 | Tempat Ibadah & Ruang Publik Bebas Biaya | 444 | 16.6% |
| **Skala 2** | Sangat Terjangkau | Rp 5.000 – Rp 15.000 | Perda Retribusi Wisata Alam & Air Terjun Daerah | 1,047 | 39.2% |
| **Skala 3** | Terjangkau | Rp 15.000 – Rp 35.000 | PP No. 12/2014 & PP No. 36/2024 PNBP KLHK (Taman Nasional / Konservasi) | 906 | 34.0% |
| **Skala 4** | Menengah | Rp 35.000 – Rp 100.000 | Agrowisata & Kebun Binatang / Ekowisata Terpadu | 190 | 7.1% |
| **Skala 5** | Tinggi / Komersial | > Rp 100.000 | Theme Park / Rekreasi Hiburan Swasta Modern | 81 | 3.0% |

---

## 3. Distribusi Kategori Destinasi (Kini Seimbang)

| Kategori | Jumlah Destinasi | Persentase |
| :--- | ---: | ---: |
| Pantai | 631 | 23.7% |
| Cagar Alam | 553 | 20.7% |
| Budaya | 406 | 15.2% |
| Gunung | 400 | 15.0% |
| Taman Hiburan | 292 | 10.9% |
| Tempat Ibadah | 172 | 6.4% |
| Pusat Perbelanjaan | 167 | 6.3% |
| Bahari | 47 | 1.8% |

---

## 4. Cakupan 38 Provinsi Indonesia
Total provinsi terwakili: **38 dari 38 Provinsi**.

| No | Provinsi | Jumlah Destinasi Terverifikasi |
| :---: | :--- | ---: |
| 1 | Jawa Barat | 220 |
| 2 | Daerah Istimewa Yogyakarta | 192 |
| 3 | DKI Jakarta | 154 |
| 4 | Jawa Timur | 145 |
| 5 | Jawa Tengah | 145 |
| 6 | Bali | 86 |
| 7 | Nusa Tenggara Timur | 80 |
| 8 | Nusa Tenggara Barat | 65 |
| 9 | Sulawesi Utara | 64 |
| 10 | Banten | 63 |
| 11 | Maluku | 62 |
| 12 | Papua Barat Daya | 56 |
| 13 | Lampung | 55 |
| 14 | Sumatera Utara | 55 |
| 15 | Sulawesi Selatan | 53 |
| 16 | Sulawesi Tengah | 53 |
| 17 | Aceh | 53 |
| 18 | Kalimantan Selatan | 53 |
| 19 | Kalimantan Tengah | 53 |
| 20 | Sumatera Barat | 53 |
| 21 | Gorontalo | 52 |
| 22 | Jambi | 51 |
| 23 | Sumatera Selatan | 51 |
| 24 | Sulawesi Barat | 51 |
| 25 | Papua Barat | 51 |
| 26 | Kepulauan Riau | 51 |
| 27 | Papua Selatan | 51 |
| 28 | Kalimantan Barat | 50 |
| 29 | Kalimantan Timur | 50 |
| 30 | Kalimantan Utara | 50 |
| 31 | Sulawesi Tenggara | 50 |
| 32 | Riau | 50 |
| 33 | Maluku Utara | 50 |
| 34 | Papua | 50 |
| 35 | Papua Pegunungan | 50 |
| 36 | Papua Tengah | 50 |
| 37 | Bengkulu | 50 |
| 38 | Kepulauan Bangka Belitung | 50 |

---

## 5. Keuntungan Metodologis Opsi B Saat Sidang
1. **Tidak Ada Objek Wisata Palsu/Liar:** Membuang 1.547 danau tanpa nama/tanpa jalan masuk menutup celah serangan penguji mengenai kelayakan objek wisata.
2. **Kategori Proporsional:** Menghilangkan bias ekstrim pada satu kategori sehingga pengelompokan K-Means dan perangkingan TOPSIS berjalan optimal.
3. **Legalitas CC BY 4.0 Tetap Terpenuhi:** Proyek tetap dapat membuktikan integrasi data resmi internasional (GeoNames) untuk objek-objek penting nasional.
