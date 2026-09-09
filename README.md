# TravelFit — Sistem Pendukung Keputusan Rekomendasi Destinasi Wisata Multi-Kriteria

Aplikasi web berbasis Sistem Pendukung Keputusan (SPK) yang membantu wisatawan menemukan destinasi wisata terbaik di Indonesia berdasarkan **banyak variabel penentu**, bukan budget semata. Budget hanyalah satu dari enam kriteria yang dipertimbangkan — berdampingan dengan rating pengunjung, jarak/waktu tempuh, kelengkapan fasilitas, kesesuaian kategori minat, dan kesesuaian hobi. Pengembangan proses data mining mengikuti kerangka **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*), menggunakan **K-Means Clustering** pada tahap pemodelan, lalu menggabungkannya dengan metode **Multi-Criteria Decision Making/MCDM** (AHP dan TOPSIS). Kombinasi ini menghasilkan rekomendasi destinasi yang terukur, transparan, dan dapat dipertanggungjawabkan secara matematis — bukan sekadar rekomendasi acak berdasarkan popularitas di media sosial, dan bukan sekadar daftar destinasi termurah.

User memasukkan profil preferensinya secara lengkap: budget maksimal, kota/wilayah tujuan, kategori wisata yang diminati (alam, budaya, kuliner, hiburan, religi), dan hobi terkait wisata (hiking, fotografi, kuliner lokal, dsb). Sistem kemudian memproses data ratusan destinasi wisata dengan menimbang **seluruh variabel tersebut secara bersamaan** untuk menghasilkan daftar rekomendasi peringkat teratas lengkap dengan skor kesesuaian dan alasan di balik setiap rekomendasi.

## Variabel Penentu Keputusan

Keputusan rekomendasi TravelFit ditentukan oleh enam kriteria (C1–C6) yang dihitung bersama, bukan oleh satu variabel tunggal:

- **Budget** berperan sebagai *batas kelayakan* (destinasi di luar budget maksimal tersaring sejak awal) sekaligus sebagai *salah satu* kriteria cost (C1) di tahap perankingan — bukan satu-satunya penentu.
- **Kualitas destinasi** diwakili rating pengunjung (C2) dan kelengkapan fasilitas (C4).
- **Aksesibilitas** diwakili jarak/waktu tempuh dari kota asal user (C3).
- **Kecocokan personal** diwakili kesesuaian kategori (C5) dan kesesuaian hobi (C6).

Besarnya pengaruh tiap variabel tidak fixed: bobotnya dihitung dengan AHP dan dapat diubah user melalui sensitivity analysis. Artinya user yang memprioritaskan pengalaman (rating, hobi) bisa mendapatkan hasil berbeda dari user yang memprioritaskan hemat — walau budgetnya sama.

## Identitas Kelompok

| Nama | NIM | Peran |
|---|---|---|
| Kristofer Ryan Giggs | 412024005 | Ketua |
| Cristian Dion | 412024006 | Anggota |
| Reynard Liu | 412025022 | Anggota |
| Justin Augusto Liusri | 412025029 | Anggota |

## Latar Belakang Masalah

Wisatawan, khususnya kalangan mahasiswa dan backpacker, sering kesulitan memilih destinasi wisata karena informasi harga tiket, rating, jarak, dan fasilitas tersebar di berbagai platform (Google Maps, Instagram, TripAdvisor) dan sulit dibandingkan secara objektif. Banyak orang akhirnya memilih destinasi hanya berdasarkan tren media sosial atau patokan harga termurah, tanpa mempertimbangkan trade-off antar banyak faktor: destinasi murah bisa jadi jauh dan fasilitas minim, destinasi populer bisa jadi tidak cocok dengan hobi. Dibutuhkan alat bantu yang menimbang seluruh variabel tersebut secara seimbang dan transparan.

## Fungsi & Manfaat Aplikasi

**Fungsi utama:**
- Memfilter dan mengelompokkan ratusan destinasi wisata berdasarkan karakteristik harga, rating, dan kategori
- Menghitung skor kesesuaian tiap destinasi terhadap preferensi user secara objektif dan terukur
- Menampilkan ranking rekomendasi destinasi beserta penjelasan alasan (explainability) di balik setiap rekomendasi
- Menyediakan simulasi sensitivitas (sensitivity analysis) — user dapat mengubah bobot prioritas kriteria dan melihat perubahan hasil rekomendasi secara real-time
- Menyediakan peta interaktif Indonesia (38 provinsi, 7 gugus pulau) sebagai antarmuka eksplorasi destinasi (`index.html`)

