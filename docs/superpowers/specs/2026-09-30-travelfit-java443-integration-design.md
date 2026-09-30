# TravelFit Jawa: integrasi 443 destinasi, model, dan website

Tanggal: 30 September 2026. Branch kerja: `new`.

Status: rancangan tertulis disetujui pengguna pada 30 September 2026; rencana implementasi sedang disusun.
Dokumen ini belum menyatakan integrasi telah selesai.

## 1. Tujuan dan batasan

Menyelesaikan pembaruan TravelFit menjadi aplikasi rekomendasi destinasi pada
enam label provinsi Jawa, dengan sumber aktif **437 Kaggle + 6 tambahan = 443
destinasi**, preprocessing yang dapat ditelusuri, K-Means, AHP–TOPSIS, serta
desain website baru dan peta yang berfokus pada Jawa.

Keputusan yang sudah diberikan pengguna:

- Bekerja native di branch `new`, bukan membuat worktree atau task baru.
- Tidak kehilangan destinasi setelah preprocessing; ID 1–443 tetap lengkap.
- C4 tetap indikator fasilitas dari deskripsi, dengan koreksi konteks.
- Rating Tahura menggunakan imputasi median untuk perhitungan. Rating sumber tetap kosong; median snapshot sekarang 4,5.
- Pelabuhan Marina tetap dimasukkan, termasuk koordinat sumber yang bermasalah. Retensi tidak mengubah status validasi koordinat.
- Laporan DOCX tidak diubah.
- Commit lokal terpisah untuk setiap task yang selesai dan terverifikasi. Push tidak termasuk ruang lingkup.
- Pertanyaan berikutnya diberikan sebagai pilihan, bukan meminta pengguna merancang solusi teknis dari awal.

Tidak membuat survei fiktif, menambahkan destinasi baru, mengganti rating
imputasi menjadi rating Google Maps, mengarang fasilitas, atau mengklaim
seluruh data Kaggle sebagai data resmi pemerintah.

## 2. Pendekatan yang dipilih

**Satu pipeline Python bersama**, dipakai notebook dan proses impor/training,
dengan kontrak output ber-versi. Pengguna memilih pendekatan ini dibandingkan
pembacaan CSV hasil notebook saja.

Trade-off: kode pipeline perlu tersedia di folder proyek Colab, tetapi definisi
fitur, median, dan validasi ID tidak perlu diduplikasi. Pendekatan CSV saja
lebih sederhana untuk distribusi notebook mandiri, tetapi memerlukan
pemeriksaan versi dan sinkronisasi transformasi terpisah pada aplikasi.

Stack tetap Django, SQLite, pandas, NumPy, template HTML, CSS lokal, dan
JavaScript native. Tidak memigrasikan proyek ke Next.js/Flask atau memasang
backend/frontend lain.

## 3. Alur data dan kontrak pipeline

```text
CSV Kaggle 437 + CSV review 6 + bukti rating Google Maps
                   │
          pipeline Python bersama
                   │
       master 443 + fitur clustering + manifest
                   │
          import atomik database 443
                   │
         K-Means offline → label segmen
                   │
         input pengguna → AHP–TOPSIS
                   │
        hasil, kualitas data, dan peta Jawa
```

Modul pipeline berada di `recommender/data_pipeline.py`, tanpa ketergantungan
pada database atau request Django. Tanggung jawabnya: membaca sumber,
membersihkan format, membentuk fitur, memvalidasi retensi, dan menyiapkan
metadata transformasi. Proses impor menyimpan hasilnya ke database; training
memakai pembentuk fitur yang sama, bukan mendefinisikan scaler baru sendiri.

Input aktif:

- `data/raw/tourism_with_id.csv`, ID 1–437.
- `data/review/gabungan_jawa/destinasi_jawa_review.csv`, ID 438–443.
- `data/review/gabungan_jawa/google_maps_rating_review.json`, bukti lima rating cocok dan satu kandidat identitas yang belum pasti.
- `data/raw/tourism_rating.csv`, interaksi pengguna Kaggle untuk agregat deskriptif, bukan pengganti rating destinasi atau survei baru.

Raw CSV dan bukti asal tidak ditimpa. Kolom Kaggle pada sumber tetap sama.
Metadata turunan ditambahkan pada master, bukan disamarkan sebagai field sumber.

Output aktif mempertahankan nama dataset baru:

- `data/processed/destinations_clean_java443.csv`.
- `data/processed/destinations_kmeans_features_java443.csv`.
- `reports/preprocessing/preprocessing_java443_summary.json`.
- Manifest pipeline dengan versi, hash sumber, daftar ID, parameter transformasi, serta metadata imputasi.

