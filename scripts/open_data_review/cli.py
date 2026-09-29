"""Offline review command. No Django import, source scrape, or model retraining."""

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from .evidence import deduplicate_candidates, review_candidate
from .export import OUTPUT_NAMES, write_review_outputs
from .legacy import load_legacy_candidates
from .osm import parse_osm_snapshot
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
        ))
    return evidence


def _auto_osm_evidence(candidate, snapshot_at: str) -> list[SourceEvidence]:
    """Use only explicit, item-level OSM tags; never infer ticket/facility negatives."""
    if candidate.origin != "osm":
        return []
    source = candidate.source_path
    base = (candidate.candidate_id, source, snapshot_at, "odbl")
    found = [SourceEvidence(base[0], "identity", candidate.name, base[1], base[2], base[3], "OSM name tag")]
    if candidate.province and candidate.geometry_origin == "node":
        found.append(SourceEvidence(base[0], "location", {
            "lat": candidate.lat, "lon": candidate.lon, "city": candidate.city,
            "province": candidate.province,
        }, base[1], base[2], base[3], "OSM node coordinate + addr:province; manual boundary check advisable"))
    for tag in ("tourism", "natural", "historic"):
        if tag in candidate.raw:
            found.append(SourceEvidence(base[0], "c5_category", candidate.raw[tag],
                                        base[1], base[2], base[3], f"source tag={tag}/{candidate.raw[tag]}"))
            break
    return found


def run_review(
    legacy_xlsx: Path, kaggle_csv: Path, *, osm_json: Path | None = None,
    evidence_csv: Path | None = None, output_dir: Path | None = None,
) -> dict[str, int]:
    """Run one reproducible review and return its actual status counts."""
    legacy_xlsx, kaggle_csv = Path(legacy_xlsx), Path(kaggle_csv)
    osm_json = Path(osm_json) if osm_json else None
    evidence_csv = Path(evidence_csv) if evidence_csv else None
    output_dir = Path(output_dir) if output_dir else ROOT / "data/review"
    inputs = [legacy_xlsx, kaggle_csv] + ([osm_json] if osm_json else []) + ([evidence_csv] if evidence_csv else [])
    if any((output_dir / name).resolve() in {p.resolve() for p in inputs} for name in OUTPUT_NAMES):
        raise ValueError("Review output aliases an input path")
    if output_dir.resolve() in {(ROOT / "data/raw").resolve(), (ROOT / "data/processed").resolve()}:
        raise ValueError("Review output cannot be a production data directory")

    candidates = load_legacy_candidates(legacy_xlsx, kaggle_csv)
    snapshot_at, source_query, points = "", "", []
    if osm_json:
        with osm_json.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        snapshot_at = payload.get("_snapshot_at", "")
        source_query = payload.get("_source_query", "")
        osm_candidates, points = parse_osm_snapshot(payload, snapshot_at, source_query)
        candidates.extend(osm_candidates)
    manual_evidence = _read_evidence(evidence_csv)
    per_candidate = defaultdict(list)
    for item in manual_evidence:
        per_candidate[item.candidate_id].append(item)
    if set(per_candidate) - {c.candidate_id for c in candidates}:
        raise ValueError("Evidence refers to an unknown candidate ID")
    _, duplicate_flags = deduplicate_candidates(candidates)
    duplicate_ids = {flag.candidate_id for flag in duplicate_flags}
    results = []
    for candidate in candidates:
        evidence = per_candidate[candidate.candidate_id] + _auto_osm_evidence(candidate, snapshot_at)
        location = next((e.value for e in evidence if e.field == "location" and isinstance(e.value, dict)), None)
        lat = location.get("lat") if location else candidate.lat
        lon = location.get("lon") if location else candidate.lon
        c2_ids = nearby_service_evidence(float(lat), float(lon), points) if points and lat is not None and lon is not None else {}
        result = review_candidate(candidate, evidence, c2_ids)
        if candidate.candidate_id in duplicate_ids:
            result = type(result)(result.candidate_id, "pending", (*result.reasons, "possible_duplicate"),
                                  result.values, result.evidence)
        results.append(result)
    manifest = {
        "inputs": [{"path": str(p.resolve()), "sha256": _hash(p)} for p in inputs],
        "osm_snapshot_at": snapshot_at or None, "osm_query": source_query or None,
        "osm_candidate_count": sum(c.origin == "osm" for c in candidates),
        "c2_radius_km": 2.0, "c2_classes": list(SERVICE_CLASSES),
        "attribution": "© OpenStreetMap contributors; ODbL 1.0 (https://www.openstreetmap.org/copyright)",
        "warning": "Legacy synthetic and Kaggle values are inventory only, not verified measurements.",
    }
    write_review_outputs(candidates, results, output_dir, manifest)
    counts = {status: sum(r.status == status for r in results) for status in ("verified", "pending", "rejected")}
    counts["candidates"] = len(candidates)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-xlsx", type=Path, default=ROOT / "Dataset_Wisata_38_Provinsi.xlsx")
    parser.add_argument("--kaggle-csv", type=Path, default=ROOT / "data/raw/tourism_with_id.csv")
    parser.add_argument("--osm-json", type=Path, help="saved Overpass JSON with _source_query and _snapshot_at")
    parser.add_argument("--evidence-csv", type=Path, help="manually verified field evidence")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/review")
    args = parser.parse_args()
    print(json.dumps(run_review(args.legacy_xlsx, args.kaggle_csv, osm_json=args.osm_json,
                                evidence_csv=args.evidence_csv, output_dir=args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
