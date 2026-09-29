"""Parse a saved Overpass snapshot with explicit Indonesia-boundary provenance.

This module makes no network requests. OSM data © OpenStreetMap contributors,
ODbL 1.0: https://www.openstreetmap.org/copyright
"""

import math
import re

from .schema import Candidate, OsmPoint


# Use a smaller regional bbox *inside* the country area when making bounded
# requests; the boundary, not the bbox, excludes East Timor and sea neighbours.
INDONESIA_QUERY = '''[out:json][timeout:180];
rel["boundary"="administrative"]["admin_level"="2"]["ISO3166-1"="ID"];
map_to_area->.indonesia;
(
  nwr["tourism"~"^(attraction|museum|viewpoint|artwork|theme_park|zoo|aquarium|gallery)$"](area.indonesia);
  nwr["natural"~"^(beach|waterfall|cave_entrance|volcano)$"](area.indonesia);
  nwr["historic"~"^(monument|memorial|castle|ruins|archaeological_site)$"](area.indonesia);
  nwr["public_transport"](area.indonesia);
  nwr["highway"="bus_stop"](area.indonesia);
  nwr["railway"~"^(station|halt)$"](area.indonesia);
  nwr["amenity"~"^(bus_station|ferry_terminal|hospital|clinic|doctors|pharmacy|atm|bank)$"](area.indonesia);
  nwr["tourism"~"^(hotel|guest_house|hostel|motel)$"](area.indonesia);
);
out center tags;'''

ATTRACTIONS = {
    "tourism": {"attraction", "museum", "viewpoint", "artwork", "theme_park", "zoo", "aquarium", "gallery"},
    "natural": {"beach", "waterfall", "cave_entrance", "volcano"},
    "historic": {"monument", "memorial", "castle", "ruins", "archaeological_site"},
}
OSM_CATEGORY_MAP = {
    ("tourism", "museum"): "Budaya", ("tourism", "gallery"): "Budaya",
    ("tourism", "artwork"): "Budaya", ("tourism", "viewpoint"): "Cagar Alam",
    ("tourism", "theme_park"): "Taman Hiburan", ("tourism", "zoo"): "Taman Hiburan",
    ("tourism", "aquarium"): "Taman Hiburan",
    ("natural", "beach"): "Pantai", ("natural", "volcano"): "Gunung",
    ("natural", "waterfall"): "Cagar Alam", ("natural", "cave_entrance"): "Cagar Alam",
    **{("historic", tag): "Budaya" for tag in ATTRACTIONS["historic"]},
}


def snapshot_covers_radius(payload: dict, lat: float, lon: float, radius_km: float = 2.0) -> bool:
    """Require documented bounded scan covering the *entire* circular C2 search.

    A national area alone does not prove coverage for places near a border, so
    snapshots without an explicit bbox are not accepted for C2 verification.
    """
    query = payload.get("_source_query", "")
    if not _is_indonesia_query(query):
        return False
    matches = re.findall(r"\(area\.indonesia\)\(([-\d.,]+)\)", query)
    bbox = payload.get("_bbox")
    if matches and not bbox:
        raise ValueError("Bounded query must record its bbox")
    if not matches or not isinstance(bbox, list) or len(bbox) != 4:
        return False
    recorded = [float(part) for part in matches[0].split(",")]
    if len(matches) != 1 and any(match != matches[0] for match in matches):
        raise ValueError("Snapshot query uses inconsistent bounding boxes")
    if any(abs(float(a) - b) > 1e-9 for a, b in zip(bbox, recorded)):
        raise ValueError("Snapshot bbox differs from recorded query")
    south, west, north, east = recorded
    if not (-12 <= south < north <= 7 and 94 <= west < east <= 142):
        return False
    lat_margin = radius_km / 111.195
    lon_margin = radius_km / (111.195 * math.cos(math.radians(lat)))
    return south + lat_margin <= lat <= north - lat_margin and west + lon_margin <= lon <= east - lon_margin


def _is_indonesia_query(source_query: str) -> bool:
    return bool(
        re.search(r'\["ISO3166-1"\s*=\s*"ID"\]', source_query)
        and re.search(r'\["admin_level"\s*=\s*"2"\]', source_query)
        and "map_to_area" in source_query
        and re.search(r"\(area\.[A-Za-z_]+\)", source_query)
    )


def parse_osm_snapshot(payload: dict, snapshot_at: str, source_query: str) -> tuple[list[Candidate], list[OsmPoint]]:
    """Return named attractions and all georeferenced points for service scoring.

    A way/relation `center` is only a geometry proxy and is never verified as an
    actual entrance. Query provenance must be provided by the snapshot operator.
    """
    if not _is_indonesia_query(source_query):
        raise ValueError("Snapshot needs a recorded Indonesia admin-2 boundary query")
    return _parse_elements(payload, snapshot_at)


def parse_geofabrik_snapshot(payload: dict) -> tuple[list[Candidate], list[OsmPoint]]:
    """Parse a known regional extract; item-level province is *not* inferred."""
    source_url = payload.get("_source_url", "")
    if (payload.get("_source_kind") != "geofabrik_maluku"
            or not source_url.startswith("https://download.geofabrik.de/asia/indonesia/maluku-")
            or not source_url.endswith(".osm.pbf")):
        raise ValueError("Unknown Geofabrik extract provenance")
    return _parse_elements(payload, payload.get("_snapshot_at", ""))


def _parse_elements(payload: dict, snapshot_at: str) -> tuple[list[Candidate], list[OsmPoint]]:
    if not snapshot_at or not isinstance(payload.get("elements"), list):
        raise ValueError("Snapshot date and Overpass elements are required")
    candidates, points, seen = [], [], set()
    for item in payload["elements"]:
        osm_type, osm_id = item.get("type"), item.get("id")
        if osm_type not in {"node", "way", "relation"} or not isinstance(osm_id, int):
            continue
        key = (osm_type, osm_id)
        if key in seen:
            continue
        seen.add(key)
        geometry_origin = "node" if osm_type == "node" else "center_unverified"
        geo = item if osm_type == "node" else item.get("center") or {}
        try:
            lat, lon = float(geo["lat"]), float(geo["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        tags = {str(k): str(v) for k, v in (item.get("tags") or {}).items()}
        point = OsmPoint(osm_type, osm_id, lat, lon, tags, geometry_origin, snapshot_at)
        points.append(point)
        name = tags.get("name", "").strip()
        if name and any(tags.get(k) in values for k, values in ATTRACTIONS.items()):
            candidates.append(Candidate(
                candidate_id=f"osm:{point.ref}", origin="osm", name=name,
                city=tags.get("addr:city", ""), province=tags.get("addr:province", ""),
                source_row_id=point.ref, source_path="https://www.openstreetmap.org/" + point.ref,
                raw=tags, lat=lat, lon=lon, geometry_origin=geometry_origin,
            ))
    return candidates, points