**Manfaat:**
- **Bagi wisatawan:** menghemat waktu riset, keputusan liburan lebih terarah sesuai keseluruhan preferensi (budget, kualitas, akses, dan kecocokan minat), tidak perlu membandingkan puluhan sumber informasi secara manual
- **Bagi pelaku UMKM/agen travel kecil:** dapat digunakan sebagai alat bantu menyusun paket wisata yang sesuai profil dan prioritas klien, bukan sekadar menyesuaikan harga
- **Bagi pengembangan pariwisata:** data hasil clustering dapat memberi gambaran destinasi mana yang under-explored namun punya value tinggi, berpotensi mendukung pemerataan kunjungan wisata

## Metode yang Digunakan

| Tahap | Metode | Fungsi |
|---|---|---|
| Kerangka Data Mining | CRISP-DM | Mengarahkan proses data mining dari pemahaman masalah sampai penerapan dan evaluasi sistem |
| Data Mining | K-Means Clustering | Mengelompokkan destinasi ke dalam segmen berdasarkan karakteristik (harga, rating, kategori) |
| SPK — Pembobotan Kriteria | AHP (Analytic Hierarchy Process) | Menentukan bobot kepentingan tiap kriteria secara terstruktur dan teruji konsistensinya |
| SPK — Perankingan Alternatif | TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) | Meranking destinasi berdasarkan kedekatannya terhadap solusi ideal |

### Alasan Pemilihan Metode

**CRISP-DM** dipilih sebagai kerangka kerja karena menyediakan tahapan pengembangan data mining yang sistematis, iteratif, dan mudah didokumentasikan. Kerangka ini memastikan proses tidak hanya berfokus pada pembuatan model, tetapi juga dimulai dari pemahaman kebutuhan wisatawan, pemeriksaan kualitas data, evaluasi hasil, hingga penerapan model ke dalam aplikasi.

**K-Means** dipilih karena data destinasi wisata tidak memiliki label "benar/salah" (bersifat unsupervised) — tujuannya murni mengelompokkan destinasi yang mirip karakteristiknya, sehingga proses filtering sebelum tahap SPK menjadi lebih efisien dan terstruktur dibanding membandingkan seluruh destinasi satu per satu. K-Means juga ringan secara komputasi dan mudah di-deploy ulang secara real-time dibanding metode clustering lain seperti Hierarchical Clustering.

**AHP** dipilih untuk menentukan bobot kriteria karena metode ini memungkinkan perbandingan berpasangan antar kriteria secara terstruktur dan dilengkapi mekanisme uji konsistensi (Consistency Ratio), sehingga bobot yang dihasilkan dapat dipertanggungjawabkan secara metodologis, bukan ditentukan secara subjektif sepihak.

**TOPSIS** dipilih untuk tahap perankingan karena mempertimbangkan jarak alternatif terhadap solusi ideal positif *dan* negatif sekaligus, sehingga hasilnya lebih robust terhadap data outlier (misalnya destinasi murah tapi rating sangat rendah) dibanding metode SAW (Simple Additive Weighting) yang hanya menjumlahkan skor tertimbang. TOPSIS juga secara konsep lebih mudah dijelaskan ke pengguna awam ("destinasi ini paling dekat dengan kondisi ideal Anda"), mendukung aspek *explainability* aplikasi.

## Penerapan CRISP-DM

CRISP-DM digunakan sebagai kerangka utama pengembangan data mining. Prosesnya bersifat iteratif, sehingga hasil evaluasi pada suatu tahap dapat mengarahkan pengembang kembali ke tahap sebelumnya untuk memperbaiki data, fitur, atau model.

### 1. Business Understanding

Tahap ini berfokus pada pemahaman masalah, kebutuhan pengguna, dan tujuan aplikasi.

