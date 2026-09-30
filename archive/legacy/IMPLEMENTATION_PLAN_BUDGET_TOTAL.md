# IMPLEMENTATION PLAN — Budget Total Per-Orang + Moda Ganda (Darat/Udara/Feri)

**Status:** disetujui user (mode plan, 2026-09-29). **Belum dieksekusi.**
**Terkait:** `docs/superpowers/specs/2026-09-25-travelfit-django-design.md`,
`docs/superpowers/plans/2026-09-25-travelfit-django.md`

## 1. Goal

C1 berubah makna dari *harga tiket* menjadi *estimasi total biaya per orang*
(tiket + transport PP + makan + inap), dengan moda darat (OSRM), pesawat
(antar-pulau, tarif terkalibrasi observasi), dan feri (2 koridor tarif ASDP),
sesuai preferensi budget user. Jumlah kriteria tetap 6; AHP–TOPSIS tak berubah.

## 2. Arsitektur

- Modul baru `recommender/spk/biaya.py` — stdlib + `urllib` saja, tanpa
  dependensi baru. Fungsi murni untuk kalkulasi; I/O network terisolasi di
  `jarak_darat()`.
- Model baru `JarakCache(asal, tujuan, moda, jarak_km, sumber, updated_at)` —
  wajib untuk kepatuhan kebijakan OSRM (maks 1 req/detik, tanpa heavy use).
- Input form baru: `moda` (motor/mobil/bus), `hari` (default 1),
  `mode_antar_pulau` (termurah [default] / pesawat / darat_feri).
- Peta statis `PROVINSI_KE_PULAU` (38 provinsi → 7 gugus pulau).

## 3. Parameter & Sumber (wajib masuk `reports/audit_biaya.md`)

| Parameter | Nilai default | Sumber / kepercayaan |
|---|---|---|
| BBM Pertalite | Rp10.000/L + tanggal berlaku | Pertamina resmi — tinggi |
| Konsumsi motor/mobil/bus | 45 / 12 / 4 km/L | Umum — sedang (sensitivity ±20%) |
| Makan/hari, inap/malam | Derivasi BPS Wisatawan Nusantara 2024 (makan Rp443.340, akomodasi Rp488.590 per perjalanan ÷ lama perjalanan) | BPS — tinggi sbg acuan nasional |
| Jarak darat | OSRM `router.project-osrm.org`, User-Agent valid, cache + throttle | Sedang — demo server tanpa SLA |
| Fallback offline | Haversine × 1,3 + flag provenance | Rendah — terdokumentasi |
| Tarif pesawat | `base + rate_per_km × great-circle`, rate difit ±10 sampel Traveloka/Tiket.com + tanggal observasi | Sedang — observasi terdokumentasi |
| Feri Merak–Bakauheni, Ketapang–Gilimanuk | Tarif resmi ASDP + tanggal | Tinggi |
| Koordinat 4 pelabuhan | OpenStreetMap | Tinggi |

## 4. Aliran per Kandidat

1. Gugus pulau asal (via `PROVINSI_KOTA`) vs tujuan (via `PETA_PULAU`).
2. Sama → OSRM mobil (cache → API → fallback Haversine×1,3 + flag).
3. Beda → hitung pesawat; bila mode user Termurah/Darat+Feri DAN koridor
   tersedia → hitung feri (2 kaki OSRM + flat ASDP); mode Termurah ambil min.
4. `total = tiket + 2×transport + hari×makan + (hari−1)×inap`.
5. Filter budget atas **total**; TOPSIS seperti biasa.
6. Kartu hasil: rincian 4 komponen + sumber jarak + alasan moda
   ("dipilih karena termurah" / "pesawat (tanpa koridor feri)").

## 5. Task (TDD, 1 commit per task, branch non-main)

1. **Audit & konstanta** — tulis `reports/audit_biaya.md` (tabel di atas +
   ±10 sampel fare + tanggal); buat `spk/biaya.py` (konstanta +
   `estimasi_total()` murni). Test: angka manual per komponen.
2. **Pulau & cache** — `PETA_PULAU` 38 entri + model `JarakCache` + migrasi.
   Test: semua provinsi terpetakan 7 gugus; CRUD cache.
3. **OSRM client** — `jarak_darat()` (cache → throttle → API → fallback +
   flag sumber). Test: mock respons OK, HTTP 429, offline total.
4. **Pesawat & feri** — `tarif_pesawat()` + `opsi_feri()` + logika min.
   Test: NoRoute tak crash; non-koridor (mis. Makassar) langsung pesawat +
   pesan; Termurah memilih min dari dua opsi.
5. **Form & view** — field moda/hari/mode-antar-pulau + integrasi C1 +
   rincian kartu + AJAX JSON. Test POST tiap mode + fallback pesan.
6. **Spreadsheet & docs** — perluas `Perhitungan_SPK_TravelFit.xlsx`
   (kolom transport/makan/inap/total, C1 baru, Hasil ulang) + README +
   catatan Bab 2/3 laporan.
7. **Validasi akhir** — sensitivity ±20% tiap tarif (Spearman Top-10);
   kasus tiket-gratis-jauh vs tiket-mahal-dekat membalik ranking vs model
   lama; full suite hijau.

## 6. Risiko & Batasan Jujur

- OSRM rate-limit/tanpa SLA → ditutup cache + throttle + fallback.
- Estimasi ≠ presisi → label "±" di UI + paragraf limitasi di laporan.
- Bobot C1 warisan (dielisitasi untuk "harga tiket") → paragraf justifikasi
  + uji stabilitas, atau elisitasi ulang bila penguji meminta.
- Tol dikeluarkan dari v1 (tarif spesifik-rute belum terverifikasi).

## 7. Kriteria Selesai

User memilih moda/hari/mode-antar-pulau → Top-10 + rincian 4 komponen +
sumber jarak tampil; offline / antar-pulau / NoRoute jalan tanpa crash;
semua validasi (§5 task 7) lolos.
