# TravelFit — Sistem Pendukung Keputusan Rekomendasi Destinasi Wisata Multi-Kriteria

Aplikasi web Sistem Pendukung Keputusan (SPK) untuk mengeksplorasi destinasi wisata di Indonesia melalui enam kriteria: harga tiket, rating, jarak garis lurus, indikasi fasilitas, kesesuaian kategori, dan kesesuaian hobi. Pengembangan mengikuti **CRISP-DM** (*Cross-Industry Standard Process for Data Mining*); **K-Means** membentuk label segmen, **AHP** menentukan bobot profil, dan **TOPSIS** meranking kandidat. Nilai peringkat dapat ditelusuri secara matematis, sementara ketepatan rekomendasi di dunia nyata masih harus diuji dengan data terverifikasi dan pengguna.

> **Status data prototipe:** 1.900 dari 2.337 destinasi adalah data simulasi. Generator mengacak harga, rating, dan koordinat di sekitar titik kota; angka ini belum boleh diperlakukan sebagai fakta lapangan. Sebanyak 437 baris dari dataset Jawa merupakan data sumber, tetapi informasi fasilitas dan aktivitasnya juga merupakan ekstraksi heuristik deskripsi. Website menandai hasil simulasi agar pengguna dapat membedakannya.

User memasukkan budget maksimal, kota asal, provinsi tujuan, kategori wisata yang diminati (alam, bahari, belanja, budaya, hiburan, religi), dan hobi terkait wisata (hiking, fotografi, kuliner lokal, dsb). Sistem kemudian memproses kandidat yang lolos filter dan menampilkan peringkat beserta skor relatif dan alasannya.

## Variabel Penentu Keputusan

Keputusan rekomendasi TravelFit ditentukan oleh enam kriteria (C1–C6) yang dihitung bersama, bukan oleh satu variabel tunggal:

- **Budget** berperan sebagai *batas kelayakan* (destinasi di luar budget maksimal tersaring sejak awal) sekaligus sebagai *salah satu* kriteria cost (C1) di tahap perankingan — bukan satu-satunya penentu.
- **Kualitas destinasi** diwakili rating pengunjung (C2) dan kelengkapan fasilitas (C4).
- **Aksesibilitas** saat ini diwakili jarak garis lurus Haversine dari kota asal user (C3), bukan waktu tempuh atau jarak rute jalan.
- **Kecocokan personal** diwakili kesesuaian kategori (C5) dan kesesuaian hobi (C6).

Besarnya pengaruh tiap variabel tidak fixed. Bobot dasar dihitung dengan AHP melalui beberapa **profil preferensi** (misalnya *Hemat*, *Kualitas*, *Petualang*, *Seimbang*) — setiap profil memiliki matriks perbandingan berpasangan tersendiri yang telah lolos uji konsistensi (CR < 0,1). User cukup memilih profil yang paling mendekati prioritasnya, lalu dapat menyetel bobot lebih lanjut melalui sensitivity analysis. Artinya user yang memprioritaskan pengalaman (rating, hobi) bisa mendapatkan hasil berbeda dari user yang memprioritaskan hemat — walau budgetnya sama.

## Identitas Kelompok

| Nama | NIM | Peran |
|---|---|---|
| Kristofer Ryan Giggs aka Ganyol | 412024005 | Ketua |
| Cristian Dion | 412024006 | Anggota |
| Reynard Liu | 412025022 | Anggota |
| Justin Augusto Liusri | 412025029 | Anggota |

## Latar Belakang Masalah

Wisatawan, khususnya kalangan mahasiswa dan backpacker, sering kesulitan memilih destinasi wisata karena informasi harga tiket, rating, jarak, dan fasilitas tersebar di berbagai platform (Google Maps, Instagram, TripAdvisor) dan sulit dibandingkan secara objektif. Banyak orang akhirnya memilih destinasi hanya berdasarkan tren media sosial atau patokan harga termurah, tanpa mempertimbangkan trade-off antar banyak faktor: destinasi murah bisa jadi jauh dan fasilitas minim, destinasi populer bisa jadi tidak cocok dengan hobi. Dibutuhkan alat bantu yang menimbang seluruh variabel tersebut secara seimbang dan transparan.

## Fungsi & Manfaat Aplikasi