- **Permasalahan bisnis:** wisatawan kesulitan membandingkan banyak destinasi secara objektif karena informasi harga, rating, jarak, fasilitas, kategori, dan aktivitas tersebar di berbagai sumber.
- **Tujuan bisnis:** membantu pengguna menemukan destinasi yang paling sesuai dengan budget, lokasi, minat, dan hobinya melalui rekomendasi yang transparan.
- **Tujuan data mining:** menemukan kelompok destinasi dengan karakteristik serupa agar kandidat rekomendasi lebih terstruktur sebelum diproses oleh AHP dan TOPSIS.
- **Target pengguna:** wisatawan umum, mahasiswa, backpacker, serta pelaku UMKM atau agen perjalanan skala kecil.
- **Kriteria keberhasilan:** sistem mampu menghasilkan rekomendasi relevan, menampilkan alasan rekomendasi, memberikan hasil perhitungan yang konsisten, serta merespons perubahan preferensi pengguna.
- **Batasan:** kualitas rekomendasi bergantung pada kelengkapan dan kebaruan data destinasi; harga, rating, fasilitas, dan waktu tempuh dapat berubah.

**Output tahap:** rumusan masalah, tujuan sistem, kebutuhan pengguna, batasan proyek, dan indikator keberhasilan.

### 2. Data Understanding

Tahap ini digunakan untuk mengumpulkan, mengenali, dan memeriksa data destinasi yang akan digunakan.

- Mengumpulkan data destinasi dari sumber yang relevan dan dapat dipertanggungjawabkan.
- Mengidentifikasi atribut utama: nama destinasi, provinsi/kota, koordinat, harga tiket, rating, jarak atau waktu tempuh, fasilitas, kategori wisata, dan tag aktivitas/hobi.
- Memeriksa tipe data, jumlah data, rentang nilai, distribusi, dan hubungan antaratribut.
- Mengidentifikasi data kosong, data ganda, format yang tidak konsisten, nilai ekstrem, serta kemungkinan data yang sudah tidak terbaru.
- Melakukan eksplorasi awal untuk mengetahui pola harga, rating, persebaran wilayah, kategori wisata, dan karakteristik calon cluster.

**Output tahap:** deskripsi dataset, kamus data, statistik deskriptif, visualisasi eksploratif, dan laporan kualitas data.

### 3. Data Preparation

Tahap ini menyiapkan data agar dapat digunakan oleh K-Means, AHP, dan TOPSIS.

- Menghapus data duplikat dan menangani nilai kosong.
- Menyeragamkan format harga, rating, koordinat, kategori, fasilitas, dan tag hobi.
- Mengubah atribut kategorikal menjadi representasi numerik yang sesuai, misalnya *one-hot encoding* untuk kategori wisata.
- Mengubah fasilitas menjadi skor kelengkapan berdasarkan jumlah atau bobot fasilitas yang tersedia.
- Menghitung jarak atau estimasi waktu tempuh dari lokasi asal pengguna ke destinasi.
- Menghitung kesesuaian hobi menggunakan **Jaccard Similarity** antara hobi pengguna dan tag aktivitas destinasi.
- Melakukan normalisasi atau standardisasi fitur numerik sebelum K-Means agar fitur berskala besar, seperti harga dan jarak, tidak mendominasi pembentukan cluster.
- Memilih fitur clustering yang relevan, misalnya harga, rating, fasilitas, serta representasi kategori. Jarak dari pengguna dan skor kecocokan personal dihitung saat rekomendasi karena nilainya bergantung pada setiap pengguna.

**Output tahap:** dataset bersih dan dataset transformasi yang siap digunakan untuk pemodelan serta perankingan.

### 4. Modeling

Tahap pemodelan terdiri atas clustering destinasi dan proses SPK.

1. Menentukan kandidat jumlah cluster (`k`) dan nilai awal centroid.
2. Menjalankan **K-Means Clustering** pada data destinasi yang telah dinormalisasi.
3. Membandingkan beberapa nilai `k` menggunakan metode seperti *Elbow Method* dan *Silhouette Score*.
4. Menginterpretasikan setiap cluster, misalnya destinasi ekonomis, destinasi premium berfasilitas lengkap, atau destinasi dengan rating tinggi.
5. Memilih destinasi dari cluster yang relevan dengan profil pengguna sebagai kandidat alternatif.
6. Menggunakan **AHP** untuk menghitung bobot C1–C6 dan memastikan nilai *Consistency Ratio* kurang dari 0,1.
7. Menggunakan **TOPSIS** untuk menghitung nilai preferensi dan menentukan peringkat akhir destinasi.

**Output tahap:** model K-Means, profil setiap cluster, bobot kriteria AHP, nilai preferensi TOPSIS, dan daftar rekomendasi terurut.

