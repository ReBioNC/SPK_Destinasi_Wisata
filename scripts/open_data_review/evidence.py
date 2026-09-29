"""Conservative item-level evidence gate; legacy values are never proof."""

import math
import re
import unicodedata
from collections import defaultdict
from datetime import date
from urllib.parse import urlparse

from .schema import Candidate, ReviewResult, SourceEvidence
from .services import SERVICE_CLASSES, _haversine_km, service_score


REQUIRED_FIELDS = (
    "identity", "location", "c1_ticket_price", "c2_snapshot",
    "c4_toilet", "c4_parking", "c4_food", "c4_prayer",
    "c5_category", "c6_activity",
)
ACCEPTED_REUSE = {"open", "odbl", "cc0", "cc-by", "cc-by-4.0", "public-domain"}


def _norm(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    return " ".join(re.findall(r"\w+", text))


def _source_ok(e: SourceEvidence) -> bool:
    parsed = urlparse(e.source_ref)
    try:
        date.fromisoformat(e.accessed_at)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


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
        return isinstance(value, str) and bool(value.strip()) and "source tag=" in note
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
    for field in REQUIRED_FIELDS:
        records = grouped.get(field, [])
        if not records:
            reasons.append(f"missing:{field}")
            continue
        valid = [e for e in records if _source_ok(e) and e.reuse_status.casefold() in ACCEPTED_REUSE]
        if not valid:
            reasons.append(f"reuse:{field}")
            continue
        if any(e.value != valid[0].value for e in valid[1:]):
            reasons.append(f"conflict:{field}")
            continue
        item = valid[0]
        if not _field_ok(field, item.value, item.note):
            reasons.append(f"uncertain:{field}")
            continue
        values[field] = item.value

    if "identity" in values and _norm(values["identity"]) != _norm(candidate.name):
        reasons.append("conflict:identity")
    location = values.get("location")
    if location:
        if candidate.province and _norm(location["province"]) != _norm(candidate.province):
            reasons.append("conflict:province")
        if candidate.lat is not None and candidate.lon is not None:
            if _haversine_km(candidate.lat, candidate.lon, location["lat"], location["lon"]) > 2:
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

    flagged_ids = set()
    for group in groups.values():
        for index, left in enumerate(group):
            for right in group[index + 1:]:
                same_province = (left.province and right.province
                                 and _norm(left.province) == _norm(right.province))
                a, b = coords(left), coords(right)
                nearby = bool(a and b and _haversine_km(*a, *b) <= 2)
                if same_province or nearby:
                    flagged_ids.update((left.candidate_id, right.candidate_id))
    flagged = [ReviewResult(c.candidate_id, "pending", ("possible_duplicate",))
               for c in candidates if c.candidate_id in flagged_ids]
    return candidates, flagged
