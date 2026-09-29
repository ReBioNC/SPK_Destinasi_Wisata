"""Perencana transport per kandidat: darat / pesawat / feri (termurah opsional).

Memakai `jarak.jarak_darat` (cache+OSRM+fallback) untuk kaki darat dan
`biaya` untuk tarif. Tak pernah melempar karena network; ValueError hanya
untuk input tak valid (provinsi/moda/mode tak dikenal).
"""

from recommender.jarak import jarak_darat
from recommender.spk import biaya, geo
from recommender.spk.biaya import FERI, PELABUHAN, PETA_PULAU

MODE_ANTAR = (
    ("termurah", "Termurah — sistem bandingkan pesawat vs feri"),
    ("pesawat", "Pesawat saja"),
    ("darat_feri", "Darat + feri saja"),
)
MODE_VALID = tuple(k for k, _ in MODE_ANTAR)


def _koridor(g1, prov1, g2, prov2):
    """(kunci_feri, pelabuhan_asal, pelabuhan_tujuan) atau None."""
    if {g1, g2} == {"Jawa", "Sumatera"}:
        asal = "merak" if g1 == "Jawa" else "bakauheni"
        tujuan = "bakauheni" if g1 == "Jawa" else "merak"
        return "merak_bakauheni", asal, tujuan
    if g1 == "Jawa" and prov2 == "Bali":
        return "ketapang_gilimanuk", "ketapang", "gilimanuk"
    if prov1 == "Bali" and g2 == "Jawa":
        return "ketapang_gilimanuk", "gilimanuk", "ketapang"
    return None


def koridor_ports(prov_asal, prov_tujuan):
    """Publik untuk pra-pemanasan cache: koridor antar dua provinsi.

    ValueError bila provinsi tak dikenal (konsisten dengan rencanakan)."""
    try:
        g1, g2 = PETA_PULAU[prov_asal], PETA_PULAU[prov_tujuan]
    except KeyError as exc:
        raise ValueError(f"Provinsi tak dikenal: {exc}.")
    return _koridor(g1, prov_asal, g2, prov_tujuan)


def rencanakan(lat1, lon1, prov1, lat2, lon2, prov2, moda="mobil", mode="termurah"):
    """Dict {transport, cara, rincian, sumber_jarak, opsi}.

    transport = biaya transport PP per orang. cara salah satu dari
    "darat"/"pesawat"/"feri". opsi = perbandingan angka bila dibanding.
    """
    if moda not in biaya.MODA:
        raise ValueError(f"Moda tak dikenal: {moda!r}.")
    if mode not in MODE_VALID:
        raise ValueError(f"Mode tak dikenal: {mode!r}.")
    try:
        g1, g2 = PETA_PULAU[prov1], PETA_PULAU[prov2]
    except KeyError as exc:
        raise ValueError(f"Provinsi tak dikenal: {exc}.")
    if g1 == g2:
        km, sumber = jarak_darat(lat1, lon1, lat2, lon2, moda)
        return {"transport": biaya.transport_pp(km, moda), "cara": "darat",
                "rincian": f"Darat {km:.0f} km ({sumber}).",
                "sumber_jarak": sumber, "opsi": None, "jarak_km": km}

    gc = geo.haversine(lat1, lon1, lat2, lon2)
    tarif_pesawat = biaya.tarif_pesawat_pp(gc)
    koridor = _koridor(g1, prov1, g2, prov2)
    tarif_feri, ket_feri = None, None
    if koridor is not None:
        kunci, pa, pt = koridor
        km_a, _ = jarak_darat(lat1, lon1, *PELABUHAN[pa], moda)
        km_b, _ = jarak_darat(*PELABUHAN[pt], lat2, lon2, moda)
        tarif_feri = 2 * FERI[kunci] + biaya.transport_pp(km_a + km_b, moda)
        ket_feri = {"koridor": kunci, "tarif": tarif_feri}

    if mode == "pesawat" or (mode == "darat_feri" and ket_feri is None):
        rincian = f"Pesawat ± Rp{tarif_pesawat:,.0f} PP."
        if mode == "darat_feri":
            rincian += " (tanpa koridor feri ke tujuan.)"
        return {"transport": tarif_pesawat, "cara": "pesawat", "rincian": rincian,
                "sumber_jarak": "estimasi-pesawat", "jarak_km": gc,
                "opsi": {"pesawat": tarif_pesawat,
                         "feri": tarif_feri} if ket_feri else None}
    if mode == "darat_feri":
        return {"transport": tarif_feri, "cara": "feri",
                "rincian": f"Feri {ket_feri['koridor']} + darat.",
                "sumber_jarak": "estimasi-feri", "jarak_km": km_a + km_b,
                "opsi": {"pesawat": tarif_pesawat, "feri": tarif_feri}}
    # mode == "termurah"
    if ket_feri is not None and tarif_feri < tarif_pesawat:
        return {"transport": tarif_feri, "cara": "feri",
                "rincian": (f"Dipilih feri (Rp{tarif_feri:,.0f}) karena termurah "
                            f"dibanding pesawat (Rp{tarif_pesawat:,.0f})."),
                "sumber_jarak": "estimasi-feri", "jarak_km": km_a + km_b,
                "opsi": {"pesawat": tarif_pesawat, "feri": tarif_feri}}
    alasan = "" if ket_feri is None else " (feri tersedia namun lebih mahal)"
    return {"transport": tarif_pesawat, "cara": "pesawat",
            "rincian": f"Dipilih pesawat (Rp{tarif_pesawat:,.0f}).{alasan}",
            "sumber_jarak": "estimasi-pesawat", "jarak_km": gc,
            "opsi": {"pesawat": tarif_pesawat, "feri": tarif_feri}
            if ket_feri else None}