### 5. Evaluation

Tahap ini memastikan model dan hasil rekomendasi telah memenuhi tujuan sistem.

- Mengevaluasi kualitas cluster menggunakan *Silhouette Score*, nilai *inertia/SSE*, ukuran setiap cluster, dan kemudahan interpretasi cluster.
- Memastikan cluster tidak hanya baik secara matematis, tetapi juga masuk akal dalam konteks destinasi wisata.
- Menguji konsistensi bobot AHP dengan syarat `CR < 0,1`.
- Memeriksa hasil TOPSIS secara manual menggunakan beberapa skenario profil pengguna.
- Melakukan *sensitivity analysis* untuk melihat stabilitas peringkat saat bobot kriteria berubah.
- Memvalidasi apakah rekomendasi memenuhi filter wajib seperti budget, wilayah, dan kategori pilihan pengguna.
- Jika hasil belum memenuhi kriteria keberhasilan, proses dapat kembali ke tahap Data Understanding, Data Preparation, atau Modeling.

**Output tahap:** laporan evaluasi cluster, hasil uji konsistensi AHP, validasi ranking TOPSIS, hasil sensitivity analysis, dan keputusan kelayakan model.

### 6. Deployment

Tahap ini menerapkan hasil data mining dan SPK ke dalam aplikasi TravelFit.

- Menyimpan hasil clustering dan profil cluster agar dapat digunakan aplikasi.
- Mengintegrasikan input preferensi pengguna, proses filter, AHP, dan TOPSIS ke antarmuka web.
- Menampilkan rekomendasi Top-5 atau Top-10 beserta skor dan alasan pada setiap kriteria.
- Menyediakan peta interaktif dan fitur sensitivity analysis untuk mengeksplorasi hasil.
- Menyusun dokumentasi penggunaan, struktur data, metode perhitungan, dan keterbatasan sistem.
- Menetapkan proses pemutakhiran dataset, pelatihan ulang K-Means, dan evaluasi berkala ketika terdapat data destinasi baru.

**Output tahap:** aplikasi rekomendasi yang dapat digunakan, model dan data yang terintegrasi, dokumentasi sistem, serta rencana pemeliharaan.

### Hubungan CRISP-DM dengan Metode Sistem

```text
CRISP-DM
├── Business Understanding
├── Data Understanding
├── Data Preparation
├── Modeling
│   ├── K-Means → clustering destinasi
│   ├── AHP     → pembobotan kriteria
│   └── TOPSIS  → perankingan destinasi
├── Evaluation
└── Deployment
```

CRISP-DM bukan pengganti K-Means, AHP, atau TOPSIS. CRISP-DM merupakan kerangka siklus pengembangan proyek, sedangkan K-Means adalah algoritma data mining dan AHP–TOPSIS adalah metode SPK yang digunakan di dalam tahap pemodelan dan evaluasi.

## Rumus Utama

### K-Means — Perhitungan Jarak Euclidean

```text
d(x, c) = √[(x1 - c1)² + (x2 - c2)² + ... + (xn - cn)²]
```

Digunakan untuk menghitung jarak setiap destinasi (x) ke centroid cluster (c), lalu destinasi di-assign ke cluster dengan jarak terdekat.

### AHP — Normalisasi & Bobot Kriteria

```text
Normalisasi matriks:  a'ij = aij / Σ(aij) untuk setiap kolom j
Bobot kriteria (wj):  wj = rata-rata baris ke-j dari matriks ternormalisasi
Consistency Ratio:    CR = CI / RI,  CI = (λmax - n) / (n - 1)
```

Bobot dinyatakan valid jika CR < 0.1.

### TOPSIS — Perankingan Alternatif

```text
1. Normalisasi matriks keputusan:     rij = xij / √Σ(xij²)
2. Matriks ternormalisasi terbobot:   vij = wj × rij
3. Solusi ideal positif (A+) & negatif (A-):
   A+ = { maksimum (kriteria benefit), minimum (kriteria cost) }
   A- = { minimum (kriteria benefit), maksimum (kriteria cost) }
4. Jarak ke solusi ideal:
   D+i = √Σ(vij - A+j)²
   D-i = √Σ(vij - A-j)²
5. Nilai preferensi akhir:
   Vi = D-i / (D+i + D-i)
```

Semakin tinggi nilai Vi (mendekati 1), semakin ideal destinasi tersebut terhadap preferensi user.

