"""Regression tests for the isolated, review-only open-data pipeline."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from hashlib import sha256
import csv
import json

import pandas as pd

from scripts.open_data_review.legacy import load_legacy_candidates
from scripts.open_data_review.osm import parse_osm_snapshot, parse_geofabrik_snapshot, INDONESIA_QUERY
from scripts.open_data_review.schema import OsmPoint
from scripts.open_data_review.services import nearby_service_evidence, service_score, _haversine_km
from scripts.open_data_review.schema import Candidate, SourceEvidence
from scripts.open_data_review.evidence import review_candidate, deduplicate_candidates
from scripts.open_data_review.export import write_review_outputs
from scripts.open_data_review.cli import run_review, _auto_geonames_evidence, _auto_osm_evidence
from scripts.open_data_review.fetch_osm import build_bounded_query
from scripts.open_data_review.geonames import parse_geonames_rows


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

    def test_osm_category_is_mapped_to_travelfit_taxonomy(self):
        candidate = Candidate("osm:node/11", "osm", "Museum A",
                              source_path="https://www.openstreetmap.org/node/11",
                              raw={"tourism": "museum"})
        values = [e.value for e in _auto_osm_evidence(candidate, "2026-09-29")
                  if e.field == "c5_category"]
        self.assertEqual(values, ["Budaya"])


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

    def test_gazetteer_point_is_not_automatically_an_entrance(self):
        candidate = Candidate(self.candidate.candidate_id, "geonames", "Pantai A",
                              "Kota A", "Aceh", lat=5.0, lon=95.0,
                              geometry_origin="gazetteer_point_unverified")
        result = review_candidate(candidate, self.complete_evidence(), self.c2)
        self.assertIn("uncertain:entrance_location", result.reasons)

    def test_same_name_nearby_kaggle_and_geonames_are_flagged(self):
        kaggle = Candidate("kaggle_437:7", "kaggle_437", "Kebun Binatang Ragunan",
                           raw={"Lat": -6.31246, "Long": 106.82019})
        gazetteer = Candidate("geonames:1960432", "geonames", "Kebun Binatang Ragunan",
                              province="Daerah Khusus Ibukota Jakarta", lat=-6.31064, lon=106.81998)
        _, flags = deduplicate_candidates([kaggle, gazetteer])
        self.assertEqual({flag.candidate_id for flag in flags}, {kaggle.candidate_id, gazetteer.candidate_id})


class ReviewExportTests(TestCase):
    def test_isolated_outputs_are_deterministic_and_do_not_change_inputs(self):
        with TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            source = base / "input.csv"
            source.write_text("source,untouched\n", encoding="utf-8")
            before = sha256(source.read_bytes()).hexdigest()
            candidate = Candidate("x:1", "osm", "Museum A", "Kota A", "Aceh")
            evidence = [
                SourceEvidence("x:1", "identity", "Museum A", "https://example.org/a",
                               "2026-09-29", "open", "item-specific"),
            ]
            result = review_candidate(candidate, evidence, {})
            out = base / "review"
            manifest = {"inputs": [{"path": str(source), "sha256": before}],
                        "attribution": "© OpenStreetMap contributors; ODbL 1.0"}
            write_review_outputs([candidate], [result], out, manifest)
            expected = (
                "destinations_candidate_audit.csv", "destinations_verified_open.csv",
                "destination_evidence.csv", "audit_summary.md", "source_manifest.json",
            )
            self.assertTrue(all((out / name).exists() for name in expected))
            first = {name: (out / name).read_bytes() for name in expected}
            with (out / "destinations_candidate_audit.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(list(csv.DictReader(handle))[0]["status"], "pending")
            with (out / "destinations_verified_open.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(list(csv.DictReader(handle)), [])
            self.assertIn("https://example.org/a", (out / "destination_evidence.csv").read_text(encoding="utf-8"))
            write_review_outputs([candidate], [result], out, manifest)
            self.assertEqual(first, {name: (out / name).read_bytes() for name in expected})
            self.assertEqual(sha256(source.read_bytes()).hexdigest(), before)

    def test_cli_refuses_output_that_aliases_input(self):
        with TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            xlsx = base / "old.xlsx"
            csv_path = base / "destinations_candidate_audit.csv"
            pd.DataFrame([{"Place_Id": 1, "Place_Name": "A"}]).to_excel(xlsx, index=False)
            pd.DataFrame([{"Place_Id": 2, "Place_Name": "B"}]).to_csv(csv_path, index=False)
            with self.assertRaises(ValueError):
                run_review(xlsx, csv_path, output_dir=base)

    def test_geonames_category_is_visible_in_audit(self):
        with TemporaryDirectory(dir=ROOT) as tmp:
            candidate = Candidate("geonames:1", "geonames", "Pantai A", "", "Aceh",
                                  raw={"category_mapped": "Pantai"})
            result = review_candidate(candidate, [], {})
            out = Path(tmp) / "review"
            write_review_outputs([candidate], [result], out)
            with (out / "destinations_candidate_audit.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(list(csv.DictReader(handle))[0]["category_raw"], "Pantai")

    def test_cli_can_verify_explicit_evidence_with_empty_mapped_service_snapshot(self):
        with TemporaryDirectory(dir=ROOT) as tmp:
            base = Path(tmp)
            xlsx, kaggle, osm, evidence_csv = (base / name for name in
                ("old.xlsx", "kaggle.csv", "osm.json", "evidence.csv"))
            pd.DataFrame([{"Place_Id": 1, "Place_Name": "Pantai A", "City": "Kota A",
                           "Province": "Aceh", "Price": 0}]).to_excel(xlsx, index=False)
            pd.DataFrame(columns=["Place_Id", "Place_Name"]).to_csv(kaggle, index=False)
            osm.write_text(json.dumps({"_snapshot_at": "2026-09-29", "_source_query": INDONESIA_QUERY,
                                       "elements": []}), encoding="utf-8")
            values = {
                "identity": "Pantai A", "location": {"lat": 5, "lon": 95,
                    "city": "Kota A", "province": "Aceh"},
                "c1_ticket_price": 0, "c2_snapshot": "2026-09-29",
                "c4_toilet": False, "c4_parking": True, "c4_food": True,
                "c4_prayer": False, "c5_category": "Pantai", "c6_activity": "berenang",
            }
            notes = {"c1_ticket_price": "explicit free; ticket_kind=domestic;currency=IDR",
                     "c2_snapshot": "radius_km=2; Indonesia boundary",
                     "c4_toilet": "explicit absent", "c4_parking": "explicit present",
                     "c4_food": "explicit present", "c4_prayer": "explicit absent",
                     "c5_category": "source tag=natural/beach", "c6_activity": "explicit activity"}
            with evidence_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["candidate_id", "field", "value",
                    "source_ref", "accessed_at", "reuse_status", "note"])
                writer.writeheader()
                for field, value in values.items():
                    writer.writerow({"candidate_id": "synthetic_1900:1", "field": field,
                        "value": json.dumps(value), "source_ref": "https://example.org/item",
                        "accessed_at": "2026-09-29", "reuse_status": "open", "note": notes.get(field, "")})
            out = base / "review"
            counts = run_review(xlsx, kaggle, osm_json=osm, evidence_csv=evidence_csv, output_dir=out)
            self.assertEqual(counts["verified"], 1)
            with (out / "destinations_verified_open.csv").open(encoding="utf-8", newline="") as handle:
                row = list(csv.DictReader(handle))[0]
            self.assertEqual(row["Price"], "0")
            self.assertEqual(row["c2_services"], "0")
            self.assertEqual(row["Rating"], "")
            with evidence_csv.open(encoding="utf-8", newline="") as handle:
                items = list(csv.DictReader(handle))
            for item in items:
                if item["field"] == "c2_snapshot":
                    item["value"] = json.dumps("2026-09-28")
            with evidence_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(items[0]))
                writer.writeheader()
                writer.writerows(items)
            counts = run_review(xlsx, kaggle, osm_json=osm, evidence_csv=evidence_csv, output_dir=out)
            self.assertEqual(counts["verified"], 0)


class BoundedSourceTests(TestCase):
    def test_query_is_country_filtered_and_geographically_bounded(self):
        query = build_bounded_query((-8.8, 115.1, -8.5, 115.4))
        self.assertIn('["ISO3166-1"="ID"]', query)
        self.assertIn('(area.indonesia)(-8.8,115.1,-8.5,115.4)', query)
        with self.assertRaises(ValueError):
            build_bounded_query((-90, -180, 90, 180))

    def test_regional_extract_requires_explicit_source_metadata(self):
        payload = {"_source_kind": "geofabrik_maluku", "_source_url":
                   "https://download.geofabrik.de/asia/indonesia/maluku-260915.osm.pbf",
                   "_snapshot_at": "2026-09-15", "elements": [{"type": "node", "id": 9,
                   "lat": -3.7, "lon": 128.2, "tags": {"name": "Museum Ambon", "tourism": "museum"}}]}
        candidates, points = parse_geofabrik_snapshot(payload)
        self.assertEqual(candidates[0].name, "Museum Ambon")
        self.assertEqual(len(points), 1)
        self.assertEqual(candidates[0].province, "")
        payload["_source_url"] = "https://example.com/unknown.pbf"
        with self.assertRaises(ValueError):
            parse_geofabrik_snapshot(payload)


class GeoNamesTests(TestCase):
    def test_only_indonesian_landmark_codes_become_candidates(self):
        def row(ident, name, cls, code, country="ID", adm="01"):
            fields = [str(ident), name, name, "", "-6.0", "106.0", cls, code,
                      country, "", adm, "01", "", "", "0", "", "", "Asia/Jakarta", "2026-09-20"]
            return "\t".join(fields)
        rows = [row(1, "Provinsi A", "A", "ADM1"), row(2, "Pantai A", "T", "BCH"),
                row(3, "Desa B", "P", "PPL"), row(4, "Museum C", "S", "MUS"),
                row(5, "Foreign", "T", "BCH", "TL"),
                row(6, "Puncak tanpa informasi wisata", "T", "PK")]
        candidates = parse_geonames_rows(rows)
        self.assertEqual([c.name for c in candidates], ["Pantai A", "Museum C"])
        self.assertEqual(candidates[0].province, "Provinsi A")
        self.assertEqual(candidates[0].candidate_id, "geonames:2")

    def test_gazetteer_admin_label_is_not_location_verification(self):
        candidate = Candidate("geonames:9", "geonames", "Pura X", "", "Sulawesi Tengah",
                              raw={"category_mapped": "Tempat Ibadah", "feature_class": "S",
                                   "feature_code": "TMPL"}, lat=-8.34, lon=115.59,
                              source_path="https://www.geonames.org/9/",
                              geometry_origin="gazetteer_point_unverified")
        fields = {item.field for item in _auto_geonames_evidence(candidate, "2026-09-29")}
        self.assertNotIn("location", fields)
