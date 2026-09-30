"""Read-only validation of schema, source consistency and baseline deduplication."""

import ast
import csv
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def normalize(name):
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("gua", "goa"))


def main():
    baseline = rows(ROOT / "data/raw/tourism_with_id.csv")
    banten = rows(ROOT / "data/review/banten/banten_kaggle_review.csv")
    draft = rows(HERE / "jawa_kaggle_review.csv")
    manifest = json.loads((HERE / "provenance.json").read_text(encoding="utf-8"))
    assert draft[0] == baseline[0] == banten[0]
    assert len(draft) == 5 and all(len(row) == 13 for row in draft)
    existing = baseline[1:] + banten[1:]
    ids = {int(row[0]) for row in existing}
    names = {normalize(row[1]) for row in existing}
    categories = {row[3] for row in baseline[1:]}
    assert len({row[0] for row in draft[1:]}) == 4
    assert len({normalize(row[1]) for row in draft[1:]}) == 4
    by_id = {r["place_id"]: r for r in manifest["records"]}
    assert set(by_id) == {int(row[0]) for row in draft[1:]}
    for source in manifest["sources"].values():
        digest = hashlib.sha256((HERE / source["file"]).read_bytes()).hexdigest()
        assert digest.upper() == source["sha256"]
    for row in draft[1:]:
        record = by_id[int(row[0])]
        assert int(row[0]) not in ids and normalize(row[1]) not in names
        assert row[1] == record["place_name"] and row[3] == record["category"]
        assert row[4] == record["city"] and row[3] in categories
        assert int(row[5]) == record["price"]
        assert row[6:8] == ["", ""] and row[11:] == ["", ""]
        receipt = json.loads((HERE / record["location_receipt"]).read_text(encoding="utf-8"))
        match = next(r for r in receipt["results"] if r["osm_id"] == record["osm_id"]
                     and r["osm_type"] == record["osm_type"])
        assert record["city"].lower() in match["display_name"].lower()
        assert record["province"].lower() in match["display_name"].lower()
        snapshot = json.loads((HERE / record["osm_snapshot"]).read_text(encoding="utf-8"))
        assert "odbl" in snapshot["license"].lower()
        obj = next(e for e in snapshot["elements"] if e["type"] == record["osm_type"]
                   and e["id"] == record["osm_id"])
        if record["coordinate_method"] == "osm_node":
            lat, lon = obj["lat"], obj["lon"]
        else:
            nodes = {e["id"]: e for e in snapshot["elements"] if e["type"] == "node"}
            geometry = [nodes[n] for n in obj["nodes"]]
            lat = (min(n["lat"] for n in geometry) + max(n["lat"] for n in geometry)) / 2
            lon = (min(n["lon"] for n in geometry) + max(n["lon"] for n in geometry)) / 2
        coordinate = ast.literal_eval(row[8])
        assert set(coordinate) == {"lat", "lng"}
        assert coordinate == {"lat": float(row[9]), "lng": float(row[10])}
        assert abs(float(row[9]) - lat) < 1e-10
        assert abs(float(row[10]) - lon) < 1e-10
    # Geographic manual review additionally checked objects/aliases and rejected wrong points.
    print("PASS: 4 rows; exact 13-field Kaggle header; IDs/names disjoint from Kaggle+Banten;")
    print("tariff manifest/PDF hashes and source coordinates consistent; rating/duration blank.")
    print("Not a full-criteria approval or proof of current on-site tariffs/entrance coordinates.")


if __name__ == "__main__":
    main()
