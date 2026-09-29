"""Small explicit records shared by the review-only pipeline."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    origin: str
    name: str
    city: str = ""
    province: str = ""
    source_row_id: str = ""
    source_path: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    untrusted_fields: tuple[str, ...] = ()
    possible_filler_name: bool = False
    lat: float | None = None
    lon: float | None = None
    geometry_origin: str = ""


@dataclass(frozen=True)
class OsmPoint:
    osm_type: str
    osm_id: int
    lat: float
    lon: float
    tags: dict[str, str]
    geometry_origin: str
    snapshot_at: str

    @property
    def ref(self) -> str:
        return f"{self.osm_type}/{self.osm_id}"


@dataclass(frozen=True)
class SourceEvidence:
    candidate_id: str
    field: str
    value: Any
    source_ref: str
    accessed_at: str
    reuse_status: str
    note: str = ""
    license_ref: str = ""
    reviewer: str = ""
    reviewed_at: str = ""
    review_decision: str = "unreviewed"
    valid_on: str = ""


@dataclass(frozen=True)
class ReviewResult:
    candidate_id: str
    status: str
    reasons: tuple[str, ...]
    values: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[SourceEvidence, ...] = ()
