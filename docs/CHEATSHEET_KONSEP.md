# TravelFit — Cheatsheet Konsep (buat presentasi & tanya-jawab)

> Versi teknis (perintah, folder, file): [CHEATSHEET.md](CHEATSHEET.md).
> Rumus lengkap: [README.md](../README.md) · Sumber data: [Dokumentasi.md](../Dokumentasi.md)

---

## 1. Satu kalimat

TravelFit adalah **SPK rekomendasi destinasi wisata di Jawa**. **AHP** memberi bobot
pada 6 kriteria, **TOPSIS** meranking destinasi, dan **K-Means** hanya memberi
label segmen. Seluruh proses dibingkai dengan **CRISP-DM**.

```text
Input user ─► filter (provinsi + tiket ≤ budget) ─► matriks C1–C6 ─► TOPSIS (bobot AHP) ─► Top 10
                                                                      ▲
                                    K-Means (offline) ─► label segmen ┘ (ditampilkan saja, tidak memfilter)
```

## 2. Angka yang wajib hafal

| Hal | Nilai |
| --- | --- |
| Total destinasi | **443** = 437 Kaggle + 6 kurasi Jawa |
| Provinsi tujuan | 6 (Banten, DKI, Jabar, Jateng, DIY, Jatim) |
| Kriteria | 6: C1 harga, C3 jarak (**cost**); C2 rating, C4 fasilitas, C5 kategori, C6 hobi (**benefit**) |
| Profil AHP | 4: Seimbang (**kuesioner 28 responden**), Hemat, Kualitas, Petualang (preset). Semua **CR < 0,1** |
| RI (n = 6) | 1,24 |
| Hasil K-Means | **k = 2** (414 & 29 anggota), silhouette **0,54302** |
| Fitur K-Means | 8: harga (cap P99 Rp275.800 + Z-score), rating (Z-score), 6 one-hot kategori |
| Output | Maksimal **10** rekomendasi |
| Tiket gratis | 137 dari 443 destinasi (Rp0) |

### Bobot profil (hasil AHP)

| Profil | C1 Harga | C2 Rating | C3 Jarak | C4 Fasilitas | C5 Kategori | C6 Hobi | CR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Seimbang (kuesioner) | 16,1% | 13,5% | 7,9% | 13,2% | **26,0%** | 23,2% | 0,060147 |
| Hemat | **40,6%** | 12,7% | 13,3% | 6,9% | 13,3% | 13,3% | 0,002559 |
| Kualitas | 13,0% | **38,5%** | 13,6% | 7,9% | 13,6% | 13,6% | 0,012159 |
| Petualang | 14,0% | 14,0% | **34,4%** | 7,5% | 15,0% | 15,0% | 0,004431 |

---

## 3. Kenapa TOPSIS? (dibanding metode lain)

**Inti jawaban:** TOPSIS mudah ditelusuri langkah demi langkah, menangani cost dan
benefit sekaligus, dan **tidak rusak oleh nilai nol**. Data kita banyak berisi nol:
137 tiket gratis, C4 = 0, C5 = 0, dan C6 = 0 kalau hobi tidak dipilih.

| Metode | Cara kerja singkat | Kenapa tidak dipakai untuk ranking TravelFit |
| --- | --- | --- |
| **SAW** | Jumlah terbobot dari nilai ternormalisasi | Normalisasi cost `min/x` **tidak terdefinisi kalau ada x = 0** (tiket gratis). Hanya mengukur "skor total", tidak ada konsep jarak ke ideal. **Tetap dipakai sebagai pembanding internal** (`spk/validation.py` + Spearman) |
| **WP** (Weighted Product) | Perkalian nilai berpangkat bobot | Nilai 0 membuat hasil kali = 0, dan cost berpangkat negatif `0^(-w)` **tidak terdefinisi**. Padahal banyak C1/C5/C6 = 0 |
| **AHP penuh** (untuk alternatif juga) | Bandingkan semua alternatif berpasangan | 443 destinasi → 443×442/2 ≈ **97.903 perbandingan per kriteria**. Mustahil, dan kandidat berubah tiap input user |
| **VIKOR** | Solusi kompromi (utility S, regret R, Q) | Perlu parameter tambahan *v* dan syarat penerimaan, jadi lebih rumit dijelaskan ke user awam. Kebutuhan kita cukup dengan ranking |
| **ELECTRE / PROMETHEE** | Outranking dengan threshold dan fungsi preferensi | Butuh threshold indifference/preference per kriteria yang tidak punya dasar data. Hasil bisa parsial (tidak semua alternatif terurut) |

