"""One bounded, sequential Overpass request; never bulk-crawls an entire country."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .osm import INDONESIA_QUERY


ENDPOINT = "https://overpass-api.de/api/interpreter"
MAX_RESPONSE_BYTES = 10 * 1024 * 1024


def build_bounded_query(bbox: tuple[float, float, float, float]) -> str:
    """Require a small Indonesia-extent bbox *and* the Indonesia admin boundary."""
    south, west, north, east = bbox
    if not (-12 <= south < north <= 7 and 94 <= west < east <= 142):
        raise ValueError("BBox must be within Indonesia's approximate geographic envelope")
    if (north - south) * (east - west) > 0.5:
        raise ValueError("BBox is too large for a bounded public Overpass request")
    bounds = "(" + ",".join(f"{number:g}" for number in bbox) + ")"
    return INDONESIA_QUERY.replace("[timeout:180]", "[timeout:60]").replace(
        "(area.indonesia);", f"(area.indonesia){bounds};"
    )


def fetch_once(bbox: tuple[float, float, float, float], output: Path) -> dict:
    """Fetch one response, capped at 10 MB, and save a provenance-wrapped snapshot."""
    query = build_bounded_query(bbox)
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    request = Request(
        ENDPOINT, data=urlencode({"data": query}).encode("utf-8"), method="POST",
        headers={"User-Agent": "TravelFit-academic-review/1.0 (one bounded query; OSM attribution)",
                 "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urlopen(request, timeout=90) as response:
        data = response.read(MAX_RESPONSE_BYTES + 1)
    if len(data) > MAX_RESPONSE_BYTES:
        raise ValueError("Overpass response exceeded 10 MB cap; try a smaller bbox")
    payload = json.loads(data)
    if not isinstance(payload.get("elements"), list):
        raise ValueError("Overpass did not return elements")
    snapshot = {
        "_endpoint": ENDPOINT, "_source_query": query,
        "_snapshot_at": datetime.now(timezone.utc).date().isoformat(),
        "_bbox": list(bbox), "_license_url": "https://www.openstreetmap.org/copyright",
        "elements": payload["elements"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
    return {"elements": len(snapshot["elements"]), "snapshot_at": snapshot["_snapshot_at"], "path": str(output)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", type=float, nargs=4, required=True, metavar=("S", "W", "N", "E"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(fetch_once(tuple(args.bbox), args.output), sort_keys=True))


if __name__ == "__main__":
    main()
