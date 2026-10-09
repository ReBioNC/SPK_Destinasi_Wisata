# Keputusan budget tiket — 5 Oktober 2026

## Aturan aktif

- Alternatif A_i adalah satu destinasi, bukan paket beberapa tujuan.
- Budget maksimal tiket masuk satu destinasi per orang; minimal Rp0.
- Filter harga sumber <= budget dan provinsi tujuan. Destinasi gratis tetap sah.
- C1 cost = harga tiket asli, bukan harga capped K-Means atau total perjalanan.
- C3 cost = Haversine dalam km dari kota asal, bukan jarak jalan atau ongkos.
- C2/C4/C5/C6 benefit dan bobot AHP tetap mengikuti implementasi sebelumnya.
- TOPSIS dinormalisasi atas seluruh kandidat lolos, lalu ditampilkan Top10.
- Sisa alokasi tiket = budget - tiket. Tidak mengalokasikan sisa untuk belanja.
- Tarif adalah snapshot; transportasi, makan dan penginapan di luar cakupan.

## Integritas dan kompatibilitas

443 ID sumber dipertahankan; tidak ada perubahan data mentah, scaler, fitur
K-Means, label cluster atau bukti kurasi. Perubahan ini hanya aturan rekomendasi.
Versi fingerprint session `ticket-v1:` membatalkan hasil perhitungan biaya lama.
Field POST lama moda/hari/mode_antar diabaikan dan tidak disimpan lagi.
Modul biaya/routing serta model cache lama disimpan sebagai kode historis,
bukan dependensi perhitungan aktif. Tidak ada request OSRM untuk rekomendasi.

## Pengelompokan pengalaman

Rencana tiga kelompok pengalaman ada di IMPLEMENTATION_PLAN_ONTOLOGY.md.
Ini rencana pengembangan, bukan klaim ontology OWL/reasoner yang sudah aktif.
Tidak ada klasifikasi budget premium/hemat otomatis atau optimasi itinerary.

## Verifikasi

Tes budget memeriksa Rp0, tepat batas tiket, kota asal jauh, cost/benefit,
Top10, session lama, dan tidak adanya panggilan routing. Excel menghitung harga
dan jarak menggunakan formula; hasil dibandingkan dengan view Django asli.
Laporan UTS dan Excel aktif di outputs; file root historis tetap dipertahankan.