**Fungsi utama:**
- Memfilter destinasi wisata berdasarkan batas kelayakan (budget dan wilayah), serta mengelompokkannya berdasarkan harga, rating, dan kategori sebagai label segmen yang mudah dipahami
- Menghitung skor kesesuaian tiap destinasi terhadap preferensi user secara objektif dan terukur, dengan bobot kriteria yang mengikuti profil preferensi pilihan user
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
| Data Mining | K-Means Clustering | Mengelompokkan destinasi ke dalam segmen berdasarkan harga, rating, dan kategori; label segmen ditampilkan pada rekomendasi |
| SPK — Pembobotan Kriteria | AHP (Analytic Hierarchy Process) | Menentukan bobot kepentingan tiap kriteria per profil preferensi secara terstruktur dan teruji konsistensinya |
| SPK — Perankingan Alternatif | TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) | Meranking destinasi berdasarkan kedekatannya terhadap solusi ideal positif dan negatif |
| SPK — Validasi Metode | SAW (Simple Additive Weighting) + Spearman Rank Correlation | Pembanding (*baseline*) untuk memverifikasi kestabilan ranking TOPSIS pada tahap Evaluation |

### Alasan Pemilihan Metode

**CRISP-DM** dipilih sebagai kerangka kerja karena menyediakan tahapan pengembangan data mining yang sistematis, iteratif, dan mudah didokumentasikan. Kerangka ini memastikan proses tidak hanya berfokus pada pembuatan model, tetapi juga dimulai dari pemahaman kebutuhan wisatawan, pemeriksaan kualitas data, evaluasi hasil, hingga penerapan model ke dalam aplikasi.

**K-Means** dipilih karena data destinasi wisata tidak memiliki label "benar/salah" (bersifat unsupervised) — tujuannya mengelompokkan destinasi yang mirip karakteristiknya. K-Means juga ringan secara komputasi dan mudah dilatih ulang saat data bertambah. Dalam sistem ini, hasil clustering diposisikan sebagai **label interpretatif** relatif terhadap data pelatihan (misalnya "Segmen 1 · harga rendah") yang ditampilkan pada penjelasan rekomendasi, bukan sebagai penyaring keras kandidat. Pemetaan profil user ke satu cluster tertentu berisiko membuang destinasi yang sebenarnya cocok; penyaringan keras dilakukan oleh batas budget dan wilayah, sedangkan trade-off antar-kriteria ditangani AHP–TOPSIS.

**AHP** dipilih untuk menentukan bobot kriteria karena metode ini memungkinkan perbandingan berpasangan antar kriteria secara terstruktur dan dilengkapi mekanisme uji konsistensi (Consistency Ratio), sehingga bobot yang dihasilkan dapat dipertanggungjawabkan secara metodologis, bukan ditentukan secara subjektif sepihak. Karena mengisi 15 perbandingan berpasangan (6 kriteria) saat runtime tidak praktis bagi user awam dan rawan gagal uji konsistensi, AHP diterapkan pada **profil preferensi preset**: setiap profil (Hemat, Kualitas, Petualang, Seimbang) memiliki matriks perbandingan berpasangan yang disusun pengembang, diuji CR < 0,1, dan disimpan sebagai bobot dasar. User memilih profil, lalu dapat menyetel bobot melalui slider sensitivity analysis. Dengan cara ini uji konsistensi tetap terjaga sekaligus personalisasi tetap terpenuhi.

**TOPSIS** dipilih untuk tahap perankingan karena mempertimbangkan jarak alternatif terhadap solusi ideal positif *dan* negatif sekaligus. Jarak Euclidean menghukum penyimpangan besar secara kuadratik, sehingga TOPSIS tidak sepenuhnya kompensatoris seperti SAW — destinasi yang sangat buruk pada satu kriteria (misalnya murah tetapi rating sangat rendah) tidak mudah "tertutupi" oleh keunggulan di kriteria lain. Secara konsep TOPSIS juga mudah dijelaskan ke pengguna awam ("destinasi ini paling dekat dengan kondisi ideal Anda"). Untuk *explainability* per kriteria, sistem menampilkan kontribusi jarak terbobot tiap kriteria terhadap solusi ideal (`vij` vs `A+j`), sehingga user tetap melihat kriteria mana yang membuat destinasi unggul atau tertinggal.

Dua keterbatasan TOPSIS yang disadari dan ditangani:

