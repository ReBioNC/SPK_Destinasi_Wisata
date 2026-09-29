"""Conservative item-level evidence gate; legacy values are never proof."""

import math
import re
import unicodedata
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import urlparse

from .schema import Candidate, ReviewResult, SourceEvidence
from .services import SERVICE_CLASSES, _haversine_km, service_score


REQUIRED_FIELDS = (
    "identity", "location", "c1_ticket_price", "c2_snapshot",
    "c4_toilet", "c4_parking", "c4_food", "c4_prayer",
    "c5_category", "c6_activity",
)
ACCEPTED_REUSE = {"odbl", "cc0", "cc-by-4.0", "public-domain"}
TRAVELFIT_CATEGORIES = {
    "Pantai", "Bahari", "Gunung", "Cagar Alam", "Budaya",
    "Taman Hiburan", "Pusat Perbelanjaan", "Tempat Ibadah",
}


def _norm(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    return " ".join(re.findall(r"\w+", text))


def _source_ok(e: SourceEvidence) -> bool:
    parsed = urlparse(e.source_ref)
    license_parsed = urlparse(e.license_ref)
    try:
        date.fromisoformat(e.accessed_at)
    except ValueError:
        return False
    source_host, license_host = parsed.hostname or "", license_parsed.hostname or ""
    related = source_host == license_host or any(
        source_host.endswith("." + domain) and license_host.endswith("." + domain)
        for domain in ("geonames.org", "openstreetmap.org")
    )
    if source_host == "download.geofabrik.de" and license_host == "www.openstreetmap.org":
        related = True  # Geofabrik distributes OSM under ODbL.
    if (e.field == "c2_snapshot" and source_host == "overpass-api.de"
            and license_host == "www.openstreetmap.org"):
        related = True  # Overpass serves OSM data, whose license is ODbL.
    return (parsed.scheme == "https" and bool(source_host)
            and parsed.path not in {"", "/"}
            and license_parsed.scheme == "https" and bool(license_host)
            and license_parsed.path not in {"", "/"} and related)


def _review_ok(e: SourceEvidence) -> bool:
    if e.review_decision != "approved" or not e.reviewer.strip():
        return False
    try:
        reviewed = date.fromisoformat(e.reviewed_at)
        if reviewed < date.fromisoformat(e.accessed_at):
            return False
        if e.field == "c1_ticket_price":
            valid_on = date.fromisoformat(e.valid_on)
            return valid_on >= date.today() - timedelta(days=365)
        return True
    except ValueError:
        return False


def _field_ok(field: str, value, note: str) -> bool:
    note = note.casefold()
    if field == "identity":
        return isinstance(value, str) and bool(value.strip())
    if field == "location":
        if not isinstance(value, dict):
            return False
        try:
            lat, lon = float(value["lat"]), float(value["lon"])
            return (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90
                    and -180 <= lon <= 180 and bool(value.get("province")))
        except (KeyError, TypeError, ValueError):
            return False
    if field == "c1_ticket_price":
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value >= 0 and value == int(value)
                and "ticket_kind=domestic" in note and "currency=idr" in note
                and (value != 0 or "explicit free" in note))
    if field == "c2_snapshot":
        try:
            date.fromisoformat(str(value))
        except ValueError:
            return False
        return "radius_km=2" in note and "indonesia boundary" in note
    if field.startswith("c4_"):
        return isinstance(value, bool) and (
            (value and "explicit present" in note)
            or (not value and "explicit absent" in note)
        )
    if field == "c5_category":
        return isinstance(value, str) and value in TRAVELFIT_CATEGORIES and "source tag=" in note
    if field == "c6_activity":
        return isinstance(value, str) and bool(value.strip()) and "explicit activity" in note
    return False


