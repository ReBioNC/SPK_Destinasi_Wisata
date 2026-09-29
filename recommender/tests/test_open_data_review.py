"""Regression tests for the isolated, review-only open-data pipeline."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import pandas as pd

from scripts.open_data_review.legacy import load_legacy_candidates


ROOT = Path(__file__).resolve().parents[2]


class LegacyInventoryTests(TestCase):
    def test_actual_sources_are_inventoried_without_implicit_verification(self):
        rows = load_legacy_candidates(
            ROOT / "Dataset_Wisata_38_Provinsi.xlsx",
            ROOT / "data/raw/tourism_with_id.csv",
        )
        self.assertEqual(len(rows), 2337)
        self.assertEqual(sum(row.origin == "synthetic_1900" for row in rows), 1900)
        self.assertEqual(sum(row.origin == "kaggle_437" for row in rows), 437)
        self.assertEqual(len({row.candidate_id for row in rows}), 2337)
        generated = rows[0]
        self.assertEqual(generated.source_row_id, "1")
        self.assertIn("Price", generated.untrusted_fields)
        self.assertIn("Lat", generated.untrusted_fields)
        self.assertIn("Description", generated.untrusted_fields)
        self.assertIn("Price", rows[1900].untrusted_fields)
        self.assertTrue(generated.source_path.endswith("Dataset_Wisata_38_Provinsi.xlsx"))

    def test_same_name_different_provinces_remains_distinct(self):
        with TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            xlsx = base / "old.xlsx"
            csv = base / "kaggle.csv"
            pd.DataFrame([
                {"Place_Id": 1, "Place_Name": "Pantai Indah", "City": "A", "Province": "Aceh"},
                {"Place_Id": 2, "Place_Name": "Pantai Indah", "City": "B", "Province": "Bali"},
                {"Place_Id": 3, "Place_Name": "Pantai C A 1", "City": "C", "Province": "Aceh"},
            ]).to_excel(xlsx, index=False)
            pd.DataFrame(columns=["Place_Id", "Place_Name"]).to_csv(csv, index=False)
            rows = load_legacy_candidates(xlsx, csv)
            self.assertNotEqual(rows[0].candidate_id, rows[1].candidate_id)
            self.assertFalse(rows[0].possible_filler_name)
            self.assertTrue(rows[2].possible_filler_name)