- **Rank reversal** — solusi ideal dihitung dari himpunan kandidat, sehingga peringkat bisa berubah saat kandidat bertambah/berkurang akibat perubahan filter. Ini dimitigasi dengan menguji kestabilan ranking pada beberapa skenario filter di tahap Evaluation dan, bila perlu, menggunakan nilai ideal tetap dari seluruh dataset (*fixed reference TOPSIS*).
- **Sensitivitas normalisasi vektor terhadap outlier** — nilai ekstrem (misalnya tiket sangat mahal) memengaruhi penyebut normalisasi. Ini dimitigasi dengan pemeriksaan outlier di tahap Data Understanding dan penerapan batas budget sebagai filter awal.

## Penerapan CRISP-DM

CRISP-DM digunakan sebagai kerangka utama pengembangan data mining. Prosesnya bersifat iteratif, sehingga hasil evaluasi pada suatu tahap dapat mengarahkan pengembang kembali ke tahap sebelumnya untuk memperbaiki data, fitur, atau model.

### 1. Business Understanding

Tahap ini berfokus pada pemahaman masalah, kebutuhan pengguna, dan tujuan aplikasi.

- **Permasalahan bisnis:** wisatawan kesulitan membandingkan banyak destinasi secara objektif karena informasi harga, rating, jarak, fasilitas, kategori, dan aktivitas tersebar di berbagai sumber.
- **Tujuan bisnis:** membantu pengguna menemukan destinasi yang paling sesuai dengan budget, lokasi, minat, dan hobinya melalui rekomendasi yang transparan.
- **Tujuan data mining:** menemukan kelompok destinasi dengan karakteristik serupa dan memberinya label segmen yang mudah dipahami, sehingga hasil rekomendasi AHP–TOPSIS dapat dijelaskan dengan konteks tambahan ("destinasi ini termasuk segmen Ekonomis dengan rating tinggi").
- **Target pengguna:** wisatawan umum, mahasiswa, backpacker, serta pelaku UMKM atau agen perjalanan skala kecil.
- **Kriteria keberhasilan:** sistem mampu menghasilkan rekomendasi relevan, menampilkan alasan rekomendasi, memberikan hasil perhitungan yang konsisten, serta merespons perubahan preferensi pengguna.
- **Batasan:** kualitas rekomendasi bergantung pada kelengkapan dan kebaruan data destinasi; harga, rating, dan fasilitas dapat berubah. Waktu tempuh belum dihitung.

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
- Menghitung jarak garis lurus Haversine dari lokasi asal pengguna ke destinasi. Estimasi waktu tempuh memerlukan data rute yang belum tersedia.
- Menghitung kesesuaian hobi menggunakan **Jaccard Similarity** antara hobi pengguna dan tag aktivitas destinasi.
- Melakukan normalisasi atau standardisasi fitur numerik sebelum K-Means agar fitur berskala besar, seperti harga dan jarak, tidak mendominasi pembentukan cluster.
- Memilih fitur clustering yang relevan. Implementasi saat ini memakai harga dan rating terstandardisasi serta one-hot kategori. C4 dikecualikan karena pada data sumber Jawa mayoritas fasilitas tidak tercatat; nilai kosong tidak dapat ditafsirkan sebagai fasilitas tidak tersedia. Jarak dan kecocokan personal dihitung saat rekomendasi.

**Output tahap:** dataset bersih dan dataset transformasi yang siap digunakan untuk pemodelan serta perankingan.

### 4. Modeling

Tahap pemodelan terdiri atas clustering destinasi dan proses SPK.

1. Menentukan kandidat jumlah cluster (`k`) dan nilai awal centroid.
2. Menjalankan **K-Means Clustering** pada data destinasi yang telah dinormalisasi.
3. Membandingkan beberapa nilai `k` menggunakan metode seperti *Elbow Method* dan *Silhouette Score*.
4. Menginterpretasikan setiap cluster dari statistik data pelatihan dan memberinya label relatif, misalnya "Segmen 1 · harga rendah". Label disimpan sebagai atribut destinasi dan ditampilkan pada penjelasan rekomendasi.
5. Menyaring kandidat alternatif berdasarkan batas kelayakan budget dan wilayah pilihan pengguna (bukan berdasarkan cluster maupun kategori, agar C5 tetap berfungsi sebagai kriteria pembeda).
6. Menyusun matriks perbandingan berpasangan **AHP** untuk setiap profil preferensi (Hemat, Kualitas, Petualang, Seimbang), menghitung bobot C1–C6, dan memastikan nilai *Consistency Ratio* setiap profil kurang dari 0,1. Bobot profil yang dipilih pengguna menjadi bobot dasar, yang dapat disetel lebih lanjut melalui sensitivity analysis.
7. Menggunakan **TOPSIS** untuk menghitung nilai preferensi dan menentukan peringkat akhir destinasi.
8. Menghitung ranking pembanding dengan **SAW** menggunakan bobot yang sama, sebagai bahan validasi di tahap Evaluation.

