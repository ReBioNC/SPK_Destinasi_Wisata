"""Kota/kabupaten Indonesia + koordinat — dimuat dari data/kota_indonesia.csv.

KOTA_ASAL: nama -> (lat, lon). PROVINSI_KOTA: nama -> provinsi.
Sumber kredibel tiap baris tercantum di kolom `sumber` pada CSV
(Kemendagri, BPS, BIG; koordinat pendekatan registry internal).
"""

import csv
from pathlib import Path

_CSV = Path(__file__).resolve().parent.parent / "data" / "kota_indonesia.csv"


def _load():
    kota, prov = {}, {}
    with open(_CSV, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            kota[row["nama"]] = (float(row["lat"]), float(row["lon"]))
            prov[row["nama"]] = row["provinsi"]
    return kota, prov


KOTA_ASAL, PROVINSI_KOTA = _load()
