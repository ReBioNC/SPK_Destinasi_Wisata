# Audit metode dan website TravelFit

Audit kode dan data lokal, 29 September 2026. Dokumen ini membedakan perhitungan
yang sudah berjalan dari validasi penelitian yang masih diperlukan.

## Temuan yang diperbaiki

| Area | Temuan | Perbaikan |
| --- | --- | --- |
| Provenansi data | 1.900/2.337 destinasi berasal dari generator dengan harga, rating, dan koordinat acak sekitar kota. | Website dan README memberi penanda data simulasi; hasil tidak diklaim sebagai fakta lapangan. |
| K-Means | Sebelumnya 0 dari 2.337 baris memiliki `cluster_label`. | Perintah `train_clusters` melatih pada 437 baris sumber Jawa, memilih k melalui silhouette, lalu mengisi label seluruh baris. |
| K-Means C4 | Fasilitas hanya terindikasi pada 82/437 baris Jawa; cluster dengan C4 terutama memisahkan metadata yang disebut/tidak disebut. | C4 dikeluarkan dari fitur K-Means. Fitur sekarang harga dan rating terstandardisasi serta kategori one-hot. |
| Rating C2 | Impor mencampur rata-rata rating pengguna dengan rating destinasi sehingga skala kedua sumber tidak sebanding. | C2 memakai kolom rating destinasi pada kedua sumber. Rating agregat tetap tersimpan sebagai data pendukung. |
| Fasilitas C4 | Website membagi skor dengan lima indikator, padahal `fas_penginapan` tidak terisi dari sumber mana pun. | Skor memakai empat indikator yang tersedia di kedua sumber: toilet, parkir, warung, musala. |
| Hobi C6 | Tanpa hobi pilihan, Jaccard kosong-kosong = 1 memberi keunggulan palsu kepada destinasi tanpa tag. | C6 dibuat konstan saat pengguna tidak memilih hobi, sehingga tidak memengaruhi TOPSIS. |
| TOPSIS | Persentase per kriteria dinormalisasi hanya di Top-10; kriteria konstan dapat ditampilkan sebagai keunggulan. | Rentang ideal dihitung dari seluruh kandidat dan kriteria konstan diberi tanda “Setara”. |
| SAW pembanding | Rumus `min/x` gagal saat tiket gratis atau jarak nol. | Kasus nilai minimum nol ditangani dengan normalisasi rentang; nilai konstan tidak membagi nol. |
| Form dan website | Opsi form dibaca berulang, urutan “harga termurah/jarak terdekat” terbalik, dan nama destinasi peta dimasukkan sebagai HTML. | Opsi dimuat satu kali, arah pengurutan diperbaiki, dan nama dirender sebagai teks. |

## Bukti eksekusi

- `python manage.py test`: 54 tes lulus.
- `python manage.py check`: tanpa isu.
- Basis data lokal: 2.337 destinasi dan 2.337 label cluster setelah impor dan pelatihan ulang.
- K-Means saat ini memilih `k=2`, silhouette `0,56452`, inertia `863,40678`; rinciannya ada di `reports/clustering/kmeans_evaluation.json`. Harga pelatihan dibatasi pada persentil ke-99 dan cluster minimum 5% dari 437 data pelatihan.
- GET halaman utama mengerjakan satu query database untuk pilihan form pada pemeriksaan lokal; POST rekomendasi AJAX dan halaman peta berhasil merespons.

## Hal yang belum dapat diklaim selesai

1. **Validitas destinasi dan keputusan.** Harga, rating, koordinat, serta fasilitas data simulasi belum diverifikasi. Pada 437 baris sumber, tidak ada penyebutan fasilitas belum tentu berarti tidak ada fasilitas. C4 pada ranking masih bersifat indikasi sementara.
2. **Jarak perjalanan.** C3 adalah jarak garis lurus Haversine. Untuk rute dan waktu tempuh dibutuhkan data jaringan jalan/transportasi serta koordinat destinasi yang benar.
3. **Evaluasi rekomendasi.** Tes membuktikan rumus AHP dan TOPSIS sesuai contoh spreadsheet, tetapi belum ada survei pengguna, penilaian relevansi destinasi, atau uji rank reversal lintas skenario. Spearman TOPSIS–SAW contoh 10 alternatif sekitar `0,297`; korelasi antar-metode tidak mengukur akurasi terhadap kebutuhan wisatawan.
4. **Generalitas cluster.** Centroid berasal dari lima wilayah kota di Jawa; label untuk 1.900 baris simulasi adalah ekstrapolasi eksploratif, bukan validasi segmentasi seluruh Indonesia.
5. **Kinerja produksi.** Beranda masih memuat Tailwind lewat CDN runtime dan banyak CSS/JS inline. Ini menjaga desain prototipe, tetapi untuk deployment sebaiknya CSS dibangun menjadi aset statis dan diuji secara visual/performa di browser target.

Urutan kerja riset berikutnya: verifikasi data destinasi, isi fasilitas aktual,
ukur relevansi lewat survei, lalu ulangi clustering dan evaluasi TOPSIS pada
skenario filter yang berbeda. Jalankan `python manage.py train_clusters` lagi
setiap kali `import_destinations` dijalankan.