**Output tahap:** model K-Means beserta label cluster, bobot kriteria AHP per profil beserta nilai CR-nya, nilai preferensi TOPSIS, ranking pembanding SAW, dan daftar rekomendasi terurut.

### 5. Evaluation

Tahap ini memastikan model dan hasil rekomendasi telah memenuhi tujuan sistem.

- Mengevaluasi kualitas cluster menggunakan *Silhouette Score*, nilai *inertia/SSE*, ukuran setiap cluster, dan kemudahan interpretasi cluster.
- Memastikan cluster tidak hanya baik secara matematis, tetapi juga masuk akal dalam konteks destinasi wisata.
- Menguji konsistensi bobot AHP untuk setiap profil preferensi dengan syarat `CR < 0,1`.
- Memeriksa hasil TOPSIS secara manual menggunakan beberapa skenario profil pengguna.
- Membandingkan ranking TOPSIS dengan ranking SAW pada bobot yang sama menggunakan *Spearman Rank Correlation* (ρ). Nilai ρ yang tinggi menunjukkan kedua metode sepakat pada urutan besar; perbedaan pada posisi tertentu dianalisis untuk memastikan TOPSIS memberi keputusan yang lebih masuk akal pada kasus trade-off ekstrem.
- Korelasi TOPSIS–SAW mengukur kesepakatan antar-metode, bukan akurasi rekomendasi terhadap pilihan wisatawan. Contoh 10 alternatif pada spreadsheet menghasilkan ρ sekitar 0,297; validasi pengguna masih diperlukan.
- Menguji *rank reversal*: menjalankan TOPSIS pada beberapa variasi filter (misalnya budget diperlonggar/diperketat) dan memeriksa apakah urutan destinasi Top-5 yang sama tetap stabil.
- Melakukan *sensitivity analysis* untuk melihat stabilitas peringkat saat bobot kriteria berubah.
- Memvalidasi apakah rekomendasi memenuhi filter wajib seperti budget dan wilayah pilihan pengguna, serta apakah destinasi dengan kesesuaian kategori/hobi tinggi memang naik peringkat.
- Jika hasil belum memenuhi kriteria keberhasilan, proses dapat kembali ke tahap Data Understanding, Data Preparation, atau Modeling.

**Output tahap:** laporan evaluasi cluster, hasil uji konsistensi AHP per profil, validasi ranking TOPSIS, hasil perbandingan TOPSIS–SAW (Spearman ρ), hasil uji rank reversal, hasil sensitivity analysis, dan keputusan kelayakan model.

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
│   ├── K-Means → clustering + label segmen destinasi
│   ├── AHP     → pembobotan kriteria per profil preferensi
│   ├── TOPSIS  → perankingan destinasi (metode utama)
│   └── SAW     → perankingan pembanding (baseline)
├── Evaluation
│   ├── Silhouette / SSE       → kualitas cluster
│   ├── CR < 0,1               → konsistensi AHP
│   ├── Spearman ρ TOPSIS–SAW  → validasi metode ranking
│   └── Sensitivity analysis   → stabilitas ranking
└── Deployment
```

CRISP-DM bukan pengganti K-Means, AHP, atau TOPSIS. CRISP-DM merupakan kerangka siklus pengembangan proyek, sedangkan K-Means adalah algoritma data mining dan AHP–TOPSIS adalah metode SPK yang digunakan di dalam tahap pemodelan dan evaluasi. SAW hanya berperan sebagai pembanding, bukan metode yang menentukan rekomendasi akhir.

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

### SAW — Perankingan Pembanding (Baseline)

```text
Normalisasi:  rij = xij / max(xj)   untuk kriteria benefit
              rij = min(xj) / xij   untuk kriteria cost