## Tahapan Algoritma (Alur Sistem)

```text
1. [CRISP-DM] Business Understanding dan Data Understanding
   → Tetapkan kebutuhan pengguna, tujuan, atribut, dan kualitas data
        ↓
2. [CRISP-DM] Data Preparation
   → Bersihkan, transformasikan, dan normalisasi data destinasi
        ↓
3. User input: profil preferensi multi-variabel —
   budget maksimal, kota tujuan, kategori wisata, hobi
        ↓
4. Filter awal data destinasi berdasarkan kota, kategori,
   dan batas kelayakan budget
        ↓
5. [CRISP-DM — MODELING] K-Means Clustering
   → Kelompokkan destinasi menjadi beberapa segmen karakteristik
     (kedekatan harga, rating, dan kategori)
   → Pilih cluster yang sesuai dengan profil user
        ↓
6. [CRISP-DM — MODELING/SPK] AHP
   → Hitung bobot tiap kriteria (harga, rating, jarak,
     fasilitas, kesesuaian kategori, kesesuaian hobi)
   → Uji konsistensi bobot (CR < 0.1)
        ↓
7. [CRISP-DM — MODELING/SPK] TOPSIS
   → Normalisasi matriks keputusan
   → Hitung jarak ke solusi ideal positif & negatif
   → Hitung nilai preferensi akhir & ranking
        ↓
8. [CRISP-DM — EVALUATION] Evaluasi cluster, konsistensi AHP,
   validasi ranking TOPSIS, dan sensitivity analysis
        ↓
9. [CRISP-DM — DEPLOYMENT] Output Top-5/10 destinasi wisata terbaik,
   lengkap dengan skor dan breakdown alasan per kriteria
        ↓
10. (Opsional) Sensitivity Analysis:
   User dapat mengubah bobot kriteria untuk melihat
   perubahan hasil rekomendasi secara langsung
```

## Arti Setiap Kriteria

| Kode | Kriteria | Jenis | Penjelasan |
|---|---|---|---|
| C1 | Harga Tiket Masuk | Cost | Semakin murah, semakin baik — disesuaikan dengan budget user |
| C2 | Rating Pengunjung | Benefit | Penilaian rata-rata pengunjung terhadap destinasi (skala 1-5) |
| C3 | Jarak/Waktu Tempuh | Cost | Jarak dari kota asal user ke lokasi destinasi |
| C4 | Kelengkapan Fasilitas | Benefit | Ketersediaan fasilitas pendukung (toilet, parkir, warung, dsb) |
| C5 | Kesesuaian Kategori | Benefit | Kecocokan kategori destinasi (alam/budaya/kuliner/dst) dengan minat user |
| C6 | Kesesuaian Hobi | Benefit | Skor kemiripan (Jaccard Similarity) antara hobi user dan tag destinasi |

## Interpretasi Hasil SPK

Nilai preferensi akhir (Vi) dari TOPSIS merepresentasikan seberapa dekat suatu destinasi terhadap kondisi ideal berdasarkan seluruh kriteria yang telah dibobotkan. Destinasi dengan Vi tertinggi ditampilkan sebagai rekomendasi utama. Setiap rekomendasi disertai breakdown skor per kriteria (misalnya: "Destinasi ini direkomendasikan karena harga masuk sesuai budget Anda, rating tinggi (4.5/5), dan sesuai dengan minat wisata alam serta hobi hiking yang Anda pilih") sehingga user memahami alasan di balik rekomendasi, bukan menerima hasil sebagai black box.

Hasil ranking ini digunakan sebagai dasar rekomendasi keputusan wisata bagi user — bukan keputusan final otomatis, melainkan alat bantu (decision support) yang tetap memungkinkan user mempertimbangkan faktor subjektif lain sebelum memutuskan.

## Struktur Proyek

```text
SPK_Destinasi_Wisata/
├── index.html   # Peta interaktif Indonesia (hero section, 38 provinsi, 7 gugus pulau)
└── README.md    # Dokumentasi proyek
```

## Status Proyek

Proyek ini masih dalam tahap pengembangan dan dapat terus dikembangkan sesuai kebutuhan serta fitur tambahan yang diinginkan.

## Lisensi

Proyek ini dibuat untuk kebutuhan akademik dan pengembangan aplikasi berbasis sistem pendukung keputusan.
