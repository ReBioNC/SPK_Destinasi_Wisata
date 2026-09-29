# Rancangan kurasi dataset terbuka TravelFit (untuk ditinjau)

Tanggal: 29 September 2026

Status: rancangan, belum diimplementasikan

## Tujuan dan keputusan pengguna

TravelFit perlu mempertahankan cakupan destinasi yang besar tanpa menyajikan angka
simulasi sebagai fakta. Sebanyak 1.900 baris lama diaudit sebagai **kandidat**, bukan
dianggap berasal dari Sisparnas atau otomatis valid. Sebanyak 437 baris Kaggle tetap
menjadi kandidat. Destinasi baru dicari dari sumber yang terbuka, gratis, dan hak
pakai ulangnya jelas. Hanya baris dengan seluruh atribut yang dipakai sistem dan
bukti sumber yang memadai yang masuk hasil **siap pakai**. Jumlah 1.900 adalah
aspirasi, bukan kuota yang boleh dipenuhi dengan data buatan.

Pengguna menyetujui penggantian C2 dari rating menjadi **layanan pendukung sekitar
yang terpetakan**. Semua hasil pekerjaan ini dibuat pada berkas baru untuk ditinjau;
dataset, notebook, database, model, dan website yang ada tidak ditimpa pada tahap
ini. Perubahan sistem aktif baru dapat diputuskan setelah hasil kurasi ditinjau.

## Ruang lingkup tahap pertama

1. Buat inventaris 2.337 baris lama dan tandai asal masing-masing, atribut yang
   dihasilkan generator, kemungkinan nama pengisi, konflik lokasi, dan duplikat.
2. Kumpulkan kandidat destinasi tambahan dari sumber yang dapat dipakai ulang,
   terutama OpenStreetMap (OSM). Dataset pada data.go.id hanya dipakai bila hak
   penggunaan berkas spesifiknya telah jelas; label "Terbuka" saja tidak dianggap
   izin tanpa batas. Jangan mengambil ulang secara massal dari situs Sisparnas.
3. Bangun rekaman bukti **per atribut**: sumber/URL atau ID OSM, tanggal akses,
   nilai asli, metode transformasi, dan status pemeriksaan.
4. Hasilkan berkas kandidat dan berkas siap pakai secara terpisah. Baris yang belum
   lengkap tetap muncul di laporan audit tetapi tidak disamarkan sebagai siap pakai.
5. Hitung jumlah akhir berdasarkan data yang benar-benar lolos. Jangan memaksakan
   ambang 1.900 bila bukti tidak mendukung.

## Definisi kriteria dan aturan bukti

| Kriteria | Nilai untuk rancangan baru | Bukti minimum |
| --- | --- | --- |
| C1 harga tiket | Nominal tiket masuk domestik yang berlaku, rupiah, atau 0 bila eksplisit gratis | Halaman pengelola/instansi atau data terbuka yang menyebut destinasi, jenis tiket, nominal, dan tanggal; kosong tidak diubah menjadi 0 |
| C2 layanan sekitar terpetakan | Skor 0–4: satu poin untuk masing-masing kategori transportasi umum, layanan kesehatan, ATM/bank, dan penginapan yang terpetakan dalam radius garis lurus 2 km | Koordinat destinasi tervalidasi, snapshot OSM bertanggal, ID objek pendukung, dan aturan pencarian yang dapat dijalankan ulang |
| C3 jarak | Dihitung dari asal pengguna ke koordinat destinasi; bukan atribut tetap dari sumber | Koordinat destinasi yang lolos pemeriksaan lokasi dan metode jarak yang dinyatakan jelas |
| C4 fasilitas di lokasi | Empat indikator lama (toilet, parkir, warung, musala) dipertahankan sebagai indikasi berbasis bukti | Setiap nilai positif maupun negatif memiliki bukti eksplisit pada tingkat destinasi; ketiadaan tag bukan bukti fasilitas tidak ada |
| C5 kategori | Kategori wisata yang dipetakan ke taksonomi TravelFit | Tag/kategori sumber dan aturan pemetaan terdokumentasi; kasus ambigu ditinjau manual |
| C6 hobi/aktivitas | Tag aktivitas yang benar-benar disebut sumber atau dapat diturunkan dari atribut eksplisit | Bukti per aktivitas; jangan mengisi hanya dari templat deskripsi sintetis |

C2 mengukur **catatan OSM pada tanggal ekstraksi**, bukan menyimpulkan keadaan
lapangan lengkap. Nilai 0 berarti tidak ada objek dari empat kategori tersebut
yang *terpetakan* dalam radius yang dipakai, bukan memastikan tidak ada layanan.
Aturan ini dipakai sama untuk 437 kandidat Kaggle dan kandidat baru. Radius dan
empat kategori dicatat sebagai parameter agar uji sensitivitas dapat dilakukan.

