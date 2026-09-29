"""Regression tests for the isolated, review-only open-data pipeline."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import pandas as pd

from scripts.open_data_review.legacy import load_legacy_candidates
from scripts.open_data_review.osm import parse_osm_snapshot, INDONESIA_QUERY
from scripts.open_data_review.schema import OsmPoint
from scripts.open_data_review.services import nearby_service_evidence, service_score, _haversine_km
from scripts.open_data_review.schema import Candidate, SourceEvidence
from scripts.open_data_review.evidence import review_candidate, deduplicate_candidates


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


class OsmSnapshotTests(TestCase):
    def test_parse_named_attraction_and_service_with_geometry_provenance(self):
        payload = {"elements": [
            {"type": "node", "id": 11, "lat": -6.2, "lon": 106.8,
             "tags": {"name": "Museum A", "tourism": "museum"}},
            {"type": "way", "id": 12, "center": {"lat": -6.3, "lon": 106.9},
             "tags": {"name": "Pantai B", "natural": "beach"}},
            {"type": "relation", "id": 13, "center": {"lat": -6.4, "lon": 107.0},
             "tags": {"name": "Hotel C", "tourism": "hotel"}},
            {"type": "node", "id": 14, "lat": -6.5, "lon": 107.1,
             "tags": {"tourism": "attraction"}},
            {"type": "node", "id": 11, "lat": -6.2, "lon": 106.8,
             "tags": {"name": "Museum A", "tourism": "museum"}},
        ]}
        candidates, points = parse_osm_snapshot(payload, "2026-09-29", INDONESIA_QUERY)
        self.assertEqual([row.name for row in candidates], ["Museum A", "Pantai B"])
        self.assertEqual(len(points), 4)
        self.assertEqual(candidates[0].candidate_id, "osm:node/11")
        self.assertEqual(candidates[1].geometry_origin, "center_unverified")
        self.assertEqual(points[2].ref, "relation/13")

    def test_missing_indonesia_boundary_query_is_refused(self):
        with self.assertRaises(ValueError):
            parse_osm_snapshot({"elements": []}, "2026-09-29", "node[tourism];out;")


class ServiceScoreTests(TestCase):
    def point(self, ident, lon, tags):
        return OsmPoint("node", ident, 0.0, lon, tags, "node", "2026-09-29")

    def test_zero_multiple_and_all_four_categories(self):
        self.assertEqual(service_score(nearby_service_evidence(0, 0, [])), 0)
        points = [
            self.point(1, 0, {"highway": "bus_stop"}),
            self.point(2, 0, {"public_transport": "platform"}),
            self.point(3, 0, {"amenity": "hospital"}),
            self.point(4, 0, {"amenity": "atm"}),
            self.point(5, 0, {"tourism": "hotel"}),
            self.point(5, 0, {"tourism": "hotel"}),
        ]
        evidence = nearby_service_evidence(0, 0, points)
        self.assertEqual(service_score(evidence), 4)
        self.assertEqual(len(evidence["transport"]), 2)
        self.assertEqual(evidence["lodging"], ["node/5@2026-09-29"])

    def test_boundary_included_and_beyond_excluded(self):
        boundary = self.point(6, 0.01, {"amenity": "bank"})
        radius = _haversine_km(0, 0, 0, boundary.lon)
        outside = self.point(7, 0.011, {"amenity": "bank"})
        evidence = nearby_service_evidence(0, 0, [boundary, outside], radius_km=radius)
        self.assertEqual(evidence["atm_bank"], ["node/6@2026-09-29"])


class EvidenceGateTests(TestCase):
    def setUp(self):
        self.candidate = Candidate("synthetic_1900:1", "synthetic_1900", "Pantai A",
                                   "Kota A", "Aceh", raw={"Price": 0})
        self.c2 = {key: [] for key in ("transport", "healthcare", "atm_bank", "lodging")}

    def ev(self, field, value, note="", reuse="open"):
        return SourceEvidence(self.candidate.candidate_id, field, value,
                              "https://example.org/entry", "2026-09-29", reuse, note)

    def complete_evidence(self):
        return [
            self.ev("identity", "Pantai A"),
            self.ev("location", {"lat": 5.0, "lon": 95.0, "city": "Kota A", "province": "Aceh"}),
            self.ev("c1_ticket_price", 0, "explicit free; ticket_kind=domestic;currency=IDR"),
            self.ev("c2_snapshot", "2026-09-29", "radius_km=2; Indonesia boundary"),
            self.ev("c4_toilet", False, "explicit absent"),
            self.ev("c4_parking", True, "explicit present"),
            self.ev("c4_food", True, "explicit present"),
            self.ev("c4_prayer", False, "explicit absent"),
            self.ev("c5_category", "Pantai", "source tag=natural/beach"),
            self.ev("c6_activity", "berenang", "explicit activity"),
        ]

    def test_generated_zero_is_not_free_entry(self):
        result = review_candidate(self.candidate, [], self.c2)
        self.assertEqual(result.status, "pending")
        self.assertIn("missing:c1_ticket_price", result.reasons)

    def test_fully_sourced_free_entry_can_pass(self):
        result = review_candidate(self.candidate, self.complete_evidence(), self.c2)
        self.assertEqual(result.status, "verified")
        self.assertEqual(result.values["c1_ticket_price"], 0)
        self.assertEqual(result.values["c2_services"], 0)

    def test_unspecified_ticket_or_inferred_absence_cannot_pass(self):
        evidence = self.complete_evidence()
        evidence[2] = self.ev("c1_ticket_price", 0, "free maybe")
        evidence[4] = self.ev("c4_toilet", False, "tag missing")
        result = review_candidate(self.candidate, evidence, self.c2)
        self.assertEqual(result.status, "pending")
        self.assertIn("uncertain:c1_ticket_price", result.reasons)
        self.assertIn("uncertain:c4_toilet", result.reasons)

    def test_conflicting_location_and_unclear_rights(self):
        candidate = Candidate("osm:node/1", "osm", "Pantai A", "Kota A", "Aceh",
                              lat=0.0, lon=100.0, geometry_origin="node")
        evidence = [SourceEvidence(candidate.candidate_id, e.field, e.value, e.source_ref,
                                   e.accessed_at, e.reuse_status, e.note)
                    for e in self.complete_evidence()]
        evidence[2] = SourceEvidence(candidate.candidate_id, "c1_ticket_price", 0,
                                     "https://example.org/entry", "2026-09-29", "unclear",
                                     "explicit free; ticket_kind=domestic;currency=IDR")
        result = review_candidate(candidate, evidence, self.c2)
        self.assertEqual(result.status, "pending")
        self.assertIn("conflict:location", result.reasons)
        self.assertIn("reuse:c1_ticket_price", result.reasons)

    def test_same_name_different_province_not_duplicate(self):
        a = Candidate("a", "osm", "Pantai A", "X", "Aceh")
        b = Candidate("b", "osm", "Pantai A", "X", "Bali")
        c = Candidate("c", "osm", "Pantai A", "Y", "Aceh")
        kept, flags = deduplicate_candidates([a, b, c])
        self.assertEqual(len(kept), 3)
        self.assertEqual([f.candidate_id for f in flags], ["a", "c"])
