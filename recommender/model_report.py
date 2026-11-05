"""Isi halaman /model/: membaca artefak K-Means dan menghitung ulang evaluasinya.

Modul ini tidak melatih model. Nilai model berasal dari
reports/clustering/kmeans_evaluation.json; fitur berasal dari CSV preprocessing.
Semua angka untuk template diformat di sini sebagai string, sehingga koordinat
SVG tidak terkena lokalisasi desimal Django.
"""
import csv
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

REPORT_PATH = "reports/clustering/kmeans_evaluation.json"
FEATURES_PATH = "data/processed/destinations_kmeans_features_java443.csv"
DESTINATIONS_PATH = "data/processed/destinations_clean_java443.csv"
EXAMPLE_ID = 1  # Monumen Nasional: contoh perhitungan pada halaman.
FEATURE_LABELS = {
    "c1_ticket_price_z": "Harga tiket (Z-score)", "c2_rating_z": "Rating (Z-score)",
    "category_alam": "Kategori alam", "category_bahari": "Kategori bahari",
    "category_belanja": "Kategori belanja", "category_budaya": "Kategori budaya",
    "category_hiburan": "Kategori hiburan", "category_religi": "Kategori religi",
}


def silhouette_samples(data, labels):
    """Nilai a(i), b(i), dan s(i) tiap baris dengan jarak Euclidean."""
    labels = np.asarray(labels)
    norms = (data ** 2).sum(axis=1)
    distances = np.sqrt(np.maximum(norms[:, None] + norms[None, :] - 2 * data @ data.T, 0))
    a, b, s = np.zeros(len(data)), np.zeros(len(data)), np.zeros(len(data))
    for i, own in enumerate(labels):
        same = labels == own
        if same.sum() == 1:
            continue
        a[i] = distances[i, same].sum() / (same.sum() - 1)
        b[i] = min(distances[i, labels == other].mean() for other in set(labels.tolist()) if other != own)
        s[i] = (b[i] - a[i]) / max(a[i], b[i]) if max(a[i], b[i]) else 0.0
    return a, b, s


def num(value, digits=3):
    """Desimal gaya Indonesia: 0,543 dan 1.234,5."""
    text = f"{value:,.{digits}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".").replace("-", "−")


def rupiah(value):
    return "Rp" + f"{value:,.0f}".replace(",", ".")


def _px(value):
    return f"{value:.2f}"


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _ticks(low, high, step):
    first = math.floor(low / step + 1e-9)
    last = math.ceil(high / step - 1e-9)
    return [round(i * step, 6) for i in range(first, last + 1)]


def _line_chart(candidates, key, step, selected_k, digits, name):
    """Satu seri per k. Dua ukuran beda skala memakai dua grafik, bukan dua sumbu."""
    width, height, left, right, top, bottom = 360, 230, 48, 14, 22, 40
    values = [c[key] for c in candidates]
    ticks = _ticks(0, max(values), step)
    y = lambda v: top + (height - top - bottom) * (1 - v / ticks[-1])
    span = max(c["k"] for c in candidates) - min(c["k"] for c in candidates)
    x = lambda k: left + (width - left - right) * (k - candidates[0]["k"]) / span
    points = [{"cx": _px(x(c["k"])), "cy": _px(y(c[key])), "k": c["k"], "selected": c["k"] == selected_k,
               "text": num(c[key], digits), "tip": f"k = {c['k']}", "name": name} for c in candidates]
    return {"width": width, "height": height, "left": left, "right": width - right, "tick_x": left - 8,
            "bottom": height - bottom, "axis_y": height - bottom + 20, "title_y": height - 4,
            "path": " ".join(f"{p['cx']},{p['cy']}" for p in points), "points": points,
            "ticks": [{"y": _px(y(t)), "text": num(t, 1 if step < 1 else 0)} for t in ticks]}


