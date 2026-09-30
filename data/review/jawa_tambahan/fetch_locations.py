"""Seven targeted searches and three bounded name variants, with source receipts.

Downloads source evidence only; does not select candidates or change production.
Run from repo root: python data/review/jawa_tambahan/fetch_locations.py
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCES = Path(__file__).resolve().parent / "sources"
QUERIES = {
    "tosan_aji": "Museum Tosan Aji, Purworejo, Indonesia",
    "seplawan": "Goa Seplawan, Purworejo, Indonesia",
    "jatimalang": "Pantai Jatimalang, Purworejo, Indonesia",
    "geger_menjangan": "Geger Menjangan, Purworejo, Indonesia",
    "artha_tirta": "Artha Tirta, Purworejo, Indonesia",
    "trinil": "Museum Trinil, Ngawi, Indonesia",
    "tawun": "Taman Wisata Tawun, Ngawi, Indonesia",
    "seplawan_short": "Seplawan",
    "geger_short": "Geger Menjangan",
    "tawun_short": "Tawun",
}


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, query in QUERIES.items():
        path = SOURCES / f"nominatim_{name}.json"
        if path.exists():
            print(f"Cached: {name}", flush=True)
            continue
        params = {"q": query, "format": "jsonv2", "limit": 3, "countrycodes": "id"}
        if name.endswith("_short"):
            params.update({"bounded": 1, "viewbox":
                           "111.40,-7.32,111.58,-7.50" if name == "tawun_short"
                           else "109.85,-7.60,110.20,-7.90"})
        url = "https://nominatim.openstreetmap.org/search?" + urlencode(params)
        try:
            request = Request(url, headers={
                "User-Agent": "TravelFit-academic-review/1.0 (small cached dataset review)",
            })
            with urlopen(request, timeout=15) as response:
                raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("One MB response cap exceeded")
            results = json.loads(raw)
            assert isinstance(results, list)
            snapshot = {
                "source_url": url, "query": query,
                "accessed_at_utc": datetime.now(timezone.utc).isoformat(),
                "license_url": "https://www.openstreetmap.org/copyright",
                "license": "ODbL 1.0", "attribution": "OpenStreetMap contributors",
                "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
                "results": results,
            }
            with path.open("x", encoding="utf-8") as handle:
                json.dump(snapshot, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(name + ": " + json.dumps(results, ensure_ascii=False), flush=True)
        except Exception as error:
            print(f"Not fetched: {name}: {type(error).__name__}: {error}", flush=True)
        time.sleep(1.1)


if __name__ == "__main__":
    main()