def review_candidate(
    candidate: Candidate, evidence: list[SourceEvidence], c2_ids: dict[str, list[str]],
) -> ReviewResult:
    """Pass only when every criterion has independent, reusable, explicit evidence."""
    grouped = defaultdict(list)
    for item in evidence:
        if item.candidate_id == candidate.candidate_id:
            grouped[item.field].append(item)
    reasons: list[str] = []
    values = {}
    selected = {}
    for field in REQUIRED_FIELDS:
        records = grouped.get(field, [])
        if not records:
            reasons.append(f"missing:{field}")
            continue
        reusable = [e for e in records if _source_ok(e) and e.reuse_status.casefold() in ACCEPTED_REUSE]
        if not reusable:
            reasons.append(f"reuse:{field}")
            continue
        valid = [e for e in reusable if _review_ok(e)]
        if not valid:
            reasons.append(f"unreviewed:{field}")
            continue
        if any(e.value != valid[0].value for e in valid[1:]):
            reasons.append(f"conflict:{field}")
            continue
        item = valid[0]
        if not _field_ok(field, item.value, item.note):
            reasons.append(f"uncertain:{field}")
            continue
        values[field] = item.value
        selected[field] = item

    if "identity" in values and _norm(values["identity"]) != _norm(candidate.name):
        reasons.append("conflict:identity")
    location = values.get("location")
    if location:
        location_record = selected["location"]
        independently_corrected = location_record.source_ref != candidate.source_path
        if (candidate.province and _norm(location["province"]) != _norm(candidate.province)
                and not (independently_corrected and "province_corrected" in location_record.note)):
            reasons.append("conflict:province")
        if candidate.lat is not None and candidate.lon is not None:
            if (_haversine_km(candidate.lat, candidate.lon, location["lat"], location["lon"]) > 2
                    and not (independently_corrected and "coordinate_corrected" in location_record.note)):
                reasons.append("conflict:location")
        if candidate.geometry_origin in {"center_unverified", "gazetteer_point_unverified"} and not any(
            "entrance_checked" in e.note for e in grouped.get("location", [])
        ):
            reasons.append("uncertain:entrance_location")
    if set(c2_ids) != set(SERVICE_CLASSES):
        reasons.append("missing:c2_service_scan")
    elif "location" in values and "c2_snapshot" in values:
        snapshot = values["c2_snapshot"]
        if any("@" not in ref or not ref.endswith(f"@{snapshot}")
               for refs in c2_ids.values() for ref in refs):
            reasons.append("conflict:c2_snapshot")
        else:
            values["c2_services"] = service_score(c2_ids)
            values["c2_service_ids"] = c2_ids
    status = "verified" if not reasons else "pending"
    return ReviewResult(candidate.candidate_id, status, tuple(dict.fromkeys(reasons)),
                        values, tuple(e for e in evidence if e.candidate_id == candidate.candidate_id))


def deduplicate_candidates(candidates: list[Candidate]) -> tuple[list[Candidate], list[ReviewResult]]:
    """Flag same-name pairs by matching province or provisional nearby coordinates.

    Legacy coordinates are used only to raise a review flag, never as proof.
    """
    groups = defaultdict(list)
    for candidate in candidates:
        if candidate.name.strip():
            groups[_norm(candidate.name)].append(candidate)

    def coords(candidate):
        try:
            lat = candidate.lat if candidate.lat is not None else float(candidate.raw["Lat"])
            lon = candidate.lon if candidate.lon is not None else float(candidate.raw["Long"])
            return (lat, lon) if math.isfinite(lat) and math.isfinite(lon) else None
        except (KeyError, TypeError, ValueError):
            return None

    peers = defaultdict(set)
    for group in groups.values():
        for index, left in enumerate(group):
            for right in group[index + 1:]:
                same_province = (left.province and right.province
                                 and _norm(left.province) == _norm(right.province))
                a, b = coords(left), coords(right)
                nearby = bool(a and b and _haversine_km(*a, *b) <= 2)
                if same_province or nearby:
                    peers[left.candidate_id].add(right.candidate_id)
                    peers[right.candidate_id].add(left.candidate_id)
    flagged = [ReviewResult(c.candidate_id, "pending",
                            tuple(f"possible_duplicate:{peer}" for peer in sorted(peers[c.candidate_id])))
               for c in candidates if c.candidate_id in peers]
    return candidates, flagged


def resolve_duplicate_flags(
    flags: list[ReviewResult], evidence: list[SourceEvidence],
) -> dict[str, str]:
    """Return pending/resolved/rejected after reviewed per-candidate identity decisions.

    No automatic pair is merged. A canonical candidate is released only when
    every flagged peer has a reviewed alias decision pointing to it.
    """
    peer_map = {flag.candidate_id: {reason.split(":", 1)[1] for reason in flag.reasons
                                    if reason.startswith("possible_duplicate:")}
                for flag in flags}
    decisions = {}
    for item in evidence:
        if (item.field != "duplicate_resolution" or item.candidate_id not in peer_map
                or not isinstance(item.value, dict)
                or not _source_ok(item) or item.reuse_status.casefold() not in ACCEPTED_REUSE
                or not _review_ok(item)):
            continue
        if set(item.value.get("peer_ids", [])) != peer_map[item.candidate_id]:
            continue
        decisions[item.candidate_id] = item.value
    aliases = {ident: value.get("canonical_id") for ident, value in decisions.items()
               if value.get("decision") == "alias"
               and value.get("canonical_id") in peer_map[ident]}
    dispositions = {}
    for ident, peers in peer_map.items():
        decision = decisions.get(ident, {})
        if ident in aliases:
            dispositions[ident] = "rejected"
        elif decision.get("decision") == "distinct":
            dispositions[ident] = "resolved"
        elif (decision.get("decision") == "canonical"
              and all(aliases.get(peer) == ident for peer in peers)):
            dispositions[ident] = "resolved"
        else:
            dispositions[ident] = "pending"
    return dispositions