Notebook utama memanggil modul ini. Pada Colab, modul Python dan folder sumber
harus tersedia di `Drive Saya/TravelFit`; jika ada yang tidak tersedia,
notebook berhenti dengan pesan jelas, bukan melanjutkan dengan 437 saja.
Tidak ada pengunduhan kode Python remote yang langsung dieksekusi.

Semua tahap memeriksa 443 baris, 443 ID unik, dan kesetaraan himpunan ID 1–443.
Duplikat/ID hilang menghentikan ekspor/impor. Nilai kosong atau masalah lokasi
dicatat, bukan dijadikan alasan menghapus destinasi. Ketidaksesuaian versi
manifest/transformasi menghentikan training sampai preprocessing diperbarui.

## 4. Rating dan kualitas lokasi

| Field | Makna |
| --- | --- |
| `rating` / `c2_rating` | Rating teramati; Tahura tetap kosong |
| `c2_rating_for_model` | Nilai untuk perhitungan; Tahura memakai median |
| `rating_imputed` | Penanda eksplisit bahwa nilai perhitungan bukan hasil pengamatan |
| `rating_status`, URL, tanggal | Asal dan batasan bukti rating |
| `coordinate_review_required`, catatan | Konflik lokasi yang diketahui |
| `data_quality_issues` | Masalah sumber tanpa penghapusan baris |

Median berasal dari seluruh rating destinasi valid pada snapshot aktif,
sebelum imputasi, saat ini 442 pengamatan dan median 4,5. Nilai yang sama
disimpan pada manifest dan digunakan K-Means/TOPSIS; tidak dihitung ulang
berdasarkan provinsi atau kandidat hasil filter. Imputasi hanya diizinkan
untuk Tahura ID 438 jika rating sumbernya kosong dan nama cocok. Rating valid
yang kemudian tersedia menggantikan kebutuhan imputasi, bukan menimpa bukti
lama secara diam-diam.

Pelabuhan Marina ID 9 dipertahankan dengan lintang 1,07888 dan bujur
103,931398. Label sumber Jakarta dan konflik lokasinya tetap dicatat. Titik
tidak dipindahkan ke Jakarta dengan koordinat tebakan. Aplikasi tidak
menyebut jarak/biaya yang dihitung dari titik tersebut sebagai lokasi
terverifikasi; hasilnya mendapat peringatan yang terlihat.

Pemetaan kota ke provinsi mengikuti label sumber dan pemetaan yang telah ada,
dengan alias provinsi diseragamkan. Ini bukan klaim audit batas administrasi
untuk semua 437 baris. Koreksi data yang belum memiliki bukti tidak dilakukan
hanya untuk memenuhi peta.

## 5. C4 dan fitur clustering

C4 master, model database, dan TOPSIS memakai definisi yang sama:
jumlah kelompok penyebutan yang diterima dibagi enam. Kelompoknya toilet,
parkir, tempat makan, tempat ibadah, aksesibilitas, dan pusat informasi.
Aturan koreksi konteks yang sudah diuji dipindahkan ke modul bersama.
Deskripsi kosong dibedakan dari deskripsi tanpa kecocokan. Nilai 0 bukan
bukti bahwa fasilitas tidak tersedia di lapangan.

**C4 dipertahankan pada SPK, tetapi tidak menjadi fitur jarak K-Means.**
Pada snapshot saat ini hanya 69/443 deskripsi mempunyai indikator positif;
memasukkan C4 berisiko mengelompokkan kelengkapan metadata, bukan fasilitas
aktual. Pengecualian ini mengikuti alasan pada trainer lama dan dilaporkan.

Fitur clustering sebenarnya:

- Harga tiket dibatasi pada persentil 99 untuk transformasi model, kemudian Z-score.
- `c2_rating_for_model`, kemudian Z-score.
- One-hot kategori wisata.

Harga asli tidak diubah oleh pembatasan persentil. Metadata seperti ID,
imputasi, provinsi, dan kualitas koordinat tidak dihitung sebagai fitur jarak.
CSV fitur clustering diperbarui agar tepat menggambarkan fitur trainer;
master tetap memuat C4 untuk SPK. Jumlah baris kedua output tetap 443.

## 6. Database dan impor

Tambahkan identitas ID sumber yang unik, rating sumber nullable, nilai rating
perhitungan, provenance, catatan kualitas, deskripsi, serta dua indikator
fasilitas yang sebelumnya belum ada. Nama field akhir disesuaikan dengan
pola model Django, tetapi pemisahan rating sumber/perhitungan wajib terjaga.

