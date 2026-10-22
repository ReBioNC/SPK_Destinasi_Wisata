"""Rekap anonim kuesioner bobot kriteria menjadi jumlah pilihan per pasangan.

Pemakaian:
    .venv/Scripts/python.exe scripts/rekap_kuesioner.py "<Responses>.xlsx"

Hanya jumlah pilihan yang ditulis; nama, email, prodi, usia dan waktu
pengisian tidak disalin. Jangan menyimpan file respons mentah di repository.
"""

import argparse
import csv
import re
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/survey/kuesioner_bobot_rekap.csv"
# Awalan jawaban pada Google Form -> indeks kriteria C1..C6.
PREFIXES = ["Biaya", "Rating", "Jarak", "Fasilitas", "Kesesuaian Kategori", "Kesesuaian Hobi"]


def criterion(text):
    text = str(text).strip()
    for index, prefix in enumerate(PREFIXES):
        if text.startswith(prefix):
            return index
    raise ValueError(f"Jawaban tidak dikenal: {text!r}")


def tally(path):
    rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True))
    header, answers = rows[0], [row for row in rows[1:] if any(cell not in (None, "") for cell in row)]
    pairs = []
    for column, title in enumerate(header):
        match = re.search(r"\((.+) dengan (.+)\)", str(title or ""))
        if match:
            pairs.append((column, criterion(match.group(1)), criterion(match.group(2))))
    if len(pairs) != 15:
        raise ValueError(f"Harus ada 15 pasangan kriteria, ditemukan {len(pairs)}.")
    result = []
    for column, i, j in pairs:
        chosen = [criterion(row[column]) for row in answers]
        if any(c not in (i, j) for c in chosen):
            raise ValueError(f"Jawaban di luar pasangan C{i + 1}–C{j + 1}.")
        result.append((i, j, chosen.count(i), chosen.count(j), len(answers)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("responses", type=Path)
    args = parser.parse_args()
    rows = tally(args.responses)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["kriteria_i", "kriteria_j", "pilih_i", "pilih_j", "responden"])
        writer.writerows([f"C{i + 1}", f"C{j + 1}", a, b, n] for i, j, a, b, n in rows)
    print(f"{rows[0][4]} responden, 15 pasangan -> {OUTPUT}")


if __name__ == "__main__":
    main()
