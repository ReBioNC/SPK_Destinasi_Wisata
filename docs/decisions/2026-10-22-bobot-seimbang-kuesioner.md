# Bobot profil Seimbang dari kuesioner — 22 Oktober 2026

## Keputusan

Matriks AHP profil **Seimbang** diganti dengan agregasi kuesioner perbandingan
berpasangan. Nama, kunci (`seimbang`) dan posisinya sebagai profil default tetap.
Hemat, Kualitas dan Petualang tetap preset rancangan pengembang.

## Data

- Google Form, 28 responden (mahasiswa, mayoritas usia 18–21), 15 pasangan C1–C6,
  tidak ada jawaban kosong.
- Responden hanya memilih kriteria yang lebih penting; tidak ada skala intensitas 1–9.
- Rekap anonim: `data/survey/kuesioner_bobot_rekap.csv`, dibuat dengan
  `scripts/rekap_kuesioner.py`. File respons mentah berisi nama dan email, sehingga
  **tidak** disimpan di repository.

## Metode

Untuk pasangan (i, j): `a_ij = n_i / n_j`, dengan `n_i` jumlah responden yang memilih
C_i. Nilai ini sama dengan `p / (1 − p)` dan dibatasi pada skala Saaty 1/9 sampai 9
(pada data ini rasio terbesar 22/6 ≈ 3,67, jadi batas tidak terpakai).
Bobot tetap dihitung dengan normalisasi kolom dan rata-rata baris.

| Kriteria | Lama (preset) | Baru (kuesioner) |
| --- | --- | --- |
| C1 Harga tiket | 26,93% | 16,13% |
| C2 Rating | 17,85% | 13,51% |
| C3 Jarak | 15,67% | 7,90% |
| C4 Fasilitas | 8,20% | 13,23% |
| C5 Kategori | 15,67% | 26,04% |
| C6 Hobi | 15,67% | 23,19% |
| CR | 0,008418 | 0,060147 |

Alternatif yang ditolak: memetakan proporsi secara linear ke skala 1–9 (CR 0,118,
tidak konsisten) dan intensitas tetap 2 atau 3 per responden dengan rata-rata
geometrik (konsisten, tetapi intensitasnya asumsi bebas dan bobot menjadi hampir rata).
CR per responden tidak dihitung: 17 dari 28 responden memiliki pilihan siklik
(A > B, B > C, C > A), yang wajar pada jawaban biner.

## Batasan

- Kuesioner menyebut "biaya total (tiket, transportasi, makan, penginapan)" dan
  "jarak tempuh", sedangkan C1 hanya harga tiket dan C3 jarak garis lurus.
- Contoh kategori pada kuesioner menyebut kuliner, yang bukan kategori dataset.
- Sampel kecil dan homogen; bobot mewakili responden, bukan seluruh wisatawan.

## Dampak

Peringkat profil Seimbang berubah. `Perhitungan_SPK_TravelFit.xlsx`,
Excel `outputs/excel_spk_20261005/` dan laporan UTS masih memakai bobot lama;
perbarui dokumen tersebut sebelum dipakai sebagai bukti terbaru. Fixture
`W_SEIMBANG` pada `test_spk.py` tetap bobot lama karena menguji contoh spreadsheet,
bukan profil aktif.