**Kelebihan TOPSIS yang dipakai di app:**
- Memakai **dua acuan sekaligus**: dekat ke solusi ideal (A⁺) dan jauh dari anti-ideal (A⁻).
- Skor `Vi` ada di rentang 0–1 dan mudah dibaca, juga ditampilkan sebagai bar per kriteria ("unggul di …, tertahan oleh …").
- Komputasinya ringan (O(m·n)), jadi bisa dihitung **langsung saat user submit**.
- Edge case sudah ditangani: kolom semua nol → 0, satu kandidat → `Vi = 1`, kandidat kosong → pesan.

**Kelemahan (jujur kalau ditanya):**
- **Rank reversal**: menambah atau menghapus kandidat bisa mengubah urutan kandidat lain, karena normalisasi dan A⁺/A⁻ bergantung pada himpunan kandidat.
- Skor `Vi` itu **relatif**. `0,8` ≠ 80% puas atau akurat.
- Bobot Seimbang dari kuesioner biner (pilih satu dari dua), jadi perlu asumsi konversi; profil lain preset pengembang.

## 4. Kenapa AHP untuk bobot?

- Manusia lebih mudah menilai "harga **lebih penting 2×** dari jarak" (perbandingan berpasangan) daripada langsung menulis "harga 26,9%".
- Ada **uji konsistensi (CR)** sehingga bobot yang kontradiktif bisa ditolak (CR ≥ 0,1 → profil dibuang otomatis di `profiles.py`).
- Hanya **6 kriteria** → 15 perbandingan per profil, jadi ringan.
- Pembagian peran: AHP **memberi bobot** pada kriteria, TOPSIS **meranking** alternatif. Kombinasi ini lazim di literatur SPK.

**Alternatif pembobotan lain & alasannya:**
- *Bobot sama rata*: mengabaikan preferensi user.
- *Entropy/CRITIC* (bobot objektif dari data): bobotnya sama untuk semua user, tidak bisa "Hemat" vs "Kualitas".
- *Slider langsung*: **ada di web sebagai opsi kustom**, tapi itu **bukan AHP** (tanpa CR). Kalau semua slider nol → kembali ke bobot profil.

## 5. Kenapa K-Means? (dan kenapa bukan untuk ranking)

- Tujuannya **segmentasi tanpa label** (unsupervised), yaitu mengelompokkan destinasi yang mirip harga, rating, dan kategori.
- Sederhana, centroid mudah dijelaskan ("cluster harga rendah vs tinggi"), dan cocok untuk fitur numerik yang sudah distandardisasi.
- k dipilih secara objektif: coba **k = 2..6**, ambil **silhouette tertinggi**, dengan syarat ukuran cluster minimal **22** (5% dari 443).
- k-means++, 10 inisialisasi, **seed 42** → hasil reprodusibel.
- Harga di-**cap P99** karena K-Means sensitif terhadap outlier. Cap **hanya untuk fitur clustering**; C1 TOPSIS tetap memakai harga asli.
- **Bukan metode ranking**: label cluster tidak memfilter kandidat dan tidak mengubah bobot.
- Silhouette 0,543 = evaluasi internal bentuk cluster, **bukan akurasi rekomendasi**.

Kenapa bukan DBSCAN atau hierarchical? DBSCAN butuh `eps/minPts` dan bisa
menandai titik sebagai noise, padahal semua 443 destinasi wajib berlabel.
Hierarchical lebih berat dan label akhirnya tetap perlu dipotong manual.

## 6. Kenapa kriteria dihitung seperti itu?

| Kriteria | Pilihan | Alasan |
| --- | --- | --- |
| C1 Harga | Harga tiket asli 1 destinasi/orang | Budget = batas **tiket**, bukan total perjalanan. Ongkos transport/makan/inap tidak punya data yang terkalibrasi |
| C2 Rating | Rating sumber; Tahura diimputasi median 4,5 (ditandai) | Lebih baik daripada membuang destinasi; status imputasi ditampilkan ke user |
| C3 Jarak | **Haversine** (garis lurus, R = 6371 km) | Deterministik, tanpa API eksternal (OSRM ada rate limit). Konsekuensinya bukan jarak jalan |
| C4 Fasilitas | Jumlah penyebutan di deskripsi ÷ 6 | Tidak ada data fasilitas lapangan. **0 = tidak disebut**, bukan pasti tidak ada |
| C5 Kategori | Utama 1, sekunder 0,5, lain 0 | Sederhana dan mengakomodasi dua minat |
| C6 Hobi | **Jaccard** = \|H∩T\| / \|H∪T\| | Ukuran kemiripan dua himpunan (hobi vs tag); otomatis ternormalisasi 0–1 |