`import_destinations` tidak lagi membaca XLSX sintetis 1900 atau CSV lama
437 sebagai sumber utama. Import memvalidasi master/manifest dari pipeline
dan upsert berdasarkan ID sumber. Impor ulang idempoten.

Sebelum mengganti isi database lokal, simpan backup SQLite yang dapat
dipulihkan di folder arsip workspace. `--dry-run` menampilkan jumlah input,
upsert, dan record lama yang akan dikeluarkan tanpa menulis database.
Penggantian berlangsung dalam transaksi: hanya 443 ID aktif baru yang
tersisa; kegagalan validasi tidak meninggalkan impor parsial. Record lama
di luar himpunan sumber dihapus setelah backup dan validasi, sesuai
permintaan cleanup. Cache opsi form/hasil lama diinvalidasi.

Backup database tidak ditambahkan ke Git karena dapat memuat sesi pengguna.
Lokasi pemulihan dilaporkan saat penggantian. Tidak menghapus file DOCX,
sumber aktif, bukti kurasi, atau perubahan lain milik pengguna.

## 7. K-Means dan evaluasi

Trainer mempelajari centroid dari **seluruh 443 destinasi**, bukan 437 lalu
hanya menempelkan label pada tambahan. Urutan data mengikuti ID sumber.
Gunakan algoritma NumPy yang telah ada: inisialisasi k-means++, seed 42,
10 starts, evaluasi k 2–6 dengan inertia, silhouette, dan ukuran cluster.
Aturan pemilihan cluster kecil tetap dijelaskan pada laporan.

Laporan menyimpan versi/hash pipeline, fitur, scaler, pembatasan harga,
median, ID imputasi, jumlah 443 training/assigned, centroid, kandidat k,
statistik cluster, dan keterbatasan sumber. Tidak menyebut silhouette
sebagai akurasi rekomendasi atau menjanjikan nilai tertentu sebelum run.
Label segmen deskriptif dan relatif terhadap snapshot, bukan kategori
kebenaran, dan tidak menjadi filter keras untuk menghilangkan kandidat.

## 8. AHP–TOPSIS dan budget

Tetap gunakan enam kriteria, profil AHP yang ada, dan sensitivitas bobot.
CR diuji < 0,1; profil disusun pengembang, belum hasil survei pengguna.

- C1 runtime: estimasi total perjalanan yang sudah ada.
- C2: nilai perhitungan rating, termasuk imputasi yang ditandai.
- C3: jarak dari layanan rute/fallback yang sudah ada.
- C4: indikator deskripsi enam kelompok yang sama dengan master.
- C5: kesesuaian kategori utama/sekunder.
- C6: Jaccard hobi dengan tag aktivitas heuristik.

Harga tiket pada preprocessing/clustering berbeda peran dengan C1 total
perjalanan pada runtime; perbedaan ini harus dijelaskan, bukan disamakan.
Budget tidak diam-diam diganti menjadi batas harga tiket saja. Transport,
makan, dan inap tetap **estimasi** dengan parameter terbuka; biaya tiket
diberi provenance tersendiri. Batasan hari biasa/libur Artha Tirta tetap
terlihat. Jangan melabeli seluruh rincian budget sebagai tarif resmi.

Kategori tujuan dibatasi enam provinsi Jawa. Pilihan kota asal yang sudah
ada tetap dipertahankan: lingkup Jawa adalah destinasi, bukan larangan
berangkat dari luar Jawa. Perhitungan antar-pulau yang masih dipakai oleh
kota asal tersebut tidak dihapus sebagai kode usang.

TOPSIS memvalidasi nilai finite, dimensi, bobot nonnegatif, dan jumlah bobot
positif. Uji benefit/cost, nilai sama, nol, satu kandidat, imputasi, dan
sensitivitas. SAW/Spearman hanya pembanding kesepakatan ranking jika
dilaporkan, bukan bukti pilihan wisatawan benar. Tidak membuat hasil survei.

## 9. Website dan peta

Gunakan **UI-UX Pro Max pada tahap implementasi desain** setelah rancangan
dan rencana implementasi disetujui. Tetap HTML/template Django, CSS lokal,
dan JavaScript native; layout dirombak tanpa mengganti stack.

Arah visual: latar krem hangat, aksen teal, teks gelap, hierarki editorial,
form yang lebih ringkas, serta kartu rekomendasi yang memisahkan biaya,
skor, dan kualitas sumber. Identitas TravelFit dipertahankan. CSS/JS besar
yang sekarang terduplikasi inline dipindahkan ke aset lokal dan komponen
template bersama; tidak bergantung pada compiler Tailwind CDN saat runtime.

