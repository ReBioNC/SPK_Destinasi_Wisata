"""Latih K-Means offline; simpan label segmen untuk tampilan rekomendasi.

Centroid dipelajari dari 437 baris sumber Jawa. Baris simulasi 38 provinsi
hanya mendapat label centroid terdekat dan tetap ditandai sebagai simulasi.
"""

import json
from collections import Counter
from pathlib import Path

import numpy as np
from django.core.management.base import BaseCommand, CommandError

from recommender.models import Destination


def _fit_kmeans(data, k, seed=42, starts=10, max_iter=100):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(starts):
        centers = [data[rng.integers(len(data))]]
        for _ in range(1, k):
            d2 = np.min(((data[:, None, :] - np.array(centers)[None, :, :]) ** 2).sum(axis=2), axis=1)
            p = d2 / d2.sum() if d2.sum() else None
            centers.append(data[rng.choice(len(data), p=p)])
        centers = np.array(centers)
        for _ in range(max_iter):
            d2 = ((data[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            labels = d2.argmin(axis=1)
            updated = np.array([
                data[labels == j].mean(axis=0) if np.any(labels == j)
                else data[np.argmax(d2.min(axis=1))]
                for j in range(k)
            ])
            if np.allclose(centers, updated, rtol=0, atol=1e-6):
                break
            centers = updated
        d2 = ((data[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = d2.argmin(axis=1)
        inertia = float(d2[np.arange(len(data)), labels].sum())
        if best is None or inertia < best[0]:
            best = (inertia, centers, labels)
    return best


def _silhouette(data, labels):
    """Silhouette rata-rata dengan jarak Euclidean pada data pelatihan."""
    norms = (data ** 2).sum(axis=1)
    distances = np.sqrt(np.maximum(norms[:, None] + norms[None, :] - 2 * data @ data.T, 0))
    values = []
    for i, own in enumerate(labels):
        same = labels == own
        if same.sum() == 1:
            values.append(0.0)
            continue
        a = distances[i, same].sum() / (same.sum() - 1)
        b = min(distances[i, labels == other].mean()
                for other in set(labels) if other != own)
        values.append((b - a) / max(a, b) if max(a, b) else 0.0)
    return float(np.mean(values))


class Command(BaseCommand):
    help = "Latih K-Means pada data Jawa, evaluasi k=2..6, dan labeli destinasi."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Evaluasi tanpa menyimpan label atau laporan.")

    def handle(self, *args, **opts):
        destinations = list(Destination.objects.all().order_by("pk"))
        observed = [d for d in destinations if d.sumber_data == "csv_jawa"]
        if len(observed) < 3:
            raise CommandError("K-Means memerlukan sedikitnya 3 destinasi dari sumber csv_jawa.")

        categories = sorted({d.kategori for d in observed})
        # C4 pada data Jawa baru berupa penyebutan di deskripsi.
        # Memakainya di K-Means akan mengelompokkan kelengkapan metadata.
        facility_evidence = sum(d.facility_score() > 0 for d in observed)
        price_cap = float(np.percentile([d.harga_tiket for d in observed], 99))
        numeric = np.array([[min(d.harga_tiket, price_cap), d.rating] for d in observed], dtype=float)
        mean, scale = numeric.mean(axis=0), numeric.std(axis=0)
        scale[scale == 0] = 1

        def features(rows):
            nums = (np.array([[min(d.harga_tiket, price_cap), d.rating] for d in rows], dtype=float)
                    - mean) / scale
            one_hot = np.array([[float(d.kategori == c) for c in categories] for d in rows])
            return np.column_stack((nums, one_hot))

        training = features(observed)
        candidates = []
        min_cluster_size = max(5, round(len(observed) * 0.05))
        for k in range(2, min(6, len(observed) - 1) + 1):
            inertia, centers, labels = _fit_kmeans(training, k)
            if len(set(labels)) != k:
                continue
            score = _silhouette(training, labels)
            smallest = int(np.bincount(labels, minlength=k).min())
            candidates.append((k, score, inertia, centers, labels, smallest))
        if not candidates:
            raise CommandError("Tidak ada konfigurasi cluster yang valid.")
        viable = [row for row in candidates if row[5] >= min_cluster_size]
        k, score, inertia, centers, labels, _ = max(
            viable or candidates, key=lambda item: (item[1], -item[0]))
        all_features = features(destinations)
        all_labels = ((all_features[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)

        order = sorted(range(k), key=lambda j: np.mean([d.harga_tiket for d, c in zip(observed, labels) if c == j]))
        names = {}
        clusters = []
        for idx, cluster_id in enumerate(order, start=1):
            members = [d for d, c in zip(observed, labels) if c == cluster_id]
            avg_price = float(np.mean([d.harga_tiket for d in members]))
            avg_rating = float(np.mean([d.rating for d in members]))
            edge = max(1, k // 3)
            price_level = ("harga rendah" if idx <= edge else
                           "harga tinggi" if idx > k - edge else "harga menengah")
            rating_note = (" · rating tinggi" if avg_rating > float(mean[1]) + 0.05 else
                           " · rating rendah" if avg_rating < float(mean[1]) - 0.05 else "")
            dominant_category, category_count = Counter(d.kategori for d in members).most_common(1)[0]
            category_note = f" · {dominant_category}" if category_count / len(members) >= 0.5 else ""
            label = f"Segmen {idx} · {price_level}{category_note}{rating_note}"
            names[cluster_id] = label
            clusters.append({"label": label, "observed_rows": len(members),
                             "all_rows": int((all_labels == cluster_id).sum()),
                             "mean_price": round(avg_price, 2), "mean_rating": round(avg_rating, 3),
                             "dominant_category": dominant_category,
                             "mean_facility_score": round(float(np.mean([d.facility_score() for d in members])), 3)})

        report = {"method": "K-Means, k-means++ initialization, 10 starts, seed 42",
                  "training_source": "csv_jawa", "training_rows": len(observed),
                  "assigned_simulation_rows": len(destinations) - len(observed),
                  "ticket_price_cap_p99": round(price_cap, 2),
                  "capped_training_rows": sum(d.harga_tiket > price_cap for d in observed),
                  "minimum_cluster_size": min_cluster_size,
                  "features": ["ticket_price_z", "rating_z"]
                              + [f"category_{c}" for c in categories],
                  "excluded_feature": f"C4 dikecualikan dari clustering: fasilitas terindikasi pada {facility_evidence}/{len(observed)} data Jawa; kosong belum tentu tidak tersedia.",
                  "selected_k": k, "silhouette": round(score, 5), "inertia": round(inertia, 5),
                  "candidates": [{"k": row[0], "silhouette": round(row[1], 5),
                                  "inertia": round(row[2], 5), "smallest_cluster": row[5]}
                                 for row in candidates],
                  "clusters": clusters,
                  "limitation": "Fasilitas pada data Jawa diekstrak dari deskripsi; harga, rating, dan koordinat data simulasi tidak terverifikasi."}
        if not opts["dry_run"]:
            for destination, cluster_id in zip(destinations, all_labels):
                destination.cluster_label = names[int(cluster_id)]
            Destination.objects.bulk_update(destinations, ["cluster_label"], batch_size=500)
            report_path = Path(__file__).resolve().parents[3] / "reports" / "clustering" / "kmeans_evaluation.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.stdout.write(f"k={k} silhouette={score:.4f} inertia={inertia:.2f}"
                          + (" (dry-run)" if opts["dry_run"] else " — label tersimpan"))
