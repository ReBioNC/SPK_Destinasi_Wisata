"""Offline K-Means on every Java443 destination, using shared preprocessing."""
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
import numpy as np
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, DatabaseError
from recommender.data_pipeline import validate_artifacts
from recommender.models import Destination

def _save_labels_and_report(destinations, labels, names, report, path):
    """Stage file writes first; undo report publication if the DB transaction fails.

    This handles ordinary I/O/commit errors, not power-loss atomicity across the
    database and filesystem. A failed restoration retains its explicit backup.
    """
    staged = backup = None
    published = keep_backup = False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, filename = tempfile.mkstemp(prefix='.kmeans-stage-', dir=path.parent)
        os.close(descriptor)
        staged = Path(filename)
        staged.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n',
                          encoding='utf-8', newline='\n')
        if path.exists():
            descriptor, filename = tempfile.mkstemp(prefix='.kmeans-backup-', dir=path.parent)
            os.close(descriptor)
            backup = Path(filename)
            backup.write_bytes(path.read_bytes())
        with transaction.atomic():
            for destination, label in zip(destinations, labels):
                destination.cluster_label = names[int(label)]
            Destination.objects.bulk_update(destinations, ['cluster_label'], batch_size=500)
            os.replace(staged, path)
            staged = None
            published = True
    except (OSError, DatabaseError, ValueError) as error:
        if published:
            try:
                if backup is not None:
                    os.replace(backup, path)
                    backup = None
                else:
                    path.unlink(missing_ok=True)
            except OSError as recovery_error:
                keep_backup = True
                raise CommandError(f'Transaksi gagal; pemulihan laporan gagal. Backup: {backup}. '
                                   f'Periksa laporan {path} sebelum memakai model: {recovery_error}') from error
        raise CommandError(f'Label/laporan tidak tersimpan; transaksi dibatalkan: {error}') from error
    finally:
        for temporary in (staged, None if keep_backup else backup):
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass  # A leftover staging file is never an active report.


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
    help = "Latih seluruh 443 destinasi, evaluasi k=2..6, dan simpan label segmen."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--project-root", default=str(Path(__file__).resolve().parents[3]))

    def handle(self, *args, **options):
        root = Path(options["project_root"])
        try:
            result = validate_artifacts(root)
        except (ValueError, FileNotFoundError) as error:
            raise CommandError(str(error)) from error
        destinations = list(Destination.objects.order_by("source_id"))
        fingerprint = result.manifest["pipeline_fingerprint"]
        if len(destinations) != 443 or [d.source_id for d in destinations] != list(range(1,444)):
            raise CommandError("Database harus tepat 443 ID; jalankan import_destinations.")
        for destination, row in zip(destinations, result.destinations.to_dict("records")):
            if (destination.pipeline_fingerprint != fingerprint
                or destination.harga_tiket != row["price"]
                or destination.rating_model != row["c2_rating_for_model"]
                or destination.kategori != row["category_clean"]):
                raise CommandError("Database tidak sesuai snapshot preprocessing; impor ulang sebelum training.")
        parameters = result.manifest["feature_parameters"]
        columns = parameters["feature_columns"]
        training = result.features[columns].to_numpy(dtype=float)
        candidates = []
        minimum = max(5, round(len(destinations) * 0.05))
        for k in range(2, 7):
            inertia, centers, labels = _fit_kmeans(training, k, seed=42, starts=10)
            if len(set(labels)) != k:
                continue
            smallest = int(np.bincount(labels, minlength=k).min())
            candidates.append((k, _silhouette(training, labels), inertia, centers, labels, smallest))
        if not candidates:
            raise CommandError("Tidak ada konfigurasi cluster valid.")
        viable = [item for item in candidates if item[5] >= minimum]
        k, score, inertia, centers, labels, _ = max(viable or candidates, key=lambda item: (item[1], -item[0]))
        order = sorted(range(k), key=lambda j: np.mean([
            d.harga_tiket for d, label in zip(destinations, labels) if label == j]))
        names, clusters = {}, []
        for index, cluster_id in enumerate(order, 1):
            members = [d for d, label in zip(destinations, labels) if label == cluster_id]
            avg_price = float(np.mean([d.harga_tiket for d in members]))
            avg_rating = float(np.mean([d.calculation_rating() for d in members]))
            edge = max(1, k // 3)
            price_level = "harga rendah" if index <= edge else "harga tinggi" if index > k-edge else "harga menengah"
            rating_note = " · rating tinggi" if avg_rating > parameters["mean"][1]+0.05 else " · rating rendah" if avg_rating < parameters["mean"][1]-0.05 else ""
            category, count = Counter(d.kategori for d in members).most_common(1)[0]
            category_note = f" · {category}" if count/len(members) >= 0.5 else ""
            name = f"Segmen {index} · {price_level}{category_note}{rating_note}"
            names[cluster_id] = name
            clusters.append({"cluster_id": cluster_id, "label": name, "observed_rows": len(members),
                             "all_rows": len(members), "mean_price": round(avg_price,2),
                             "mean_rating": round(avg_rating,3), "dominant_category": category,
                             "mean_facility_score": round(float(np.mean([d.facility_score() for d in members])),3)})
        report = {
            "method": "K-Means, k-means++ initialization, 10 starts, seed 42",
            "training_source": "437 Kaggle + 6 curated Java",
            "training_rows": 443, "assigned_rows": 443, "assigned_simulation_rows": 0,
            "pipeline_version": result.manifest["pipeline_version"], "pipeline_fingerprint": fingerprint,
            "source_hashes": result.manifest["source_hashes"], "place_ids": list(range(1,444)),
            "rating_imputation": result.manifest["rating_imputation"],
            "features": columns, "feature_parameters": parameters,
            "ticket_price_cap_p99": parameters["ticket_price_cap_p99"],
            "capped_training_rows": sum(d.harga_tiket > parameters["ticket_price_cap_p99"] for d in destinations),
            "minimum_cluster_size": minimum, "selection_used_size_constraint": bool(viable),
            "selected_k": k, "silhouette": round(score,5), "inertia": round(inertia,5),
            "centroids": centers.tolist(),
            "assignments": [{"source_id": d.source_id, "cluster_id": int(label), "label": names[int(label)]}
                            for d, label in zip(destinations, labels)],
            "candidates": [{"k": item[0], "silhouette": round(item[1],5), "inertia": round(item[2],5),
                            "smallest_cluster": item[5]} for item in candidates],
            "clusters": clusters, "excluded_feature": parameters["excluded"],
            "limitation": "Rating Tahura diimputasi, C4/tag heuristik, koordinat Marina perlu review. Silhouette bukan akurasi rekomendasi; segmen tidak menyaring TOPSIS.",
        }
        if not options["dry_run"]:
            path = root / "reports/clustering/kmeans_evaluation.json"
            _save_labels_and_report(destinations, labels, names, report, path)
        self.stdout.write(f"training=443 assigned=443 k={k} silhouette={score:.4f} inertia={inertia:.2f}"
                          + (" (dry-run)" if options["dry_run"] else " — label dan laporan tersimpan"))