def _silhouette_plot(rows, clusters, mean_score):
    """Silhouette tiap destinasi, diurutkan per segmen; lebar segmen sebanding jumlah anggota."""
    width, height, left, right, top, bottom, gap = 720, 300, 48, 14, 16, 34, 16
    low = min(min(r["s"] for r in rows), 0.0)
    ticks = _ticks(low, max(r["s"] for r in rows), 0.2)
    y = lambda v: top + (height - top - bottom) * (ticks[-1] - v) / (ticks[-1] - ticks[0])
    usable = width - left - right - gap * (len(clusters) - 1)
    unit = usable / len(rows)
    groups, hover, cursor = [], [], left
    for index, cluster in enumerate(clusters):
        members = sorted((r for r in rows if r["cluster"] == cluster["cluster_id"]),
                         key=lambda r: (-r["s"], r["id"]))
        xs = [cursor + unit * (i + 0.5) for i in range(len(members))]
        zero = _px(y(0))
        top_line = " ".join(f"{_px(px)},{_px(y(m['s']))}" for px, m in zip(xs, members))
        groups.append({"slot": index + 1, "area": f"{_px(xs[0])},{zero} {top_line} {_px(xs[-1])},{zero}",
                       "line": top_line, "label": f"Segmen {index + 1}", "label_x": _px(cursor + unit * len(members) / 2)})
        hover += [{"x": round(px, 2), "y": round(y(m["s"]), 2), "value": num(m["s"]), "name": m["nama"],
                   "note": f"Segmen {index + 1}", "slot": index + 1} for px, m in zip(xs, members)]
        cursor += unit * len(members) + gap
    return {"width": width, "height": height, "left": left, "right": width - right, "tick_x": left - 8,
            "bottom": height - bottom, "axis_y": height - 10, "groups": groups, "hover": hover,
            "zero": _px(y(0)), "mean_y": _px(y(mean_score)), "mean_text": f"Rata-rata {num(mean_score)}",
            "mean_text_x": left + 8, "mean_text_y": _px(y(mean_score) + 18), "ticks": [{"y": _px(y(t)), "text": num(t, 1)} for t in ticks]}


def _scatter(rows, centroids):
    """Dua dari delapan fitur: harga dan rating dalam skala Z-score."""
    width, height, left, right, top, bottom = 720, 380, 48, 14, 16, 44
    xs, ys = [r["z_price"] for r in rows], [r["z_rating"] for r in rows]
    x_ticks, y_ticks = _ticks(min(xs), max(xs), 1), _ticks(min(ys), max(ys), 1)
    x = lambda v: left + (width - left - right) * (v - x_ticks[0]) / (x_ticks[-1] - x_ticks[0])
    y = lambda v: top + (height - top - bottom) * (y_ticks[-1] - v) / (y_ticks[-1] - y_ticks[0])
    points = [{"cx": _px(x(r["z_price"])), "cy": _px(y(r["z_rating"])), "slot": r["slot"]} for r in rows]
    hover = [{"x": round(x(r["z_price"]), 2), "y": round(y(r["z_rating"]), 2), "name": r["nama"],
              "value": f"{r['harga']} · rating {r['rating']}", "note": f"Segmen {r['slot']}", "slot": r["slot"]}
             for r in rows]
    centers = []
    for index, center in enumerate(centroids):
        cx, cy = x(center[0]), y(center[1])
        centers.append({"slot": index + 1, "cx": _px(cx), "cy": _px(cy),
                        "shape": f"{_px(cx)},{_px(cy - 9)} {_px(cx + 9)},{_px(cy)} {_px(cx)},{_px(cy + 9)} {_px(cx - 9)},{_px(cy)}",
                        "label": f"Pusat Segmen {index + 1}", "label_x": _px(cx), "label_y": _px(cy - 14)})
    return {"width": width, "height": height, "left": left, "right": width - right, "top": top, "tick_x": left - 8,
            "bottom": height - bottom, "points": points, "hover": hover, "centers": centers,
            "x_ticks": [{"x": _px(x(t)), "text": num(t, 0)} for t in x_ticks],
            "y_ticks": [{"y": _px(y(t)), "text": num(t, 0)} for t in y_ticks],
            "axis_y": height - bottom + 20, "title_y": height - 4, "title_x": _px((left + width - right) / 2)}


