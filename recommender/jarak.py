"""Layanan jarak darat: cache DB -> OSRM (throttle 1 req/detik) -> fallback.

Sumber dikembalikan apa adanya ("cache"/"osrm"/"fallback") agar tampil
di rincian biaya sebagai provenance. Selalu mengembalikan angka —
tak pernah melempar saat network gagal.
"""

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from recommender.models import JarakCache
from recommender.spk import geo

OSRM_URL = ("https://router.project-osrm.org/route/v1/driving/"
            "{lon1},{lat1};{lon2},{lat2}?overview=false")
USER_AGENT = "TravelFit-SPK/1.0 (penelitian akademik; kontak via repo)"
TIMEOUT_DETIK = 15
FAKTOR_JALAN = 1.3  # Haversine lurus -> pendekatan jarak jalan.

_TERAKHIR = 0.0


def _kunci(lat, lon):
    return f"{round(lat, 4)},{round(lon, 4)}"


def _ambil_osrm(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=TIMEOUT_DETIK) as res:
        return res.read()


def _throttle():
    global _TERAKHIR
    jeda = 1.0 - (time.monotonic() - _TERAKHIR)
    if jeda > 0:
        time.sleep(jeda)
    _TERAKHIR = time.monotonic()


def jarak_darat(lat1, lon1, lat2, lon2, moda="mobil"):
    """(jarak_km, sumber). Cache dulu; OSRM bila perlu; fallback bila gagal."""
    asal, tujuan = _kunci(lat1, lon1), _kunci(lat2, lon2)
    hit = JarakCache.objects.filter(asal=asal, tujuan=tujuan, moda=moda).first()
    if hit is not None:
        return hit.jarak_km, "cache"
    try:
        _throttle()
        data = json.loads(_ambil_osrm(OSRM_URL.format(
            lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2)).decode("utf-8"))
        if data.get("code") != "Ok" or not data.get("routes"):
            raise ValueError(f"OSRM: {data.get('code')}")
        km = float(data["routes"][0]["distance"]) / 1000.0
        sumber = "osrm"
    except (URLError, ValueError, KeyError, OSError) as exc:
        print(f"OSRM gagal ({exc}); fallback Haversine x {FAKTOR_JALAN}.")
        km = geo.haversine(lat1, lon1, lat2, lon2) * FAKTOR_JALAN
        sumber = "fallback"
    JarakCache.objects.update_or_create(
        asal=asal, tujuan=tujuan, moda=moda,
        defaults={"jarak_km": km, "sumber": sumber})
    return km, sumber
