"""Pemeriksaan read-only kandidat tambahan November 2026.

Jalankan dari root repo: python data/review/tambahan_jawa_2026_11/validate.py
Lolos bukan berarti kandidat siap diimpor; lihat Dokumentasi.md.
"""

import ast
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CATEGORIES = {"Budaya", "Taman Hiburan", "Cagar Alam", "Bahari", "Tempat Ibadah", "Pusat Perbelanjaan"}


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def norm(name):
    return re.sub(r"\s+", " ", re.sub(r"\bgua\b", "goa", name.casefold())).strip()


def snapshot_point(path, osm_type, osm_id):
    data = json.loads((HERE / path).read_text(encoding="utf-8"))
    for item in data.get("results", []):
        if item["osm_type"] == osm_type and item["osm_id"] == osm_id:
            return float(item["lat"]), float(item["lon"])
    for item in data.get("elements", []):
        if item["type"] == osm_type and item["id"] == osm_id:
            point = item.get("center", item)
            return float(point["lat"]), float(point["lon"])
    raise AssertionError(f"OSM {osm_type}/{osm_id} tidak ada di {path}")


def main():
    rows = read(HERE / "kandidat_kaggle_review.csv")
    baseline = read(ROOT / "data/raw/tourism_with_id.csv")
    existing = read(ROOT / "data/review/gabungan_jawa/destinasi_jawa_review.csv")
    provenance = json.loads((HERE / "provenance.json").read_text(encoding="utf-8"))
    receipt = json.loads((HERE / "google_maps_rating_review.json").read_text(encoding="utf-8"))

    assert rows[0] == baseline[0], "Header harus sama persis dengan CSV Kaggle"
    data = rows[1:]
    assert all(len(row) == 13 for row in data)
    ids = [int(row[0]) for row in data]
    assert ids == list(range(444, 444 + len(data))), "ID lokal harus berurutan mulai 444"
    known = {norm(row[1]) for row in baseline[1:] + existing[1:]}
    names = [norm(row[1]) for row in data]
    assert len(set(names)) == len(names) and not known.intersection(names), "Nama bentrok dengan 443 destinasi"

    records = {r["place_id"]: r for r in provenance["records"]}
    assert set(records) == set(ids)
    for row in data:
        pid, record = int(row[0]), records[int(row[0])]
        assert row[3] in CATEGORIES and row[3] == record["category"]
        assert int(row[5]) == record["price"] > 0
        assert row[6:8] == ["", ""] and row[11:] == ["", ""], "Rating/Time_Minutes tetap kosong di CSV"
        lat, lon = float(row[9]), float(row[10])
        assert ast.literal_eval(row[8]) == {"lat": lat, "lng": lon}
        assert (lat, lon) == (record["latitude"], record["longitude"])
        assert -9 < lat < -5.5 and 105 < lon < 115, f"{pid} di luar Pulau Jawa"
        assert snapshot_point(record["location_snapshot"], record["osm_type"], record["osm_id"]) == (lat, lon)
        source = provenance["sources"][record["price_source"]]
        evidence = source["evidence_png"]
        for png in evidence if isinstance(evidence, list) else [evidence]:
            assert (HERE / png).is_file(), png
        assert len(source["sha256"]) == 64

    ratings = {r["place_id"]: r for r in receipt["records"]}
    assert set(ratings) == set(ids)
    for record in ratings.values():
        if record["integration_allowed"]:
            assert record["match_status"] == "matched_name_location"
            assert 1 <= record["rating_observed"] <= 5 and record["review_count_observed"] > 0
    allowed = sum(r["integration_allowed"] for r in ratings.values())
    print(f"PASS: {len(data)} kandidat, ID {ids[0]}-{ids[-1]}, header Kaggle, tanpa bentrok nama dengan 443 destinasi.")
    print(f"Tarif, bukti halaman dan titik OSM cocok; {allowed} rating cocok nama-lokasi, {len(data) - allowed} perlu keputusan.")


if __name__ == "__main__":
    main()
