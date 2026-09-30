"""Read-only checks: merged rows must equal the two source CSVs exactly."""

import ast
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
ROOT = HERE.parents[2]


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def main():
    banten = read(REVIEW / "banten/banten_kaggle_review.csv")
    jawa = read(REVIEW / "jawa_tambahan/jawa_kaggle_review.csv")
    merged = read(HERE / "destinasi_jawa_review.csv")
    baseline = read(ROOT / "data/raw/tourism_with_id.csv")
    assert merged[0] == banten[0] == jawa[0] == baseline[0]
    assert merged[1:] == banten[1:] + jawa[1:], "Merged values differ from sources"
    assert len(merged) == 7 and all(len(row) == 13 for row in merged)
    ids = [int(row[0]) for row in merged[1:]]
    assert ids == list(range(438, 444)) and len(set(ids)) == 6
    assert len({row[1].casefold() for row in merged[1:]}) == 6
    assert not set(ids).intersection(int(row[0]) for row in baseline[1:])
    for row in merged[1:]:
        assert row[6:8] == ["", ""] and row[11:] == ["", ""]
        assert ast.literal_eval(row[8]) == {"lat": float(row[9]), "lng": float(row[10])}
    print("PASS: 6 rows = 2 Banten + 4 additional Java; exact source values and Kaggle header.")
    print("Unique IDs/names; no Kaggle ID collision; missing fields preserved.")


if __name__ == "__main__":
    main()
