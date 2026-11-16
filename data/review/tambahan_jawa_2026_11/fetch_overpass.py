"""Pencarian nama OSM dalam kotak wilayah (Overpass) untuk kandidat yang tidak ditemukan Nominatim.

Hanya mengunduh bukti dan menyimpannya; pemilihan objek dilakukan saat review.
Jalankan dari root repo: python data/review/tambahan_jawa_2026_11/fetch_overpass.py
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCES = Path(__file__).resolve().parent / "sources"
ENDPOINTS = ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter")
# nama: (regex nama, bbox selatan,barat,utara,timur)
SEARCHES = {
    "gunung_kunci": ("Kunci", (-6.88, 107.88, -6.82, 107.95)),
    "kiskendo": ("Kiskendo", (-7.80, 110.05, -7.70, 110.15)),
    "sidem": ("Sidem", (-8.30, 111.75, -8.22, 111.85)),
    "popoh": ("Popoh", (-8.30, 111.75, -8.22, 111.85)),
    "tawun": ("Tawun", (-7.45, 111.45, -7.38, 111.52)),
    "minizoo_purworejo": ("([Mm]ini ?[Zz]oo|[Kk]ebun [Bb]inatang)", (-7.76, 109.95, -7.66, 110.08)),
}


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, (pattern, (south, west, north, east)) in SEARCHES.items():
        path = SOURCES / f"overpass_{name}.json"
        if path.exists():
            print(f"Cached: {name}", flush=True)
            continue
        query = (f'[out:json][timeout:25];nwr["name"~"{pattern}"]({south},{west},{north},{east});'
                 "out center tags;")
        try:
            raw = endpoint = None
            for endpoint in ENDPOINTS:
                try:
                    request = Request(endpoint + "?" + urlencode({"data": query}),
                                      headers={"User-Agent": "TravelFit-academic-review/1.0 (small cached dataset review)"})
                    with urlopen(request, timeout=60) as response:
                        raw = response.read(2 * 1024 * 1024 + 1)
                    break
                except OSError as error:
                    print(f"  {endpoint}: {error}", flush=True)
                    time.sleep(3)
            if raw is None:
                raise OSError("Semua endpoint Overpass gagal")
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("Batas respons 2 MB terlampaui")
            payload = json.loads(raw)
            snapshot = {
                "_endpoint": endpoint, "query": query,
                "accessed_at_utc": datetime.now(timezone.utc).isoformat(),
                "license_url": "https://www.openstreetmap.org/copyright",
                "license": "ODbL 1.0", "attribution": "OpenStreetMap contributors",
                "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
                "elements": payload.get("elements", []),
            }
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(snapshot, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(f"{name}: {len(snapshot['elements'])} elemen", flush=True)
        except Exception as error:
            print(f"Tidak terambil: {name}: {type(error).__name__}: {error}", flush=True)
        time.sleep(2)


if __name__ == "__main__":
    main()