Alur utama: beranda → input preferensi → Top-10 dan alasan C1–C6 → eksplorasi
peta; halaman metode menjelaskan CRISP-DM dan bukti data. Validasi form dan
hasil tanpa JavaScript tetap berfungsi. AJAX memberi status loading,
error, dan hasil tanpa menghilangkan CSRF atau navigasi keyboard.

Peta hanya memuat enam provinsi Jawa menggunakan geometri SVG yang telah
ada, dengan framing/viewBox berfokus Jawa dan wilayah terkait pada sumber.
Tidak menampilkan overview 38 provinsi atau memerlukan token peta berbayar.
SVG Java dan logic interaksinya dipakai bersama di beranda dan halaman peta.

Seluruh 443 destinasi tetap tersedia pada data/list; filter pengguna bisa
menampilkan subset tanpa dianggap kehilangan data. Koordinat di luar frame,
termasuk Marina, tidak mengubah zoom menjadi seluruh Indonesia dan tidak
dipaksa menjadi titik Jakarta. Daftar/status peta menyebut titik di luar
tampilan atau perlu review. Titik koordinat sumber bukan jaminan loket masuk.

UI wajib menampilkan label imputasi Tahura, catatan lokasi Marina, sumber
Kaggle/kurasi, dan batasan C4. Informasi tersebut tidak hanya disembunyikan
di tooltip. Jumlah data dan kandidat berasal dari database, bukan angka
hardcode yang tidak sesuai filter. Klaim simulasi 1900/2337 aktif dihapus.

Uji desktop/mobile, focus keyboard, label input, kontras, reduced motion,
empty/error state, pemilihan provinsi, perubahan bobot, dan konsol browser.

## 10. Cleanup dan dokumentasi

Setelah pengganti terbukti bekerja, inventarisasi file/dataset/notebook lama
beserta seluruh referensinya. Hapus atau pindahkan ke arsip yang jelas hanya
artefak yang tidak lagi diperlukan; tidak memakai recursive delete workspace.
Notebook 02/03 dan XLSX 1900/2337 tidak menjadi workflow aktif. Sesuaikan tes
yang memang merepresentasikan kontrak impor 1900/38 provinsi lama; jangan
mengabaikan tes gagal yang masih relevan. Bukti review enam tambahan dan
catatan audit tetap dipertahankan. Riwayat Git/arsip menyediakan pemulihan.

README dan dokumentasi penggunaan diperbarui: cakupan Jawa, input Drive,
perintah preprocessing/impor/training, jumlah 443, fitur clustering nyata,
definisi C4, imputasi, estimasi budget, dan keterbatasan koordinat.
File DOCX dan isinya tetap tidak disentuh. Spreadsheet perhitungan yang
masih dipakai sebagai referensi tidak dihapus tanpa audit keterkaitannya.

## 11. Task dan kriteria selesai

| ID | Outcome | Bukti penerimaan |
| --- | --- | --- |
| T1 | Preprocessing/keputusan data yang sudah dikerjakan | Commit `c41cf70`, `6be2aaf`, `bbadc48`; saat itu 131 tes lolos |
| T2 | Pipeline bersama dan database utama Jawa | Notebook/importer berbagi modul; 443 ID utuh; rating asli/perhitungan terpisah; impor idempoten dan rollback teruji |
| T3 | Training dan SPK konsisten | 443 ikut training; laporan nyata; C4 enam kelompok; C2 imputasi konsisten; uji AHP/TOPSIS dan integrasi lolos |
| T4 | Website baru dan peta Jawa | UI-UX Pro Max digunakan; enam provinsi; metadata kualitas terlihat; alur desktop/mobile diverifikasi pada browser |
| T5 | Cleanup dan dokumentasi | Dependensi legacy dihapus dari workflow; sumber/bukti/DOCX aman; README sesuai kondisi; seluruh suite dan smoke test akhir lolos |

Selesai berarti aplikasi memakai 443 data baru, bukan hanya notebook
menghasilkan CSV. Setiap outcome di-commit terpisah setelah verifikasi.
Penggantian data lama dilaporkan beserta cara pemulihan. Tidak membuat PR,
push, deployment publik, atau modifikasi DOCX tanpa permintaan tambahan.

## 12. Review rancangan

Review internal: tidak ada bagian placeholder; jumlah data, pemisahan rating,
definisi C4, fitur clustering, lingkup map, biaya estimasi, retensi Marina,
dan kebijakan cleanup konsisten. Pengguna menyetujui **dokumen ini** dengan
pesan “Setuju”. Persetujuan tersebut mengizinkan penyusunan rencana
implementasi tertulis; belum menyatakan implementasi telah selesai.
