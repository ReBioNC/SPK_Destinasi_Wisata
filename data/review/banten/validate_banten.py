"""Read-only structural and source-consistency checks for the Banten draft."""

import ast
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def main():
    baseline = read_csv(ROOT / "data/raw/tourism_with_id.csv")
    draft = read_csv(HERE / "banten_kaggle_review.csv")
    assert draft[0] == baseline[0], "Header differs from original Kaggle"
    assert len(draft) == 3, "Expected two destinations"
    assert all(len(row) == 13 for row in draft), "Wrong number of fields"
    original_ids = {int(row[0]) for row in baseline[1:]}
    categories = {row[3] for row in baseline[1:]}
    new_ids = [int(row[0]) for row in draft[1:]]
    assert len(set(new_ids)) == 2 and not (set(new_ids) & original_ids)

    tahura = json.loads((HERE / "sources/osm_balai_tahura.json").read_text())
    node = next(e for e in tahura["elements"] if e["id"] == 6728713222)
    museum = json.loads((HERE / "sources/osm_multatuli_full.json").read_text())
    way = next(e for e in museum["elements"] if e["type"] == "way")
    assert way["id"] == 1050591125 and way["tags"]["name"] == "Museum Multatuli"
    nodes = {e["id"]: e for e in museum["elements"] if e["type"] == "node"}
    latitudes = [nodes[n]["lat"] for n in way["nodes"]]
    longitudes = [nodes[n]["lon"] for n in way["nodes"]]
    expected = {
        438: (8000, node["lat"], node["lon"]),
        439: (2000, (min(latitudes) + max(latitudes)) / 2,
              (min(longitudes) + max(longitudes)) / 2),
    }
    for row in draft[1:]:
        price, latitude, longitude = expected[int(row[0])]
        assert row[3] in categories
        assert int(row[5]) == price, "Price differs from curated legal tariff"
        assert row[6:8] == ["", ""], "Do not invent ratings or duration"
        assert row[11:] == ["", ""]
        coordinate = ast.literal_eval(row[8])
        assert set(coordinate) == {"lat", "lng"}
        assert coordinate["lat"] == float(row[9])
        assert coordinate["lng"] == float(row[10])
        assert abs(float(row[9]) - latitude) < 1e-10
        assert abs(float(row[10]) - longitude) < 1e-10
    print("PASS: 2 review rows; exact Kaggle header; source-consistent coordinates;")
    print("IDs disjoint from Kaggle; tariff values checked; missing attributes preserved.")
    print("Not a full-criteria approval or verification of current on-site operations.")


if __name__ == "__main__":
    main()
