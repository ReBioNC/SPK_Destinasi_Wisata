# Rangkuman Pembahasan Metode SPK — TravelFit

Dokumen ini merangkum seluruh pemahaman konseptual, analisis perbandingan metode, serta keputusan teknis yang dibahas selama sesi diskusi Sistem Pendukung Keputusan (SPK) **TravelFit**. Dokumen ini dapat dijadikan bahan belajar, persiapan presentasi, maupun tanya-jawab teknis (sidang/evaluasi proyek).

---

## Daftar Isi
1. [Arsitektur Hybrid: AHP–TOPSIS](#1-arsitektur-hybrid-ahptopsis)
2. [Kenapa Memakai TOPSIS & Kenapa Tidak Metode Lain?](#2-kenapa-memakai-topsis--kenapa-tidak-metode-lain)
3. [Mekanisme Slider Bobot Lanjutan & Rasio Kepentingan (1:1)](#3-mekanisme-slider-bobot-lanjutan--rasio-kepentingan-11)
4. [Analisis SMARTER (ROC) vs. Masalah Nilai Nol](#4-analisis-smarter-roc-vs-masalah-nilai-nol)
5. [Mengenal AHP (Analytic Hierarchy Process)](#5-mengenal-ahp-analytic-hierarchy-process)
6. [Perbandingan Head-to-Head: AHP vs. SMARTER](#6-perbandingan-head-to-head-ahp-vs-smarter)
7. [FAQ Cepat untuk Presentasi / Sidang](#7-faq-cepat-untuk-presentasi--sidang)

---

## 1. Arsitektur Hybrid: AHP–TOPSIS

Proyek TravelFit tidak menggunakan satu metode tunggal dari hulu ke hilir, melainkan menerapkan pendekatan **Hybrid MCDM (*Multi-Criteria Decision Making*)**:

```text
               ┌────────────────────────────────────────────────────────┐
               │                     INPUT PENGGUNA                     │
               │  Kota Asal, Wilayah Tujuan, Budget Tiket, Kategori, Hobi│
               └──────────────────────────┬─────────────────────────────┘
                                          │
                        Filter Database: Provinsi & Tiket ≤ Budget
                                          │
                                          ▼
                         ┌─────────────────────────────────┐
                         │   KANDIDAT DESTINASI (Max 443)  │
                         └────────────────┬────────────────┘
                                          │
    ┌───────────────────────────┐         │
    │      PEMBOBOTAN: AHP      │         │
    │  • 6 Kriteria (C1–C6)     ├─────────┼─────────────────────────┐
    │  • 4 Profil (CR < 0,1)    │         │                         │
    │  • Opsi Slider Kustom     │         │                         │
    └───────────────────────────┘         ▼                         ▼
                                ┌──────────────────────────────────────────┐
                                │          PERANGKINGAN: TOPSIS            │
                                │  1. Matriks Keputusan Dinamis            │
                                │  2. Normalisasi Vektor Euclidean         │
                                │  3. Matriks Terbobot                     │
                                │  4. Solusi Ideal Positif & Negatif (A±)  │
                                │  5. Jarak Euclidean (D+ & D-)            │
                                │  6. Skor Preferensi Kedekatan Relatif Vi │
                                └─────────────────┬────────────────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │  TOP 10 REKOMENDASI     │
                                     └─────────────────────────┘
```

- **AHP** bertugas menentukan **bobot kriteria** secara ilmiah dan konsisten.
- **TOPSIS** bertugas melakukan **pemeringkatan (*ranking*) alternatif** secara cepat dan dinamis.

---

## 2. Kenapa Memakai TOPSIS & Kenapa Tidak Metode Lain?

### A. Alasan Utama Memilih TOPSIS
1. **Kebal terhadap Nilai Nol (*Zero-Value Robustness*):**
   Dataset 443 destinasi di Jawa memiliki banyak nilai $0$:
   - **137 destinasi memiliki tiket masuk gratis (Rp0 / C1 = 0)**.
   - Indikator Fasilitas (C4 = 0) jika tidak ada fasilitas yang terdeteksi dari teks deskripsi.
   - Kecocokan Kategori (C5 = 0) jika di luar kategori pilihan pengguna.
   - Kecocokan Hobi (C6 = 0) jika pengguna tidak memilih hobi (*Jaccard index* = 0).
   Rumus normalisasi vektor TOPSIS tetap sah dan tidak menghasilkan *error division by zero*:
   $$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{p=1}^{m} x_{pj}^2}}$$

2. **Konsep Solusi Ideal Ganda ($A^+$ dan $A^-$):**
   TOPSIS mencari alternatif yang paling dekat dengan solusi ideal positif ($A^+$: benefit tertinggi, cost terendah) sekaligus paling jauh dari solusi ideal negatif ($A^-$: benefit terendah, cost tertinggi). Konsep kompromi geometris ini sangat alami mencerminkan perilaku wisatawan.

3. **Komputasi Efisien ($O(m \cdot n)$):**
   Penghitungan rekomendasi dilakukan secara *real-time* saat form disubmit. TOPSIS dapat merangking ratusan alternatif dalam hitungan milidetik.

4. **Rentang Nilai Standar ($V_i \in [0, 1]$):**
   Skor kedekatan relatif mudah dipahami dan divisualisasikan dalam grafik antarmuka web.

---

### B. Mengapa Metode Lain Ditolak untuk Perangkingan?

| Metode | Cara Kerja | Alasan Ditolak pada TravelFit |
| :--- | :--- | :--- |
| **SAW** *(Simple Additive Weighting)* | Penjumlahan terbobot dari matriks ternormalisasi. | **Error pembagian nol pada kriteria cost:** Rumus normalisasi cost di SAW adalah $\frac{\min(x)}{x_{ij}}$. Jika ada tiket gratis ($x_{ij} = 0$), rumus membagi dengan nol.<br>*(Catatan: SAW tetap diimplementasikan di `recommender/spk/validation.py` hanya untuk validasi internal via korelasi Spearman).* |
| **WP** *(Weighted Product)* | Perkalian nilai alternatif berpangkat bobot ($\prod x_{ij}^{w_j}$). | **Gagal total terhadap nilai 0:** Jika ada $x_{ij} = 0$, perkalian menjadi 0. Kriteria cost berpangkat negatif ($w_j < 0$), sehingga $0^{-w}$ tidak terdefinisi secara matematis. |
| **AHP Penuh** *(AHP merangking alternatif)* | Perbandingan berpasangan antar alternatif. | **Komputasi meledak:** Untuk 443 destinasi pada 1 kriteria dibutuhkan $\frac{443 \times 442}{2} = 97.903$ perbandingan. Untuk 6 kriteria dibutuhkan **587.418 perbandingan**. Mustahil dihitung interaktif di web. |
| **VIKOR** | Solusi kompromi berbasis ukuran utilitas ($S$), *regret* ($R$), dan indeks $Q$. | Memerlukan parameter bobot strategi mayoritas ($v$) dan syarat pengujian tambahan (*acceptable advantage* & *acceptable stability*) yang rumit dijelaskan ke pengguna awam. |
| **ELECTRE / PROMETHEE** | Relasi *outranking* dengan fungsi preferensi dan ambang batas. | Memerlukan penetapan threshold indiferen, preferensi, dan veto yang sulit ditentukan tanpa data mikro preferensi individual. Sering menghasilkan perangkingan parsial (beberapa opsi tidak dapat dibandingkan). |

---

## 3. Mekanisme Slider Bobot Lanjutan & Rasio Kepentingan (1:1)

Pada menu **"Sesuaikan bobot lanjutan"**, terdapat slider 0%–100% untuk masing-masing dari 6 kriteria.

### A. Mengapa Angkanya Bebas dan Bisa Bernilai Sama (1:1)?
- Angka pada slider **bukan persentase absolut yang wajib total 100%**, melainkan **skala kepentingan relatif (rasio)**.
- Jika pengguna menyetel *Harga = 100%* dan *Jarak = 100%*, ini berarti pengguna menghendaki rasio perbandingan **1:1 (sama-sama penting)**.
- Pada backend (`recommender/views.py`), nilai slider dinormalisasi secara otomatis:
  $$w_i = \frac{s_i}{\sum_{j=1}^{6} s_j}$$

> **Contoh:**
> Nilai slider: Harga = 100, Rating = 63, Jarak = 60, Fasilitas = 45, Kategori = 14, Hobi = 40 (Total = 322).
> Bobot efektif TOPSIS:
> - Harga: $100 / 322 \approx 31{,}06\%$
> - Rating: $63 / 322 \approx 19{,}57\%$
> - Jarak: $60 / 322 \approx 18{,}63\%$
> - Fasilitas: $45 / 322 \approx 13{,}98\%$
> - Kategori: $14 / 322 \approx 4{,}35\%$
> - Hobi: $40 / 322 \approx 12{,}42\%$
> *(Jumlah total kembali tepat 100%)*

### B. Kenapa Tidak Dibuat Sistem Ranking Biasa (Urutan 1, 2, 3, 4, 5, 6)?
1. **Tidak bisa menangani kepentingan setara (*Tie*):** Pada ranking ordinal, pengguna dipaksa memilih satu juara 1 dan satu juara 2, padahal pengguna bisa saja menganggap dua kriteria sama-sama prioritas utama.
2. **Kehilangan informasi intensitas (derajat jarak):** Ranking hanya mencatat $A > B$, tetapi tidak tahu apakah bedanya tipis atau berkali-kali lipat.
3. **Tidak bisa menonaktifkan kriteria (0%):** Pada ranking ordinal, peringkat terakhir tetap akan mendapatkan porsi bobot. Melalui slider, kriteria yang tidak dipedulikan dapat digeser ke **0%**.
4. **Fungsi Sebenarnya adalah Uji Sensitivitas:** Slider ini dirancang untuk menguji respons sistem: *"Bagaimana jika bobot harga saya maksimalkan 100%? Apakah urutan destinasi berubah?"*.

---

## 4. Analisis SMARTER (ROC) vs. Masalah Nilai Nol

### A. Apakah SMARTER Ditolak Karena Nilai Nol?
**Bukan.** 
- Rumus utilitas linear alternatif pada SMARTER:
  $$u(x) = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$
  tetap dapat menghitung nilai 0 dengan lancar.
- Alasan nilai 0 adalah penyebab gugurnya **SAW** dan **WP**, bukan SMARTER.

### B. Mengapa Pembobotan ROC pada SMARTER Tidak Digunakan?
Dalam SMARTER, bobot dihitung menggunakan rumus **ROC (*Rank Order Centroid*)**:
$$w_k = \frac{1}{K} \sum_{i=k}^{K} \frac{1}{i}$$

Untuk $K = 6$ kriteria, hasilnya **terkunci otomatis oleh rumus**:
- Rank 1 = **40,8%**
- Rank 2 = **24,2%**
- Rank 3 = **15,8%**
- Rank 4 = **10,3%**
- Rank 5 = **6,1%**
- Rank 6 = **2,8%**

**Kelemahan ROC pada TravelFit:**
1. **Kurva Terlalu Timpang:** Rank 1 langsung menyerap $40{,}8\%$ bobot. Padahal pada kuesioner empiris 28 responden di proyek ini, Kategori ($26{,}0\%$) dan Hobi ($23{,}2\%$) hanya berselisih tipis. ROC akan merusak proporsi nyata preferensi manusia.
2. **Tidak ada mekanisme Uji Konsistensi ($CR$).**
3. **Kriteria terakhir tidak pernah bisa 0%** (selalu terbebani $2{,}8\%$).

---

## 5. Mengenal AHP (Analytic Hierarchy Process)

AHP (dikembangkan oleh Thomas L. Saaty) adalah metode pengambilan keputusan multikriteria yang menstrukturkan masalah ke dalam hierarki dan menentukan bobot melalui **perbandingan berpasangan (*pairwise comparison*)**.

### Tahapan Utama AHP:
1. **Skala Saaty 1–9:** Membandingkan dua kriteria secara relatif (1 = sama penting, 3 = sedikit lebih penting, 5 = jelas lebih penting, 7 = sangat penting, 9 = mutlak penting).
2. **Matriks Resiprokal:** Jika elemen baris $i$ terhadap kolom $j$ bernilai $a_{ij}$, maka $a_{ji} = 1 / a_{ij}$.
3. **Penentuan Bobot:** Dihitung dari normalisasi kolom dan rata-rata baris matriks (pendekatan vektor eigen):
   $$w_i = \frac{1}{n} \sum_{j=1}^{n} \frac{a_{ij}}{\sum_{p=1}^{n} a_{pj}}$$
4. **Uji Konsistensi (*Consistency Ratio* / CR):**
   - Indeks Konsistensi: $CI = \frac{\lambda_{\max} - n}{n - 1}$
   - Rasio Konsistensi: $CR = \frac{CI}{RI}$
   - Untuk $n = 6$ kriteria, $RI = 1{,}24$.
   - **Syarat Validitas:** Nilai $CR < 0{,}1$ (tingkat inkonsistensi di bawah 10%).

### Implementasi AHP di TravelFit:
Diimplementasikan pada `recommender/spk/ahp.py` dan `recommender/spk/profiles.py` untuk menghasilkan 4 profil teruji:
- **Seimbang ($CR = 0{,}0601$):** Kategori 26,0%, Hobi 23,2%, Harga 16,1%, Rating 13,5%, Fasilitas 13,2%, Jarak 7,9% (Hasil kuesioner 28 responden).
- **Hemat ($CR = 0{,}0026$):** Harga tiket dominan (40,6%).
- **Kualitas ($CR = 0{,}0122$):** Rating dominan (38,5%).
- **Petualang ($CR = 0{,}0044$):** Jarak tempuh dominan (34,4%).

---

## 6. Perbandingan Head-to-Head: AHP vs. SMARTER

| Parameter | SMARTER (ROC) | AHP (Saaty) |
| :--- | :--- | :--- |
| **Pendekatan Input** | Mengurutkan ranking ordinal ($1, 2, 3, \dots, n$) | Perbandingan berpasangan kardinal ($a_{ij} \in [1/9, 9]$) |
| **Intensitas Perbedaan** | Tidak diketahui (mengikuti pola kurva rumus ROC) | Terdefinisi jelas (berapa kali lipat lebih penting) |
| **Bisa Bobot Setara (1:1)?** | **Tidak bisa** (harus dipisah menjadi rank berbeda) | **Bisa** (diberi nilai perbandingan 1) |
| **Fleksibilitas Bobot** | **Kaku** (Rank 1 pasti $\approx 40{,}8\%$ pada 6 kriteria) | **Dinamis** (mencerminkan data empiris/survei nyata) |
| **Uji Konsistensi (CR)** | **Tidak ada** | **Ada** ($CR < 0{,}1$ wajib terpenuhi) |
| **Beban Pengguna** | Sangat mudah (cukup urutkan daftar) | Cukup berat jika manual ($n(n-1)/2$ pertanyaan) |
| **Solusi di TravelFit** | Tidak dipakai karena kurvanya terlalu timpang | **Dipakai via Preset Profil**, sehingga pengguna tidak perlu menghitung matriks sendiri |

---

## 7. FAQ Cepat untuk Presentasi / Sidang

**Q: Kenapa tidak memakai AHP murni dari kriteria sampai memilih tempat wisatanya?**  
> *A: Karena perbandingan berpasangan untuk 443 destinasi wisata membutuhkan hampir 600.000 perbandingan, yang mustahil dihitung secara interaktif di web. AHP ideal untuk membobot kriteria, sedangkan TOPSIS ideal untuk merangking alternatif dalam jumlah besar.*

**Q: Apa makna angka skor $V_i = 0{,}85$ pada hasil rekomendasi?**  
> *A: Nilai tersebut adalah tingkat kedekatan relatif alternatif terhadap solusi ideal di antara kandidat yang lolos filter saat itu, bukan berarti "tingkat akurasi atau kecocokan destinasi 85%".*

**Q: Kenapa SAW tidak digunakan sebagai output ke pengguna?**  
> *A: Karena 137 destinasi wisata bertiket Rp0 (gratis). Pada kriteria cost, rumus normalisasi SAW adalah $\min(x)/x$, yang akan menyebabkan division by zero jika ada harga Rp0.*

**Q: Apa fungsi slider bobot jika sistem sudah punya profil AHP?**  
> *A: Slider disediakan sebagai instrumen uji sensitivitas (advanced options) bagi pengguna yang ingin menguji variasi bobot secara bebas tanpa merusak konsistensi matriks AHP profil bawaan.*
