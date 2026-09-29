# Audit Parameter Biaya (C1 = Estimasi Total per Orang)

> Setiap angka di `recommender/spk/biaya.py` harus terlacak ke baris tabel ini.
> Kolom *Tanggal* wajib diisi saat nilai diambil/diubah. Nilai PROVISIONAL
> wajib dikalibrasi sebelum sidang.

## Parameter dan sumber

| Parameter | Nilai | Sumber | Tanggal akses | Kepercayaan |
|---|---|---|---|---|
| BBM Pertalite | Rp10.000/L | Pertamina Patra Niaga (siaran resmi) | 2026-09-01 | Tinggi (subsidi, stabil) |
| Konsumsi motor/mobil/bus | 45 / 12 / 4 km/L | Spesifikasi umum | 2026-09-29 | Sedang (rentang) |
| Makan/hari Rp150.000 | Flat awal | Derivasi BPS Wisatawan Nusantara 2024 (makan Rp443.340/trip) | 2026-09-29 | Sedang |
| Inap/malam Rp350.000 | Flat awal | Derivasi BPS Wisatawan Nusantara 2024 (akomodasi Rp488.590/trip) | 2026-09-29 | Sedang |
| Jarak darat | OSRM `router.project-osrm.org` (1 req/detik, User-Agent valid) | OpenStreetMap/FOSSGIS | — | Sedang (tanpa SLA) |
| Fallback offline | Haversine × 1,3 | Praktik umum | — | Rendah–Sedang |
| Pesawat base Rp400.000 + Rp1.200/km | PROVISIONAL | Observasi manual (di bawah) | — | Rendah → kalibrasi |
| Feri Merak–Bakauheni Rp80.000 | PROVISIONAL | Tarif resmi ASDP | — | Tinggi setelah diisi tanggal |
| Feri Ketapang–Gilimanuk Rp60.000 | PROVISIONAL | Tarif resmi ASDP | — | Tinggi setelah diisi tanggal |
| Koordinat 4 pelabuhan | OpenStreetMap | — | — | Tinggi setelah dicatat |

## Sampel tarif pesawat observasi (diisi manual)

| No | Rute | Maskapai | Harga sekali jalan (Rp) | Tanggal observasi | Sumber |
|---|---|---|---|---|---|
| 1 | CGK–DPS | — | — | — | Traveloka |
| 2 | CGK–SUB | — | — | — | Traveloka |
| 3 | BDO–UPG | — | — | — | Tiket.com |
| 4 | CGK–LOP | — | — | — | Traveloka |
| 5 | SUB–DPS | — | — | — | Tiket.com |
| 6 | CGK–YIA | — | — | — | Traveloka |
| 7 | CGK–KNO | — | — | — | Traveloka |
| 8 | BDO–DPS | — | — | — | Tiket.com |
| 9 | SRG–UPG | — | — | — | Traveloka |
| 10 | CGK–BPN | — | — | — | Traveloka |

Cara fit: regresi linear `harga = base + rate × jarak_great_circle_km`
dari sampel di atas; tulis base/rate hasil fit ke `biaya.py` + tanggal fit.
