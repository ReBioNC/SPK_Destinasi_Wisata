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
OSRM_TABLE_URL = ("https://router.project-osrm.org/table/v1/driving/"
                  "{coords}?sources=0&annotations=distance")
TABLE_CHUNK = 100  # batas aman jumlah titik per request Table API.
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


def jarak_table(lat0, lon0, titik_list, moda="mobil"):
    """Batch jarak dari satu titik ke banyak titik via OSRM Table API.

    Mengembalikan list [(km, sumber)] sejajar titik_list; titik yang gagal
    dilewati (pemanggil jatuh ke jarak_darat per titik). Satu chunk =
    satu request network.
    """
    hasil = []
    for i in range(0, len(titik_list), TABLE_CHUNK):
        chunk = titik_list[i:i + TABLE_CHUNK]
        coords = ";".join([f"{lon0},{lat0}"] +
                          [f"{lon},{lat}" for lat, lon in chunk])
        try:
            _throttle()
            data = json.loads(_ambil_osrm(
                OSRM_TABLE_URL.format(coords=coords)).decode("utf-8"))
            baris = (data.get("distances") or [[]])[0]
            if data.get("code") != "Ok" or len(baris) < len(chunk) + 1:
                raise ValueError(f"OSRM table: {data.get('code')}")
        except (URLError, ValueError, KeyError, OSError) as exc:
            print(f"OSRM table gagal ({exc}); titik dilewati.")
            hasil.extend([None] * len(chunk))
            continue
        for (lat, lon), meter in zip(chunk, baris[1:]):
            if meter is None:
                hasil.append(None)
                continue
            km = float(meter) / 1000.0
            JarakCache.objects.update_or_create(
                asal=_kunci(lat0, lon0), tujuan=_kunci(lat, lon), moda=moda,
                defaults={"jarak_km": km, "sumber": "osrm"})
            hasil.append((km, "osrm"))
    return hasil