Skor akhir:   Si = Σ (wj × rij)
```

SAW dihitung dengan bobot AHP yang sama seperti TOPSIS. Hasilnya tidak ditampilkan ke user, melainkan digunakan untuk validasi di tahap Evaluation.

### Spearman Rank Correlation — Validasi Metode

```text
ρ = 1 - [6 × Σ di²] / [n × (n² - 1)]
di = selisih peringkat destinasi ke-i antara TOPSIS dan SAW
n  = jumlah destinasi yang diranking
```

Nilai ρ mendekati 1 menunjukkan kedua metode menghasilkan urutan yang konsisten; destinasi dengan `di` besar dianalisis secara manual untuk memahami kasus trade-off yang membedakan kedua metode.

## Tahapan Algoritma (Alur Sistem)

```text
1. [CRISP-DM] Business Understanding dan Data Understanding
   → Tetapkan kebutuhan pengguna, tujuan, atribut, dan kualitas data
        ↓
2. [CRISP-DM] Data Preparation
   → Bersihkan, transformasikan, dan normalisasi data destinasi
        ↓
3. [CRISP-DM — MODELING] K-Means Clustering (offline, sekali per dataset)
   → Kelompokkan destinasi berdasarkan harga, rating, dan kategori
   → Beri label tiap cluster (mis. "Ekonomis", "Premium")
     dan simpan sebagai atribut destinasi
        ↓
4. User input: profil preferensi multi-variabel —
   budget maksimal, kota tujuan, kategori wisata yang diminati,
   hobi, dan profil prioritas (Hemat / Kualitas / Petualang / Seimbang)
        ↓
5. Filter awal data destinasi berdasarkan batas kelayakan
   budget dan wilayah (kategori & hobi TIDAK difilter keras —
   keduanya menjadi kriteria C5 dan C6 di tahap ranking)
        ↓
6. [CRISP-DM — MODELING/SPK] AHP
   → Ambil matriks perbandingan berpasangan sesuai profil
     prioritas yang dipilih user
   → Hitung bobot C1–C6, uji konsistensi (CR < 0.1)
   → Terapkan penyesuaian bobot dari slider user (bila ada)
        ↓
7. [CRISP-DM — MODELING/SPK] TOPSIS
   → Normalisasi matriks keputusan
   → Hitung jarak ke solusi ideal positif & negatif
   → Hitung nilai preferensi akhir & ranking
        ↓
8. [CRISP-DM — EVALUATION] Evaluasi cluster, konsistensi AHP,
   perbandingan TOPSIS–SAW (Spearman ρ), uji rank reversal,
   dan sensitivity analysis
        ↓
9. [CRISP-DM — DEPLOYMENT] Output Top-5/10 destinasi wisata terbaik,
   lengkap dengan skor, label cluster, dan breakdown alasan per kriteria
        ↓
10. (Opsional) Sensitivity Analysis:
   User dapat mengubah bobot kriteria untuk melihat
   perubahan hasil rekomendasi secara langsung
