"""Ambil koordinat ibu kota kabupaten dari Nominatim (OSM) untuk registry kota asal.

Hanya mengunduh bukti; pemilihan koordinat dicatat di Dokumentasi.md.
Jalankan dari root repo: python data/review/kota_asal_2026_11/fetch_kota.py
Kebijakan Nominatim: satu permintaan per detik, User-Agent jelas, hasil di-cache.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCES = Path(__file__).resolve().parent / "sources"
# nama registry: query ibu kota kabupaten
QUERIES = {
    "kudus": "Kudus, Kabupaten Kudus, Jawa Tengah, Indonesia",
    "purworejo": "Purworejo, Kabupaten Purworejo, Jawa Tengah, Indonesia",
    "sumedang": "Sumedang, Kabupaten Sumedang, Jawa Barat, Indonesia",
    "tegal_slawi": "Slawi, Kabupaten Tegal, Jawa Tengah, Indonesia",
    "lumajang": "Lumajang, Kabupaten Lumajang, Jawa Timur, Indonesia",
    "ngawi": "Ngawi, Kabupaten Ngawi, Jawa Timur, Indonesia",
    "trenggalek": "Trenggalek, Kabupaten Trenggalek, Jawa Timur, Indonesia",
    "tulungagung": "Tulungagung, Kabupaten Tulungagung, Jawa Timur, Indonesia",
    # Query kota di atas tidak memberi titik pusat kota; pakai alun-alun ibu kota.
    "ngawi_alun_alun": "Alun-Alun Ngawi, Jawa Timur, Indonesia",
}


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, query in QUERIES.items():
        path = SOURCES / f"nominatim_{name}.json"
        if path.exists():
            print(f"Cached: {name}", flush=True)
            continue
        params = {"q": query, "format": "jsonv2", "limit": 5, "countrycodes": "id"}
        url = "https://nominatim.openstreetmap.org/search?" + urlencode(params)
        try:
            request = Request(url, headers={"User-Agent": "TravelFit-academic-review/1.0 (small cached dataset review)"})
            with urlopen(request, timeout=20) as response:
                raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("Batas respons 1 MB terlampaui")
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
            with path.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(snapshot, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(f"{name}: {len(results)} hasil", flush=True)
        except Exception as error:
            print(f"Tidak terambil: {name}: {type(error).__name__}: {error}", flush=True)
        time.sleep(1.2)


if __name__ == "__main__":
    main()