## 7. Kenapa CRISP-DM?

Kerangka proses data mining yang **iteratif**: Business Understanding → Data
Understanding → Data Preparation → Modeling → Evaluation → Deployment. Kerangka ini
menjaga keputusan teknis tetap terhubung ke tujuan. Contohnya, temuan saat
evaluasi (harga paket, koordinat Marina) membuat kita kembali ke tahap
preparation. CRISP-DM adalah **kerangka**, bukan algoritma.

## 8. Keputusan data penting

- **Semua 443 ID dipertahankan.** Data bermasalah tidak dihapus, tapi diberi flag dan catatan kualitas.
- **Pelabuhan Marina**: label Jakarta, tapi koordinat sumber di luar Jawa (dekat Batam). Dipertahankan dan diberi flag review.
- **Tahura**: rating kosong → diimputasi median 4,5 untuk model. Rating sumber tetap kosong.
- **Pipeline ber-hash/fingerprint**: importer dan trainer menolak data olahan yang usang, jadi DB dan model tidak memakai hasil preprocessing lama.

## 9. Stack singkat

Django 5.2 + SQLite + Python, template HTML/CSS/JS native. AHP, TOPSIS, Haversine,
dan Jaccard ditulis sendiri (**stdlib**, tanpa library SPK), jadi setiap langkah
bisa dicocokkan dengan Excel `Perhitungan_AHP_TOPSIS_TravelFit.xlsx`.

---

## 10. Pertanyaan yang kemungkinan muncul

**"Kenapa tidak SAW saja? Lebih simpel."**
→ SAW memakai `min/x` untuk cost, padahal 137 destinasi gratis (x = 0). SAW juga cuma
menjumlah skor, tanpa acuan ideal/anti-ideal. SAW tetap kami pakai sebagai **pembanding**
(korelasi Spearman), bukan sebagai output.

**"Skor 0,85 artinya 85% cocok?"**
→ Bukan. Itu kedekatan relatif ke solusi ideal **di antara kandidat saat itu**.
Ganti budget atau provinsi, skornya bisa berubah.

**"Bobot AHP dari mana? Survei?"**
→ Profil **Seimbang** dari kuesioner 28 responden (15 pasangan). Karena jawabannya
"pilih satu dari dua", nilai matriks = jumlah pemilih Ci / jumlah pemilih Cj; CR = 0,060 < 0,1.
Hemat/Kualitas/Petualang tetap preset pengembang sebagai variasi.

**"Apa gunanya K-Means kalau tidak dipakai ranking?"**
→ Untuk **segmentasi/insight** (mis. destinasi murah vs mahal/hiburan) dan
ditampilkan sebagai label. Ranking tetap TOPSIS supaya keduanya tidak tercampur.

**"Kenapa k = 2?"**
→ Silhouette tertinggi di antara k = 2..6, dan semua kandidat memenuhi ukuran minimum 22 anggota.

**"Kenapa jaraknya garis lurus?"**
→ Deterministik, cepat, tanpa ketergantungan API eksternal. Kekurangannya tidak
mencerminkan jalan atau waktu tempuh, dan hal ini ditulis jelas di UI.

**"Kalau user tidak pilih hobi?"**
→ C6 = 0 untuk semua kandidat. Kolom yang semua nilainya nol tidak memengaruhi ranking
TOPSIS, jadi tidak ada yang dianggap "cocok sempurna".

**"Kalau cuma 1 kandidat lolos filter?"**
→ `Vi = 1` untuk menghindari pembagian nol. Itu bukan berarti kualitasnya sempurna.

**"Rank reversal?"**
→ Ya, itu kelemahan TOPSIS: urutan bisa berubah kalau himpunan kandidat berubah.
Di app ini kandidat memang berubah sesuai filter user, jadi skor dibaca relatif per pencarian.

**"Bagaimana memastikan hitungan benar?"**
→ Unit test (AHP, TOPSIS, edge case), cross-check SAW + Spearman, dan perhitungan
manual di Excel yang cocok dengan view Django pada input yang sama.

## 11. Keterbatasan (sebutkan duluan sebelum ditanya)

1. Harga = snapshot dataset; sebagian mungkin harga paket, bukan tiket murni.
2. Sebaran data tidak merata (Banten hanya 2 destinasi; data Kaggle berpusat di 5 kota).
3. C4 dan tag hobi diambil dari teks deskripsi, bukan observasi lapangan.
4. Jarak garis lurus, bukan rute jalan.
5. Kuesioner bobot: 28 mahasiswa, tanpa skala 1–9, dan menyebut "biaya total" padahal C1 hanya harga tiket.
