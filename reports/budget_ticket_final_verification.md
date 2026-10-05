# Verifikasi budget tiket — 5 Oktober 2026

## Cakupan perubahan

Website aktif memakai budget maksimum tiket satu destinasi per orang. C1
menggunakan harga sumber tanpa cap p99, dan C3 menggunakan Haversine tanpa
faktor jarak jalan. Transportasi, makan, penginapan, dan durasi perjalanan
tidak menjadi input biaya. Desain yang ada dipertahankan.

## Hasil pemeriksaan

| Pemeriksaan | Hasil yang diamati |
|---|---|
| Seluruh tes Django | 188 tes, 43,335 detik, OK |
| Django system check | Tidak ada issue |
| Migration check | No changes detected |
| Destinasi aktif | 443 ID lengkap; seluruh field database identik dengan snapshot sebelum uji browser |
| Sumber dan arsip | Hash sumber mentah serta XLSX/DOCX historis di root tidak berubah |
| Notebook 01/02/03 | Sel kode tidak berubah; penjelasan budget tiket ditambahkan |
| Excel native | Tujuh skenario berbeda lulus, kemudian input baseline dipulihkan |
| Formula Excel tersimpan | 9.481 sel formula; tidak ditemukan sel error pada cached values |
| Ranking Excel–web | Top10, tiket, sisa tiket, skor tampilan, dan jarak tampilan sama |
| Presisi numerik Excel | Selisih Vi terbesar 1,1102230246251565e-16, di bawah toleransi 1e-12 |
| Contoh laporan–web | Matriks Banten sama; seluruh hasil TOPSIS dalam toleransi 1e-12 |
| Laporan | 31 halaman, 34 entri daftar isi; semua halaman diperiksa visual |
| Browser: Banten/Rp0 | Hasil kosong yang benar; rekomendasi lama dibersihkan |
| Browser: Jawa Barat/Rp0 | 37 kandidat gratis; tiket dan sisa alokasi Rp0 |
| Browser: Banten/Rp10.000 | Museum Multatuli pertama: tiket Rp2.000, sisa Rp8.000, Vi tampilan 0,8296 |
| Console browser | Tidak ada warning/error pada pemeriksaan terakhir |

Skenario Excel: empat profil AHP, budget Rp25.000, budget Rp0, serta kategori
belanja/religi tanpa hobi. Contoh dasar menggunakan Bandung–Jawa Barat,
budget Rp1.000.000, profil Hemat, kategori alam/budaya, hobi fotografi/edukasi.
Pemenangnya Caringin Tilu (ID266), Vi 0,9154032286741898.

Contoh Bab 3 laporan menggunakan Serang–Banten, budget Rp10.000, Hemat,
kategori alam/budaya, tanpa hobi. Input berbeda sengaja dicantumkan supaya
dua alternatif dapat dijelaskan lengkap. Vi Museum Multatuli pada laporan
0,8296323993478285; aplikasi menghasilkan 0,8296323993478286. Selisih digit
terakhir berasal dari floating-point/normalisasi bobot dan tidak mengubah
ranking atau angka tampilan. Ini bukan klaim bit-identik semua nilai raw.

## Berkas aktif dan bukti reproduksi

- `outputs/excel_spk_20261005/Perhitungan_AHP_TOPSIS_TravelFit.xlsx`
- `outputs/uts_travelfit/Laporan_UTS_TravelFit.docx`
- Excel: `_build/capture.py`, `_build/build.mjs`, `_build/verify_excel.ps1`,
  `_build/snapshot.json`, dan `_build/native_verification.json`.
- Audit sumber/laporan: Excel `_build/verify_sources_and_report.py`.
- Laporan: `_build/build_report.py`, `_build/render_word.ps1`,
  `_build/inspect_report.py`, dan `_build/evidence.json`.
- Screenshot: Excel `_build/browser-budget-ticket.jpg`.

Jangan menggunakan file historis di root sebagai perhitungan budget tiket.
Cache sesi hasil lama dibatalkan oleh versi `ticket-v1:`. Uji browser menulis
sesi Django pada SQLite, sehingga hash seluruh file database dapat berubah;
integritas destinasi diperiksa melalui isi seluruh row, bukan hash sesi.

## Batas interpretasi

Tarif masih snapshot, bukan hasil verifikasi harga transaksi terkini. C4
adalah indikator penyebutan deskripsi, bukan audit fasilitas lapangan.
Rating Tahura diimputasi 4,5 hanya pada kolom model. Koordinat Marina tetap
ditandai untuk review. Pengelompokan tiga pengalaman dalam rencana ontology
belum diimplementasikan; tidak ada klaim itinerary optimal atau reasoner.
