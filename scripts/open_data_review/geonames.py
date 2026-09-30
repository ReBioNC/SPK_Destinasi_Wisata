"""GeoNames Indonesia gazetteer candidates (CC BY 4.0), not ticketed attractions.

Source: https://download.geonames.org/export/dump/ID.zip
Schema/license: https://download.geonames.org/export/dump/readme.txt
"""

import math
import hashlib
import json
from datetime import date
from pathlib import Path
from zipfile import ZipFile

from .schema import Candidate


# These codes identify physical landmarks or visitor-oriented facilities.
# They do NOT by themselves prove that a place is open for tourism.
LANDMARK_CATEGORIES = {
    "T.BCH": "Pantai", "T.BCHS": "Pantai", "T.VLC": "Gunung",
    "T.CRTR": "Cagar Alam",
    "H.FLLS": "Cagar Alam", "H.FLL": "Cagar Alam", "H.LK": "Cagar Alam",
    "L.PRK": "Cagar Alam", "L.RESN": "Cagar Alam",
    "S.MUS": "Budaya", "S.MNMT": "Budaya", "S.PAL": "Budaya",
    "S.RUIN": "Budaya", "S.ZOO": "Taman Hiburan", "S.RSRT": "Taman Hiburan",
    "S.OBPT": "Cagar Alam", "S.TMPL": "Tempat Ibadah",
}


def parse_geonames_rows(lines) -> list[Candidate]:
    """Filter named Indonesian landmarks and resolve region names from ADM rows."""
    records = []
    admin1, admin2 = {}, {}
    for line in lines:
        fields = line.rstrip("\r\n").split("\t")
        if len(fields) < 19 or fields[8] != "ID":
            continue
        records.append(fields)
        if fields[6] == "A" and fields[7] == "ADM1" and fields[10]:
            admin1[fields[10]] = fields[1]
        if fields[6] == "A" and fields[7] == "ADM2" and fields[10] and fields[11]:
            admin2[(fields[10], fields[11])] = fields[1]
    candidates = []
    for f in records:
        feature = f"{f[6]}.{f[7]}"
        if feature not in LANDMARK_CATEGORIES or not f[1].strip():
            continue
        try:
            lat, lon = float(f[4]), float(f[5])
        except ValueError:
            continue
        if not (math.isfinite(lat) and math.isfinite(lon) and -12 <= lat <= 7 and 94 <= lon <= 142):
            continue
        candidates.append(Candidate(
            candidate_id=f"geonames:{f[0]}", origin="geonames", name=f[1].strip(),
            city=admin2.get((f[10], f[11]), ""), province=admin1.get(f[10], ""),
            source_row_id=f[0], source_path=f"https://www.geonames.org/{f[0]}/",
            raw={"feature_class": f[6], "feature_code": f[7],
                 "category_mapped": LANDMARK_CATEGORIES[feature],
                 "admin1_code": f[10], "admin2_code": f[11], "modified_at": f[18]},
            lat=lat, lon=lon, geometry_origin="gazetteer_point_unverified",
        ))
    return candidates


def load_geonames_zip(path: Path) -> list[Candidate]:
    """Read only ID.txt inside the official country ZIP, with no file extraction."""
    with ZipFile(path) as archive:
        with archive.open("ID.txt") as member:
            return parse_geonames_rows((line.decode("utf-8") for line in member))


def read_geonames_receipt(path: Path) -> dict:
    """Validate stable retrieval metadata against the exact archive bytes."""
    path = Path(path)
    receipt = json.loads(path.with_suffix(".source.json").read_text(encoding="utf-8"))
    if receipt.get("source_url") != "https://download.geonames.org/export/dump/ID.zip":
        raise ValueError("Unexpected GeoNames source URL")
    date.fromisoformat(receipt["retrieved_at"])
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != receipt.get("sha256"):
        raise ValueError("GeoNames archive does not match source receipt")
    return receipt