```

## Arti Setiap Kriteria

| Kode | Kriteria | Jenis | Penjelasan |
|---|---|---|---|
| C1 | Harga Tiket Masuk | Cost | Semakin murah, semakin baik — disesuaikan dengan budget user |
| C2 | Rating Destinasi | Benefit | Rating pada dataset (skala 1–5); untuk data simulasi nilainya diacak |
| C3 | Jarak Garis Lurus | Cost | Haversine dari koordinat kota asal ke koordinat destinasi; bukan jarak jalan atau waktu tempuh |
| C4 | Indikasi Fasilitas | Benefit | Rata-rata empat indikator bersama: toilet, parkir, warung, musala. Pada data Jawa indikator berasal dari penyebutan dalam deskripsi, bukan verifikasi fasilitas di lokasi |
| C5 | Kesesuaian Kategori | Benefit | Kecocokan kategori destinasi (alam/bahari/belanja/budaya/hiburan/religi) dengan minat user. Bernilai 1 untuk kategori utama, 0,5 untuk kategori sekunder, dan 0 untuk kategori lain |
| C6 | Kesesuaian Hobi | Benefit | Skor kemiripan (Jaccard Similarity) antara hobi user dan tag destinasi; bila hobi tidak dipilih, C6 bernilai sama untuk seluruh kandidat sehingga tidak memengaruhi ranking |

Catatan: budget dan wilayah adalah satu-satunya **filter keras** (destinasi di luar keduanya tidak masuk kandidat). Kategori dan hobi sengaja tidak dijadikan filter keras — jika kategori difilter lebih dulu, C5 akan bernilai sama untuk semua kandidat dan bobotnya terbuang percuma.

## Interpretasi Hasil SPK

Nilai preferensi akhir (Vi) dari TOPSIS merepresentasikan kedekatan relatif suatu destinasi terhadap solusi ideal di antara kandidat yang lolos filter. Destinasi dengan Vi tertinggi ditampilkan sebagai rekomendasi utama. Tiap kartu menampilkan label cluster dan posisi C1–C6 terhadap rentang nilai ideal–terburuk dari **seluruh kandidat yang sama**, bukan hanya Top-10. Angka per kriteria ini membantu membaca kelebihan dan kekurangan relatif; angka itu bukan persentase kontribusi kausal pada Vi. Kriteria yang sama untuk semua kandidat ditampilkan sebagai “Setara”.

Hasil ranking ini digunakan sebagai dasar rekomendasi keputusan wisata bagi user — bukan keputusan final otomatis, melainkan alat bantu (decision support) yang tetap memungkinkan user mempertimbangkan faktor subjektif lain sebelum memutuskan.

## Struktur Proyek

```text
SPK_Destinasi_Wisata/
├── index.html   # Peta interaktif Indonesia (hero section, 38 provinsi, 7 gugus pulau)
└── README.md    # Dokumentasi proyek
```

## Menjalankan Website TravelFit

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py import_destinations
python manage.py train_clusters
python manage.py test
python manage.py runserver
```

Buka http://localhost:8000 — isi preferensi (budget, kota asal, wilayah, kategori,
hobi, profil), lalu lihat Top-10 rekomendasi. Geser slider sensitivitas untuk
mengubah bobot manual, dan buka halaman Peta untuk eksplorasi 38 provinsi.

Untuk menjalankan di luar lingkungan lokal, set `DJANGO_DEBUG=0`,
`DJANGO_SECRET_KEY` (nilai rahasia sendiri), dan `DJANGO_ALLOWED_HOSTS`
(daftar host dipisahkan koma). Kunci bawaan hanya untuk pengembangan lokal.

Catatan data: impor menggabungkan `Dataset_Wisata_38_Provinsi.xlsx` (1.900 baris
simulasi, 38 provinsi) dengan `data/processed/destinations_clean.csv` (437 baris
detail Jawa; total 2.337 baris). Nama provinsi dinormalisasi ke varian XLSX.
`train_clusters` membatasi harga pelatihan pada persentil ke-99, memilih `k` dari
2–6 memakai silhouette dengan ukuran cluster minimum 5%, melatih centroid hanya
pada 437 baris sumber Jawa, lalu memberi label centroid terdekat ke seluruh data.
Fitur K-Means dihitung ulang dari basis data website; kolom C4 pada notebook
preprocessing tetap ada untuk eksplorasi, tetapi tidak masuk pelatihan cluster
karena cakupan bukti fasilitasnya rendah.
Hasil evaluasinya tersimpan di `reports/clustering/kmeans_evaluation.json`.
Jalankan `train_clusters` kembali setelah `import_destinations`, karena impor
mengosongkan label lama. Label pada baris simulasi tetap berstatus simulasi.

### Batasan evaluasi saat ini

- Uji konsistensi AHP dan contoh manual TOPSIS tersedia di tes otomatis.
- Silhouette dan inertia K-Means tercatat saat `train_clusters` dijalankan.
- Contoh Spearman TOPSIS–SAW sudah dihitung, tetapi belum membuktikan relevansi kepada wisatawan.
- Uji pengguna/survei, verifikasi harga dan fasilitas lapangan, serta uji rank reversal lintas skenario filter masih perlu dilakukan sebelum hasil diklaim valid untuk keputusan perjalanan nyata.

## Status Proyek

Proyek ini masih dalam tahap pengembangan dan dapat terus dikembangkan sesuai kebutuhan serta fitur tambahan yang diinginkan.

## Lisensi

Proyek ini dibuat untuk kebutuhan akademik dan pengembangan aplikasi berbasis sistem pendukung keputusan.
