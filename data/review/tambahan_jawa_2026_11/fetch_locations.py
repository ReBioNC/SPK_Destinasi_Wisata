"""Pencarian lokasi OSM/Nominatim terarah untuk kandidat tambahan, dengan jejak sumber.

Hanya mengunduh bukti; tidak memilih kandidat atau mengubah data produksi.
Jalankan dari root repo: python data/review/tambahan_jawa_2026_11/fetch_locations.py
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
QUERIES = {
    "tasikardi": "Tasikardi, Serang, Banten, Indonesia",
    "gunung_kunci": "Taman Hutan Raya Gunung Kunci, Sumedang, Indonesia",
    "baturraden": "Lokawisata Baturraden, Banyumas, Indonesia",
    "botani_baturraden": "Taman Botani Baturraden, Banyumas, Indonesia",
    "sermo": "Waduk Sermo, Kulon Progo, Indonesia",
    "kiskendo": "Goa Kiskendo, Kulon Progo, Indonesia",
    "suroloyo": "Puncak Suroloyo, Kulon Progo, Indonesia",
    "trisik": "Pantai Trisik, Kulon Progo, Indonesia",
    "popoh": "Pantai Popoh, Tulungagung, Indonesia",
    "sidem": "Pantai Sidem, Tulungagung, Indonesia",
    "sine": "Pantai Sine, Tulungagung, Indonesia",
    "tawun": "Tawun, Kasreman, Ngawi, Indonesia",
    "minizoo_purworejo": "Mini Zoo, Purworejo, Indonesia",
    "kiskendo_gua": "Gua Kiskendo, Jatimulyo, Girimulyo, Kulon Progo",
    "kiskendo_short": "Kiskendo",
    "popoh_indah": "Pantai Indah Popoh, Besole, Besuki, Tulungagung",
    "sidem_short": "Sidem, Besole, Tulungagung",
    # Batch 2
    "krida_kudus": "Taman Krida Wisata, Kudus, Indonesia",
    "colo_kudus": "Colo, Dawe, Kudus, Indonesia",
    "tamanria_kudus": "Taman Ria, Kudus, Indonesia",
    "museum_kretek": "Museum Kretek, Kudus, Indonesia",
    "batu_seribu": "Batu Seribu, Sukoharjo, Indonesia",
    "makam_balakan": "Makam Balakan, Sukoharjo, Indonesia",
    "menara_teratai": "Menara Teratai, Purwokerto, Banyumas, Indonesia",
    "maskemambang": "Taman Maskemambang, Banyumas, Indonesia",
    "argowilis": "Pesanggrahan Argowilis, Tulungagung, Indonesia",
    "selokambang": "Selokambang, Lumajang, Indonesia",
    "ranu_klakah": "Ranu Klakah, Lumajang, Indonesia",
    "ranu_pakis": "Ranu Pakis, Lumajang, Indonesia",
    "maskemambang_purwokerto": "Taman Mas Kemambang, Purwokerto, Banyumas, Indonesia",
    # Batch 3
    "pandanaran": "Makam Sunan Pandanaran, Bayat, Klaten, Indonesia",
    "cokro": "Mata Air Cokro, Klaten, Indonesia",
    "sidoguro": "Bukit Sidoguro, Klaten, Indonesia",
    "jolotundo": "Umbul Jolotundo, Klaten, Indonesia",
    "deles": "Deles Indah, Klaten, Indonesia",
    "linggoasri": "Linggoasri, Pekalongan, Indonesia",
    "depok_pekalongan": "Pantai Depok, Pekalongan, Indonesia",
    "guci": "Guci, Bumijawa, Tegal, Indonesia",
    "purwahamba": "Purwahamba Indah, Tegal, Indonesia",
    "cacaban": "Waduk Cacaban, Tegal, Indonesia",
    "goa_lowo": "Goa Lowo, Trenggalek, Indonesia",
    "karanggongso": "Pantai Karanggongso, Trenggalek, Indonesia",
    "prigi": "Pantai Prigi, Trenggalek, Indonesia",
    "pelang": "Pantai Pelang, Trenggalek, Indonesia",
    # Batch 4
    "linggarjati": "Gedung Naskah Linggarjati, Kuningan, Indonesia",
    "kebunraya_kuningan": "Kebun Raya Kuningan, Indonesia",
}


def main():
    SOURCES.mkdir(parents=True, exist_ok=True)
    for name, query in QUERIES.items():
        path = SOURCES / f"nominatim_{name}.json"
        if path.exists():
            print(f"Cached: {name}", flush=True)
            continue
        params = {"q": query, "format": "jsonv2", "limit": 5, "countrycodes": "id", "extratags": 1}
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
