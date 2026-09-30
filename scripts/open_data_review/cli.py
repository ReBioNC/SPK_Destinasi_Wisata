"""Offline review command. No Django import, source scrape, or model retraining."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from .evidence import deduplicate_candidates, resolve_duplicate_flags, review_candidate
from .export import OUTPUT_NAMES, write_review_outputs
from .geonames import load_geonames_zip, read_geonames_receipt
from .legacy import load_legacy_candidates
from .osm import OSM_CATEGORY_MAP, parse_geofabrik_snapshot, parse_osm_snapshot, snapshot_covers_radius
from .schema import SourceEvidence
from .services import SERVICE_CLASSES, nearby_service_evidence


ROOT = Path(__file__).resolve().parents[2]


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_evidence(path: Path | None) -> list[SourceEvidence]:
    if path is None:
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    evidence = []
    for row in rows:
        raw = row["value"]
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            value = raw
        evidence.append(SourceEvidence(
            row["candidate_id"], row["field"], value, row["source_ref"],
            row["accessed_at"], row["reuse_status"], row.get("note", ""),
            row.get("license_ref", ""), row.get("reviewer", ""),
            row.get("reviewed_at", ""), row.get("review_decision", "unreviewed"),
            row.get("valid_on", ""),
        ))
    return evidence


def _auto_osm_evidence(candidate, snapshot_at: str) -> list[SourceEvidence]:
    """Use only explicit, item-level OSM tags; never infer ticket/facility negatives."""
    if candidate.origin != "osm":
        return []
    source = candidate.source_path
    base = (candidate.candidate_id, source, snapshot_at, "odbl")
    license_ref = "https://www.openstreetmap.org/copyright"
    found = [SourceEvidence(base[0], "identity", candidate.name, base[1], base[2], base[3],
                            "OSM name tag", license_ref=license_ref)]
    if candidate.province and candidate.geometry_origin == "node":
        found.append(SourceEvidence(base[0], "location", {
            "lat": candidate.lat, "lon": candidate.lon, "city": candidate.city,
            "province": candidate.province,
        }, base[1], base[2], base[3], "OSM node coordinate + addr:province; manual boundary check advisable",
            license_ref=license_ref))
    for tag in ("tourism", "natural", "historic"):
        category = OSM_CATEGORY_MAP.get((tag, candidate.raw.get(tag)))
        if category:
            found.append(SourceEvidence(base[0], "c5_category", category,
                                        base[1], base[2], base[3], f"source tag={tag}/{candidate.raw[tag]}",
                                        license_ref=license_ref))
            break
    return found


def _auto_geonames_evidence(candidate, accessed_at: str) -> list[SourceEvidence]:
    if candidate.origin != "geonames":
        return []
    source = candidate.source_path
    found = [SourceEvidence(candidate.candidate_id, "identity", candidate.name, source,
                            accessed_at, "cc-by-4.0", "GeoNames item name; tourism status not proven",
                            license_ref="https://download.geonames.org/export/dump/readme.txt")]
    # GeoNames administrative labels can conflict with its own coordinates.
    # Keep them in candidate audit, but require independent location evidence.
    found.append(SourceEvidence(candidate.candidate_id, "c5_category",
                                candidate.raw["category_mapped"], source, accessed_at,
                                "cc-by-4.0", f"source tag=geonames/{candidate.raw['feature_class']}.{candidate.raw['feature_code']}",
                                license_ref="https://download.geonames.org/export/dump/readme.txt"))
    return found


def run_review(
    legacy_xlsx: Path, kaggle_csv: Path, *, osm_json: Path | None = None,
    geonames_zip: Path | None = None, evidence_csv: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, int]:
    """Run one reproducible review and return its actual status counts."""
    legacy_xlsx, kaggle_csv = Path(legacy_xlsx), Path(kaggle_csv)
    osm_json = Path(osm_json) if osm_json else None
    geonames_zip = Path(geonames_zip) if geonames_zip else None
    geonames_receipt = read_geonames_receipt(geonames_zip) if geonames_zip else None
    evidence_csv = Path(evidence_csv) if evidence_csv else None
    output_dir = Path(output_dir) if output_dir else ROOT / "data/review"
    inputs = ([legacy_xlsx, kaggle_csv] + ([osm_json] if osm_json else [])
              + ([geonames_zip, geonames_zip.with_suffix(".source.json")] if geonames_zip else [])
              + ([evidence_csv] if evidence_csv else []))
    if any((output_dir / name).resolve() in {p.resolve() for p in inputs} for name in OUTPUT_NAMES):
        raise ValueError("Review output aliases an input path")
    destination = output_dir.resolve()
    production_dirs = ((ROOT / "data/raw").resolve(), (ROOT / "data/processed").resolve())
    if destination.name.casefold() != "review" or any(
        destination == production or destination.is_relative_to(production)
        for production in production_dirs
    ):
        raise ValueError("Review output must be a review directory outside production data")

    candidates = load_legacy_candidates(legacy_xlsx, kaggle_csv)
    if geonames_zip:
        candidates.extend(load_geonames_zip(geonames_zip))
    geonames_accessed_at = geonames_receipt["retrieved_at"] if geonames_receipt else ""
    snapshot_at, source_query, points, payload = "", "", [], {}
    osm_hash = _hash(osm_json) if osm_json else ""
    if osm_json:
        with osm_json.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        snapshot_at = payload.get("_snapshot_at", "")
        source_query = payload.get("_source_query", "")
        if payload.get("_source_kind") == "geofabrik_maluku":
            osm_candidates, points = parse_geofabrik_snapshot(payload)
        else:
            osm_candidates, points = parse_osm_snapshot(payload, snapshot_at, source_query)
        candidates.extend(osm_candidates)
    manual_evidence = _read_evidence(evidence_csv)
    per_candidate = defaultdict(list)
    for item in manual_evidence:
        per_candidate[item.candidate_id].append(item)
    if set(per_candidate) - {c.candidate_id for c in candidates}:
        raise ValueError("Evidence refers to an unknown candidate ID")
    _, duplicate_flags = deduplicate_candidates(candidates)
    duplicate_disposition = resolve_duplicate_flags(duplicate_flags, manual_evidence)
    results = []
    for candidate in candidates:
        evidence = (per_candidate[candidate.candidate_id]
                    + _auto_osm_evidence(candidate, snapshot_at)
                    + _auto_geonames_evidence(candidate, geonames_accessed_at))
        # Select location through the same approval/consistency gate used below.
        # A provisional candidate point or an earlier unreviewed CSV row cannot
        # silently determine the C2 radius for a later approved location.
        location = review_candidate(candidate, evidence, {}).values.get("location")
        lat = location.get("lat") if location else None
        lon = location.get("lon") if location else None
        scan_source = payload.get("_endpoint") or payload.get("_source_url")
        source_is_recorded = bool(scan_source and urlparse(scan_source).scheme == "https"
                                  and urlparse(scan_source).netloc)
        covered = bool(osm_json and source_is_recorded and lat is not None and lon is not None
                       and snapshot_covers_radius(payload, float(lat), float(lon)))
        c2_ids = nearby_service_evidence(float(lat), float(lon), points) if covered else {}
        if covered:
            evidence.append(SourceEvidence(
                candidate.candidate_id, "c2_service_scan",
                {"score": sum(bool(refs) for refs in c2_ids.values()), "ids": c2_ids,
                 "radius_km": 2.0, "bbox": payload["_bbox"], "snapshot_sha256": osm_hash},
                scan_source,
                snapshot_at, "odbl", "computed mapped-service scan; coordinate may still be provisional",
                license_ref="https://www.openstreetmap.org/copyright",
            ))
        result = review_candidate(candidate, evidence, c2_ids)
        if osm_json and not covered:
            result = type(result)(result.candidate_id, "pending", (*result.reasons, "out_of_coverage:c2"),
                                  result.values, result.evidence)
        if osm_json and result.values.get("c2_snapshot") and result.values["c2_snapshot"] != snapshot_at:
            result = type(result)(result.candidate_id, "pending", (*result.reasons, "conflict:c2_snapshot"),
                                  result.values, result.evidence)
        if covered and result.values.get("c2_snapshot") and not any(
            e.field == "c2_snapshot" and e.source_ref == scan_source
            and e.value == snapshot_at and e.review_decision == "approved"
            for e in evidence
        ):
            result = type(result)(result.candidate_id, "pending", (*result.reasons, "conflict:c2_source"),
                                  result.values, result.evidence)
        disposition = duplicate_disposition.get(candidate.candidate_id)
        if disposition == "rejected":
            result = type(result)(result.candidate_id, "rejected",
                                  (*result.reasons, "reviewed_duplicate_alias"),
                                  result.values, result.evidence)
        elif disposition == "pending":
            result = type(result)(result.candidate_id, "pending", (*result.reasons, "possible_duplicate"),
                                  result.values, result.evidence)
        results.append(result)
    manifest = {
        "inputs": [{"path": str(p.resolve()), "sha256": _hash(p)} for p in inputs],
        "osm_snapshot_at": snapshot_at or None, "osm_query": source_query or None,
        "osm_source_url": payload.get("_source_url") if osm_json else None,
        "osm_endpoint": payload.get("_endpoint") if osm_json else None,
        "osm_extract_sha256": payload.get("_extract_sha256") if osm_json else None,
        "osm_candidate_count": sum(c.origin == "osm" for c in candidates),
        "geonames_candidate_count": sum(c.origin == "geonames" for c in candidates),
        "geonames_license": "CC BY 4.0; https://download.geonames.org/export/dump/readme.txt" if geonames_zip else None,
        "geonames_source_url": "https://download.geonames.org/export/dump/ID.zip" if geonames_zip else None,
        "geonames_accessed_at": geonames_accessed_at or None,
        "c2_radius_km": 2.0, "c2_classes": list(SERVICE_CLASSES),
        "attribution": (["© OpenStreetMap contributors; ODbL 1.0 (https://www.openstreetmap.org/copyright)"]
                        if osm_json else []) + (["GeoNames; CC BY 4.0 (https://www.geonames.org/export/)"]
                                           if geonames_zip else []),
        "warning": "Legacy synthetic and Kaggle values are inventory only, not verified measurements.",
    }
    write_review_outputs(candidates, results, output_dir, manifest)
    counts = {status: sum(r.status == status for r in results) for status in ("verified", "pending", "rejected")}
    counts["candidates"] = len(candidates)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-xlsx", type=Path, default=ROOT / "archive/legacy/Dataset_Wisata_38_Provinsi.xlsx")
    parser.add_argument("--kaggle-csv", type=Path, default=ROOT / "data/raw/tourism_with_id.csv")
    parser.add_argument("--osm-json", type=Path, help="saved Overpass JSON with _source_query and _snapshot_at")
    parser.add_argument("--geonames-zip", type=Path, help="official GeoNames ID.zip country extract")
    parser.add_argument("--evidence-csv", type=Path, help="manually verified field evidence")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/review")
    args = parser.parse_args()
    print(json.dumps(run_review(args.legacy_xlsx, args.kaggle_csv, osm_json=args.osm_json,
                                geonames_zip=args.geonames_zip, evidence_csv=args.evidence_csv,
                                output_dir=args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
