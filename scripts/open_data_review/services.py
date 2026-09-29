"""C2: four *mapped* service classes in a straight-line radius, not availability."""

import math

from .schema import OsmPoint


SERVICE_CLASSES = ("transport", "healthcare", "atm_bank", "lodging")


def _haversine_km(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
    a1, a2 = math.radians(lat_a), math.radians(lat_b)
    dlat, dlon = a2 - a1, math.radians(lon_b - lon_a)
    h = math.sin(dlat / 2) ** 2 + math.cos(a1) * math.cos(a2) * math.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(h)))


def _classes(tags: dict[str, str]) -> set[str]:
    classes = set()
    if (
        tags.get("highway") == "bus_stop"
        or tags.get("public_transport") in {"platform", "station", "stop_position"}
        or tags.get("railway") in {"station", "halt"}
        or tags.get("amenity") in {"bus_station", "ferry_terminal"}
    ):
        classes.add("transport")
    if tags.get("amenity") in {"hospital", "clinic", "doctors", "pharmacy"}:
        classes.add("healthcare")
    if tags.get("amenity") in {"atm", "bank"}:
        classes.add("atm_bank")
    if tags.get("tourism") in {"hotel", "guest_house", "hostel", "motel"}:
        classes.add("lodging")
    return classes


def nearby_service_evidence(
    lat: float, lon: float, points: list[OsmPoint], radius_km: float = 2.0,
) -> dict[str, list[str]]:
    """Return OSM object references with snapshot dates for each mapped class.

    An empty class says only that this snapshot has no matching mapped object.
    It does not assert that the service does not exist in the real world.
    """
    if radius_km < 0 or not all(math.isfinite(v) for v in (lat, lon, radius_km)):
        raise ValueError("Coordinates and radius must be finite and radius nonnegative")
    found: dict[str, set[str]] = {key: set() for key in SERVICE_CLASSES}
    for point in points:
        if _haversine_km(lat, lon, point.lat, point.lon) > radius_km + 1e-12:
            continue
        for category in _classes(point.tags):
            found[category].add(f"{point.ref}@{point.snapshot_at}")
    return {key: sorted(found[key]) for key in SERVICE_CLASSES}


def service_score(evidence: dict[str, list[str]]) -> int:
    """Count present mapped service classes, never individual establishments."""
    return sum(bool(evidence.get(key)) for key in SERVICE_CLASSES)
