# Rencana pengelompokan pengalaman wisata TravelFit

Status 5 Oktober 2026: **rencana pengembangan**, belum modul ontology formal.
Baseline aktif: 443 destinasi (437 Kaggle + 6 kurasi Jawa), AHP–TOPSIS,
budget tiket satu destinasi per orang dan jarak garis lurus Haversine.

## 1. Tujuan dan batasan

Membantu pengguna membaca pilihan menurut jenis pengalaman, tanpa memaksakan
budget harus habis. Destinasi gratis tetap dapat direkomendasikan untuk budget
besar. Setiap alternatif A_i adalah satu destinasi. Tiga kelompok bukan tiga
paket perjalanan dan tidak menjamin rute beberapa tempat yang optimal.

C1 sudah memiliki dua peran yang sah: menyaring tiket <= budget dan menjadi
kriteria cost TOPSIS. C3 adalah cost jarak yang terpisah, bukan estimasi ongkos.
Rating, indikator fasilitas, kecocokan kategori dan hobi tetap benefit.
Harga adalah snapshot; tidak mengarang makanan, inap, parkir atau ongkos.

## 2. Data yang benar-benar tersedia

Kategori normalisasi: alam, bahari, budaya, hiburan, belanja, religi.
Cakupan aktif: DIY126, Jawa Barat124, Jakarta84, Jawa Tengah60, Jawa Timur47,
Banten2. Cakupan ini tidak mewakili seluruh destinasi setiap provinsi.

Fasilitas dihitung dari penyebutan deskripsi dengan koreksi konteks, bukan
kelengkapan yang sudah diverifikasi lapangan. Tag aktivitas adalah heuristik.
Rating Tahura menggunakan median model dengan penanda imputasi. Koordinat
Marina dipertahankan dengan peringatan. Metadata kualitas tetap ditampilkan.

## 3. Usulan tiga kelompok pengalaman

| Kelompok tampilan | Kandidat kategori awal | Batas interpretasi |
| --- | --- | --- |
| Rekreasi tematik | hiburan | Tidak otomatis premium; perlu review tempat budaya yang berkategori hiburan |
| Warisan budaya dan aktivitas kota | budaya, religi, belanja | Label bukan bukti kuliner tersedia atau biaya belanja diketahui |
| Alam dan bahari | alam, bahari | Bukan bukti akses, keselamatan, atau kelayakan aktivitas tertentu |

Mapping kategori adalah **aturan awal yang transparan**, bukan fakta baru.
Review override per destinasi harus menyimpan alasan, sumber, dan status.
Kelompok yang kosong ditampilkan kosong, tidak diisi destinasi yang melampaui
budget. Tidak ada ambang Rp150.000/Rp500.000 yang diklaim ilmiah.

## 4. Alur ranking yang menjaga keterbandingan

1. Validasi budget >=0, kota asal, provinsi tujuan dan preferensi.
2. Ambil seluruh destinasi pada wilayah yang tiketnya <= budget.
3. Bentuk C1 harga tiket, C2 rating model, C3 Haversine, C4 fasilitas/6,
   C5 kategori (1/0,5/0), C6 Jaccard hobi.
4. Hitung AHP dan TOPSIS **satu kali atas seluruh kandidat lolos**.
5. Jika pengelompokan diterapkan, pisahkan tampilan berdasarkan mapping setelah
   ranking. Semua kelompok memakai normalisasi dan ideal yang sama.
6. Tampilkan skor, ranking global, tiket, sisa alokasi tiket, jarak dan batasan.

TOPSIS yang dihitung sendiri-sendiri per kelompok menghasilkan skala relatif
berbeda; skornya tidak boleh dibandingkan sebagai ranking global.
Sisa alokasi tiket = budget - tiket. Tidak mengalokasikan otomatis untuk kuliner.

## 5. Ontology konseptual dan ontology formal

Model konseptual dapat menjelaskan kelas Destinasi, Kategori, Pengalaman,
Provinsi, Aktivitas dan BuktiSumber; hubungan beradaDi, memilikiKategori,
mendukungAktivitas dan didukungOlehSumber. Hubungan dari heuristik harus
dibedakan dari fakta sumber.

Kode if/else atau mapping kategori saja lebih tepat disebut klasifikasi berbasis
aturan. Klaim ontology formal baru layak setelah tersedia skema RDF/OWL,
definisi kelas/relasi, aturan inferensi, reasoner dan pengujian konsistensi.
Baseline website saat ini **tidak memiliki reasoner ontology formal**.

## 6. Tahapan implementasi lanjutan

| Tahap | Pekerjaan | Bukti pengujian |
| --- | --- | --- |
| Review mapping | Periksa 6 kategori dan override ambigu | Alasan dan status setiap override |
| Kelompok tampilan | Gunakan ranking global yang sudah dihitung | Skor/urutan tetap sama sebelum dan sesudah pengelompokan |
| Antarmuka | Tiga bagian atau tab tanpa mengubah arti budget | Empty state, keyboard, mobile, peringatan sumber |
| Ontology formal (opsional) | Definisi kelas/relasi dan aturan jika penelitian membutuhkan | Schema, reasoning dan kasus kontradiksi |

Implementasi paket multi-destinasi ditunda. Memerlukan tarif yang sebanding,
waktu kunjungan, rute jalan, durasi, jam buka, aturan total tiket dan metode
optimasi. Data saat ini tidak cukup untuk mengklaim optimasi itinerary.

## 7. Sumber aturan aktif

- README.md dan Dokumentasi.md untuk jumlah, metode dan keterbatasan data.
- docs/decisions/2026-10-05-ticket-budget.md untuk keputusan budget.
- recommender/views.py, recommender/spk/ahp.py, topsis.py dan geo.py untuk runtime.
- Formula Excel aktif dan laporan UTS di outputs untuk bukti perhitungan.
