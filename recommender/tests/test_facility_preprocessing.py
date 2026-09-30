"""Run the real notebook facility cell against hand-reviewed source descriptions."""

import json
from pathlib import Path
import re
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def extract_facilities(frame):
    notebook = json.loads((ROOT / "notebooks/01_preprocessing_travelfit.ipynb").read_text(encoding="utf-8"))
    source = next("".join(cell["source"]) for cell in notebook["cells"]
                  if cell["cell_type"] == "code" and "FACILITY_KEYWORDS =" in "".join(cell["source"]))
    scope = {"pd": pd, "re": re, "destinations": frame.copy()}
    exec(compile(source, "notebook_facilities", "exec"), scope)
    return scope["destinations"]


class FacilityPreprocessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        frame = pd.read_csv(ROOT / "data/raw/tourism_with_id.csv").rename(columns={
            "Place_Id": "place_id", "Place_Name": "place_name", "Description": "description",
        })
        frame["category_clean"] = ""
        cls.source = frame
        cls.actual = extract_facilities(frame).set_index("place_id")

    def test_known_context_false_positives_are_not_scored(self):
        # All expectations are from reading the source descriptions, not the extractor.
        rejected = {
            18: ["worship"], 57: ["worship"], 94: ["worship"],
            115: ["worship"], 149: ["worship"],
            176: ["parking", "information_center"],
            213: ["worship"], 232: ["food"], 249: ["toilet"],
            254: ["food"], 270: ["food"], 295: ["food"],
            298: ["food"], 347: ["parking"], 353: ["worship"],
        }
        for place_id, facilities in rejected.items():
            for facility in facilities:
                with self.subTest(place_id=place_id, facility=facility):
                    self.assertEqual(self.actual.loc[place_id, f"facility_{facility}_mentioned"], 0)

    def test_parkiran_is_recognized_as_parking(self):
        self.assertEqual(self.actual.loc[79, "facility_parking_mentioned"], 1)
        self.assertAlmostEqual(self.actual.loc[79, "c4_facility_score"], 2 / 6)

    def test_explicit_domes_facilities_are_preserved(self):
        for facility in ("toilet", "parking", "food", "worship"):
            self.assertEqual(self.actual.loc[145, f"facility_{facility}_mentioned"], 1)
        self.assertAlmostEqual(self.actual.loc[145, "c4_facility_score"], 4 / 6)

    def test_explicit_accessibility_is_preserved(self):
        self.assertEqual(self.actual.loc[394, "facility_accessibility_mentioned"], 1)
        self.assertEqual(self.actual.loc[394, "facility_food_mentioned"], 1)

    def test_additional_beach_coordinate_disclaimer_is_not_parking_evidence(self):
        frame = pd.read_csv(ROOT / "data/review/gabungan_jawa/destinasi_jawa_review.csv").rename(columns={
            "Place_Id": "place_id", "Place_Name": "place_name", "Description": "description",
        })
        frame["category_clean"] = ""
        actual = extract_facilities(frame).set_index("place_id")
        self.assertEqual(actual.loc[441, "facility_parking_mentioned"], 0)

    def test_review_does_not_change_source_descriptions(self):
        self.assertEqual(self.actual.loc[298, "description"], self.source.set_index("place_id").loc[298, "description"])

    def test_unrelated_destination_is_not_changed_by_id_only_override(self):
        # An ID may be reused in other datasets: corrections must also match the source phrase.
        frame = pd.DataFrame([{"place_id": 298, "place_name": "Other place", "description": "Tersedia warung makan.", "category_clean": ""}])
        actual = extract_facilities(frame).iloc[0]
        self.assertEqual(actual["facility_food_mentioned"], 1)


if __name__ == "__main__":
    unittest.main()
