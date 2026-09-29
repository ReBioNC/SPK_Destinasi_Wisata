"""Estimasi biaya perjalanan per orang (C1 = total biaya). Stdlib only.

Semua angka berasal dari `reports/audit_biaya.md`. Nilai bertanda
PROVISIONAL adalah asumsi terbuka yang wajib dikalibrasi observasi manual
sebelum sidang; fungsi ini murni (tanpa network) agar mudah diuji.
"""

# BBM Pertalite Rp10.000/L (Pertamina, stabil sejak 2022; catat tanggal bila berubah).
BBM_PERTALITE_RP_LITER = 10000
TANGGAL_BERLAKU_BBM = "2026-09-01"

# Tarif per km = BBM ÷ konsumsi, dibulatkan (lihat audit_biaya.md).
MODA = {
    "motor": {"tarif_per_km": 250, "parkir": 5000, "label": "Motor"},
    "mobil": {"tarif_per_km": 850, "parkir": 10000, "label": "Mobil"},
    "bus": {"tarif_per_km": 750, "parkir": 0, "label": "Bus"},
}

# Flat harian dari derivasi BPS Wisatawan Nusantara 2024 (lihat audit).
MAKAN_PER_HARI = 150000
INAP_PER_MALAM = 350000

# PROVISIONAL: tarif pesawat = base + rate × great-circle km, difit dari
# ±10 sampel Traveloka/Tiket.com (kolom diisi saat observasi manual).
PESAWAT_BASE = 400000  # PROVISIONAL
PESAWAT_RATE_PER_KM = 1200  # PROVISIONAL

# PROVISIONAL: tarif flat penyeberangan (tarif resmi ASDP + tanggal akses).
FERI = {
    "merak_bakauheni": 80000,  # PROVISIONAL
    "ketapang_gilimanuk": 60000,  # PROVISIONAL
}


def transport_pp(jarak_km, moda):
    """Biaya transport pulang-pergi darat."""
    try:
        tarif = MODA[moda]
    except KeyError:
        raise ValueError(f"Moda tak dikenal: {moda!r}. Pilih: {sorted(MODA)}")
    return 2 * jarak_km * tarif["tarif_per_km"] + tarif["parkir"]


def tarif_pesawat_pp(jarak_km):
    """Estimasi tiket pesawat PP (PROVISIONAL, lihat audit)."""
    return 2 * (PESAWAT_BASE + PESAWAT_RATE_PER_KM * jarak_km)


def estimasi_total(tiket, jarak_km, moda, hari, transport=None,
                   makan_per_hari=MAKAN_PER_HARI, inap_per_malam=INAP_PER_MALAM):
    """Rincian + total biaya per orang. `transport` menimpa hitungan darat
    (diisi tarif pesawat / feri saat mode antar-pulau)."""
    if hari < 1:
        raise ValueError("Durasi minimal 1 hari.")
    if transport is None:
        transport = transport_pp(jarak_km, moda)
    makan = hari * makan_per_hari
    inap = max(hari - 1, 0) * inap_per_malam
    return {"tiket": tiket, "transport": transport, "makan": makan,
            "inap": inap, "total": tiket + transport + makan + inap}