def _metrics(data, labels, centroids, inertia):
    k, n = len(centroids), len(data)
    total = float(((data - data.mean(axis=0)) ** 2).sum())
    between = total - inertia
    spread = [float(np.linalg.norm(data[labels == j] - centroids[j], axis=1).mean()) for j in range(k)]
    davies = float(np.mean([max((spread[i] + spread[j]) / np.linalg.norm(centroids[i] - centroids[j])
                                for j in range(k) if j != i) for i in range(k)]))
    return {"total": total, "between": between, "explained": between / total,
            "calinski": (between / (k - 1)) / (inertia / (n - k)), "davies": davies,
            "spread": spread, "center_distance": float(np.linalg.norm(centroids[0] - centroids[-1]))}


def _build(root):
    report = json.loads((root / REPORT_PATH).read_text(encoding="utf-8"))
    columns = report["features"]
    feature_rows = _read_csv(root / FEATURES_PATH)
    info = {int(r["place_id"]): r for r in _read_csv(root / DESTINATIONS_PATH)}
    assigned = {a["source_id"]: a["cluster_id"] for a in report["assignments"]}
    ids = [int(r["place_id"]) for r in feature_rows]
    if set(ids) != set(assigned) or set(ids) != set(info):
        raise ValueError("ID fitur, destinasi, dan label model tidak sama.")
    data = np.array([[float(r[c]) for c in columns] for r in feature_rows])
    labels = np.array([assigned[i] for i in ids])
    centroids = np.array(report["centroids"])
    a, b, s = silhouette_samples(data, labels)
    order = {c["cluster_id"]: i + 1 for i, c in enumerate(report["clusters"])}
    rows = []
    for index, place_id in enumerate(ids):
        row = info[place_id]
        rows.append({"id": place_id, "nama": row["place_name"], "kategori": row["category_clean"],
                     "cluster": int(labels[index]), "slot": order[int(labels[index])],
                     "a": float(a[index]), "b": float(b[index]), "s": float(s[index]),
                     "a_text": num(a[index]), "b_text": num(b[index]), "s_text": num(s[index]),
                     "harga": rupiah(float(row["price"])), "rating": num(float(row["c2_rating_for_model"]), 1),
                     "z_price": float(data[index, 0]), "z_rating": float(data[index, 1])})
    params = report["feature_parameters"]
    metrics = _metrics(data, labels, centroids, report["inertia"])
    candidates = report["candidates"]
    selected = report["selected_k"]
    minimum = report["minimum_cluster_size"]

    clusters = []
    for index, cluster in enumerate(report["clusters"]):
        cid = cluster["cluster_id"]
        scores = s[labels == cid]
        size = int((labels == cid).sum())
        center = centroids[cid]
        clusters.append({
            "slot": index + 1, "cluster_id": cid, "label": cluster["label"], "size": size,
            "share": num(100 * size / len(rows), 1), "share_width": _px(100 * size / len(rows)),
            "mean_price": rupiah(cluster["mean_price"]), "mean_rating": num(cluster["mean_rating"], 2),
            "center_price": rupiah(params["mean"][0] + center[0] * params["scale"][0]),
            "center_rating": num(params["mean"][1] + center[1] * params["scale"][1], 2),
            "dominant": cluster["dominant_category"], "s_mean": num(scores.mean()), "s_min": num(scores.min()),
            "s_max": num(scores.max()), "negative": int((scores < 0).sum()), "spread": num(metrics["spread"][cid]),
        })
    by_slot = [centroids[c["cluster_id"]] for c in clusters]

    categories = []
    for name in params["categories"]:
        j = columns.index(f"category_{name}")
        categories.append({"nama": name, "bars": [
            {"slot": c["slot"], "text": num(100 * by_slot[i][j], 1) + "%", "width": _px(100 * by_slot[i][j])}
            for i, c in enumerate(clusters)]})

    centroid_rows = []
    for j, column in enumerate(columns):
        values = [center[j] for center in by_slot]
        centroid_rows.append({"label": FEATURE_LABELS.get(column, column), "values": [num(v) for v in values],
                              "diff": num(abs(values[0] - values[-1])), "raw": abs(values[0] - values[-1])})
    strongest = max(centroid_rows, key=lambda row: row["raw"])

    example_index = ids.index(EXAMPLE_ID)
    example = rows[example_index]
    vector = data[example_index]
    distances = [float(np.linalg.norm(vector - centroids[c["cluster_id"]])) for c in clusters]
    other = next(c for c in clusters if c["cluster_id"] != example["cluster"])
    own = next(c for c in clusters if c["cluster_id"] == example["cluster"])
    source = info[EXAMPLE_ID]
    example_view = {
        "nama": example["nama"], "harga": example["harga"], "rating": example["rating"],
        "kategori": example["kategori"], "harga_raw": num(float(source["price"]), 0),
        "z_price": num(vector[0]), "z_rating": num(vector[1]),
        "mean_price": num(params["mean"][0], 2), "scale_price": num(params["scale"][0], 2),
        "mean_rating": num(params["mean"][1], 3), "scale_rating": num(params["scale"][1], 3),
        "vector": [{"label": FEATURE_LABELS.get(c, c), "value": num(v)} for c, v in zip(columns, vector)],
        "distances": [{"label": c["label"], "value": num(d), "slot": c["slot"]} for c, d in zip(clusters, distances)],
        "own_label": own["label"], "other_label": other["label"], "own_size": own["size"], "other_size": other["size"],
        "own_others": own["size"] - 1, "a": example["a_text"], "b": example["b_text"], "s": example["s_text"],
        "gap": num(example["b"] - example["a"]), "max": num(max(example["a"], example["b"])),
    }
    for candidate in candidates:
        candidate["silhouette_text"] = num(candidate["silhouette"], 5)
        candidate["inertia_text"] = num(candidate["inertia"], 2)
        candidate["eligible"] = candidate["smallest_cluster"] >= minimum
        candidate["selected"] = candidate["k"] == selected
    for prev, candidate in zip(candidates, candidates[1:]):
        candidate["drop_text"] = f"−{num(prev['inertia'] - candidate['inertia'], 2)}"

    score = float(s.mean())
    return {
        "available": True, "method": report["method"], "selected_k": selected, "minimum": minimum,
        "rows_count": len(rows), "feature_count": len(columns), "fingerprint": report["pipeline_fingerprint"],
        "silhouette_text": num(score, 5), "silhouette_short": num(score), "inertia_text": num(report["inertia"], 2),
        "stored_silhouette": report["silhouette"], "computed_silhouette": score,
        "negative_count": int((s < 0).sum()), "candidates": candidates, "clusters": clusters,
        "categories": categories, "centroid_rows": centroid_rows, "strongest": strongest, "example": example_view,
        "lowest": sorted(rows, key=lambda r: r["s"])[:5], "rows": rows,
        "cap": rupiah(report["ticket_price_cap_p99"]), "capped_rows": report["capped_training_rows"],
        "mean_price": rupiah(params["mean"][0]), "scale_price": rupiah(params["scale"][0]),
        "mean_rating": num(params["mean"][1], 3), "scale_rating": num(params["scale"][1], 3),
        "metrics": {"explained": num(100 * metrics["explained"], 1), "total": num(metrics["total"], 2),
                    "between": num(metrics["between"], 2), "calinski": num(metrics["calinski"], 2),
                    "davies": num(metrics["davies"], 3), "center_distance": num(metrics["center_distance"])},
        "chart_silhouette": _line_chart(candidates, "silhouette", 0.2, selected, 3, "Silhouette"),
        "chart_inertia": _line_chart(candidates, "inertia", 250, selected, 1, "Inertia"),
        "chart_samples": _silhouette_plot(rows, clusters, score),
        "chart_scatter": _scatter(rows, by_slot),
    }


@lru_cache(maxsize=4)
def _cached(root, stamp):
    return _build(Path(root))


def load_report(root):
    """Hasil dibaca ulang hanya bila salah satu artefak berubah."""
    root = Path(root)
    try:
        stamp = tuple((root / p).stat().st_mtime_ns for p in (REPORT_PATH, FEATURES_PATH, DESTINATIONS_PATH))
        return _cached(str(root), stamp)
    except (OSError, ValueError, KeyError, IndexError) as error:
        return {"available": False, "error": str(error)}