Rating lama tetap disimpan hanya pada inventaris audit beserta asalnya; rating
simulasi tidak dipakai untuk C2, K-Means, atau peringkat. Pada tahap integrasi
lanjutan, bobot AHP harus ditinjau ulang karena makna C2 berubah, dan K-Means
harus dilatih ulang memakai fitur baru yang memang lolos verifikasi. Tidak cukup
hanya mengganti label tampilan.

## Status baris dan keluaran yang direncanakan

- `data/review/destinations_candidate_audit.csv`: seluruh kandidat lama dan baru,
  satu baris per identitas tempat, dengan status `verified`, `pending`, atau
  `rejected` dan alasan yang spesifik.
- `data/review/destinations_verified_open.csv`: hanya kandidat yang seluruh
  atribut sumber yang wajib telah lulus pemeriksaan. Kolom inti kompatibel
  dengan skema destinasi lama; kolom C2 baru dan provenansi tambahan dibuat
  eksplisit. Ini **bukan** pengganti otomatis file produksi.
- `data/review/destination_evidence.csv`: satu baris per destinasi, atribut,
  dan sumber. Memuat nilai, URL/ID objek, tanggal, hak penggunaan, serta catatan
  pemeriksaan.
- `data/review/audit_summary.md`: jumlah kandidat, jumlah lolos, jumlah gagal
  per alasan, cakupan provinsi/kategori, dan risiko bias/pemetaan.

Identitas deduplikasi memakai nama yang dinormalisasi bersama wilayah dan
kedekatan koordinat, kemudian pasangan ambigu diperiksa manual. ID lama tidak
dipakai sebagai bukti bahwa dua nama merujuk tempat berbeda. Tidak ada baris
yang dihapus dari berkas lama; penolakan hanya berlaku di keluaran baru.

## Alur dan batasan

Alur tahap pertama: inventaris sumber lama → cek izin sumber tambahan → ekstraksi
kandidat → normalisasi dan deduplikasi → kumpulkan bukti per atribut → hitung C2
dari OSM → validasi otomatis dan tinjauan kasus ambigu → ekspor audit dan subset
siap pakai. Ekstraksi OSM harus mengikuti atribusi dan ketentuan ODbL. Sumber
yang dapat dibaca gratis tetapi tidak jelas hak penerbitan ulangnya tidak
otomatis masuk dataset publik.

Harga tiket dan fasilitas di lokasi adalah hambatan utama untuk jumlah besar.
Apabila bukti tidak tersedia, status `pending` dipertahankan; nilai generator
tidak menjadi pengganti. Data siap pakai mungkin jauh lebih sedikit dari 1.900.
Risiko lain: OSM lebih lengkap di sebagian wilayah daripada wilayah lain,
sehingga C2 perlu dilaporkan sebagai proksi dan diuji distribusinya per provinsi.

## Validasi yang harus dilakukan saat implementasi

- Uji bahwa harga kosong tidak berubah menjadi 0, dan gratis harus memiliki
  sumber eksplisit.
- Uji bahwa rating dan koordinat yang dibuat generator tidak lolos sebagai nilai
  terverifikasi tanpa bukti pengganti.
- Uji deduplikasi lintas 437 baris, 1.900 baris, dan kandidat baru.
- Uji C2 pada radius batas, tidak ada amenitas terpetakan, lebih dari satu objek
  dalam kategori sama, dan objek lintas kategori.
- Uji bahwa setiap baris `verified` memiliki bukti untuk setiap atribut wajib,
  serta berkas asal tetap tidak berubah.
- Periksa hasil sampel manual lintas provinsi dan kategori; laporkan jumlah
  sebenarnya tanpa mengklaim semua destinasi benar di lapangan.

## Sumber kebijakan dan data yang harus dicek ulang saat eksekusi

- OSM: <https://www.openstreetmap.org/copyright> (atribusi dan ODbL).
- Portal Satu Data, Peta Sebaran Daya Tarik Wisata:
  <https://data.go.id/dataset/dataset/dtw> (terbuka pada katalog; verifikasi hak
  pakai ulang dan isi berkas sebelum mengambilnya).
- Ketentuan Sisparnas: <https://sisparnas.kemenpar.go.id/terms_and_conditions>
  (reproduksi/distribusi/karya turunan mensyaratkan izin tertulis menurut halaman
  yang tersedia saat rancangan ini dibuat).
- Ketentuan Places API: <https://developers.google.com/maps/documentation/places/web-service/policies>
  (konten Google tidak dijadikan basis dataset rating offline).
