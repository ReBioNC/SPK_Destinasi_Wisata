"""Deterministic, review-only CSV/Markdown artifacts."""

import csv
import json
from collections import Counter
from pathlib import Path

from .schema import Candidate, ReviewResult


AUDIT_FIELDS = (
    "candidate_id", "origin", "source_row_id", "source_path", "place_name",
    "city_raw", "province_raw", "category_raw", "price_raw_unverified",
    "rating_raw_unverified", "lat_raw_unverified", "lon_raw_unverified",
    "possible_filler_name", "geometry_origin", "status", "reasons",
)
VERIFIED_FIELDS = (
    "Place_Id", "Place_Name", "Description", "Category", "City", "Province",
    "Price", "Rating", "Time_Minutes", "Coordinate", "Lat", "Long",
    "c2_services", "c2_service_ids", "c4_toilet", "c4_parking", "c4_food",
    "c4_prayer", "c6_activity", "candidate_id",
)
EVIDENCE_FIELDS = (
    "candidate_id", "field", "value", "source_ref", "accessed_at", "reuse_status", "note",
)
OUTPUT_NAMES = (
    "destinations_candidate_audit.csv", "destinations_verified_open.csv",
    "destination_evidence.csv", "audit_summary.md", "source_manifest.json",
)


def _string(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _string(row.get(key)) for key in fields})


def write_review_outputs(
    candidates: list[Candidate], results: list[ReviewResult], output_dir: Path,
    source_manifest: dict | None = None,
) -> None:
    """Write only new review files; reject aliases to any declared input file."""
    output_dir = Path(output_dir)
    manifest = source_manifest or {"inputs": [], "attribution": "© OpenStreetMap contributors; ODbL 1.0"}
    inputs = {Path(item["path"]).resolve() for item in manifest.get("inputs", [])}
    if any((output_dir / name).resolve() in inputs for name in OUTPUT_NAMES):
        raise ValueError("Review output would overwrite a source input")
    result_map = {result.candidate_id: result for result in results}
    if len(result_map) != len(results) or len({c.candidate_id for c in candidates}) != len(candidates):
        raise ValueError("Candidate and result IDs must be unique")
    if set(result_map) != {c.candidate_id for c in candidates}:
        raise ValueError("One review result is required for each candidate")
    output_dir.mkdir(parents=True, exist_ok=True)
    audit, verified, evidence_rows = [], [], []
    status_counts, reason_counts, province_counts, category_counts = Counter(), Counter(), Counter(), Counter()
    for candidate in sorted(candidates, key=lambda row: row.candidate_id):
        result = result_map[candidate.candidate_id]
        status_counts[result.status] += 1
        reason_counts.update(result.reasons)
        province_counts[candidate.province or "(unknown)"] += 1
        category_counts[str(candidate.raw.get("Category") or candidate.raw.get("tourism") or candidate.raw.get("natural") or "(unknown)")] += 1
        audit.append({
            "candidate_id": candidate.candidate_id, "origin": candidate.origin,
            "source_row_id": candidate.source_row_id, "source_path": candidate.source_path,
            "place_name": candidate.name, "city_raw": candidate.city, "province_raw": candidate.province,
            "category_raw": candidate.raw.get("Category") or candidate.raw.get("tourism") or candidate.raw.get("natural"),
            "price_raw_unverified": candidate.raw.get("Price"),
            "rating_raw_unverified": candidate.raw.get("Rating"),
            "lat_raw_unverified": candidate.raw.get("Lat") or candidate.lat,
            "lon_raw_unverified": candidate.raw.get("Long") or candidate.lon,
            "possible_filler_name": candidate.possible_filler_name,
            "geometry_origin": candidate.geometry_origin,
            "status": result.status, "reasons": ";".join(result.reasons),
        })
        for e in sorted(result.evidence, key=lambda item: (item.field, item.source_ref)):
            evidence_rows.append({key: getattr(e, key) for key in EVIDENCE_FIELDS})
        if result.status == "verified":
            v, loc = result.values, result.values["location"]
            verified.append({
                "Place_Id": candidate.candidate_id, "Place_Name": candidate.name,
                "Description": "", "Category": v["c5_category"], "City": loc.get("city", ""),
                "Province": loc["province"], "Price": v["c1_ticket_price"],
                "Rating": "", "Time_Minutes": "", "Coordinate": {"lat": loc["lat"], "lng": loc["lon"]},
                "Lat": loc["lat"], "Long": loc["lon"],
                "c2_services": v["c2_services"], "c2_service_ids": v["c2_service_ids"],
                "c4_toilet": v["c4_toilet"], "c4_parking": v["c4_parking"],
                "c4_food": v["c4_food"], "c4_prayer": v["c4_prayer"],
                "c6_activity": v["c6_activity"], "candidate_id": candidate.candidate_id,
            })
    _write_csv(output_dir / OUTPUT_NAMES[0], AUDIT_FIELDS, audit)
    _write_csv(output_dir / OUTPUT_NAMES[1], VERIFIED_FIELDS, verified)
    _write_csv(output_dir / OUTPUT_NAMES[2], EVIDENCE_FIELDS, evidence_rows)
    lines = [
        "# TravelFit — audit kandidat sumber terbuka", "",
        f"Kandidat: **{len(candidates)}**; terverifikasi: **{status_counts['verified']}**; "
        f"pending: **{status_counts['pending']}**; ditolak: **{status_counts['rejected']}**.", "",
        "File ini untuk peninjauan. Website, dataset produksi, bobot AHP, dan K-Means **belum diubah**.",
        "Harga/rating berlabel `raw_unverified` tidak boleh dipakai sebagai fakta. "
        "Rating di hasil siap pakai sengaja kosong karena C2 baru adalah layanan sekitar terpetakan.",
        "Skor C2=0 berarti tidak ada layanan dalam empat kelas yang *terpetakan* pada snapshot dan radius 2 km, "
        "bukan tidak ada layanan di dunia nyata.", "",
        "## Alasan tertahan", "",
    ]
    lines += [f"- {key}: {count}" for key, count in sorted(reason_counts.items())] or ["- Tidak ada."]
    lines += ["", "## Cakupan kandidat per provinsi", ""]
    lines += [f"- {key}: {count}" for key, count in sorted(province_counts.items())]
    lines += ["", "## Cakupan kandidat per kategori mentah", ""]
    lines += [f"- {key}: {count}" for key, count in sorted(category_counts.items())]
    lines += ["", "## Batasan", "",
              "OSM tidak lengkap secara merata. Harga, fasilitas onsite, aktivitas, dan lokasi masuk "
              "membutuhkan bukti item-spesifik dengan hak pakai jelas. Kandidat tanpa bukti tetap pending.", ""]
    (output_dir / OUTPUT_NAMES[3]).write_text("\n".join(lines), encoding="utf-8")
    (output_dir / OUTPUT_NAMES[4]).write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
