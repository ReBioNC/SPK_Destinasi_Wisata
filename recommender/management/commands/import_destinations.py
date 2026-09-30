"""Replace active destinations atomically from validated Java443 artifacts."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import uuid

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from recommender.data_pipeline import validate_artifacts
from recommender.models import Destination

BASE_DIR = Path(__file__).resolve().parents[3]
PROVINSI_ALIAS = {"DI Yogyakarta": "Daerah Istimewa Yogyakarta"}
FACILITIES = {
    "fas_toilet": "toilet", "fas_parkir": "parking", "fas_warung": "food",
    "fas_mushola": "worship", "fas_accessibility": "accessibility",
    "fas_information_center": "information_center",
}
TICKET_SOURCES = {
    438: ("https://jdih.bantenprov.go.id/storage/places/peraturan/2024pd0036001_1706502771.pdf", 261, "Pengunjung umum Nusantara per hari"),
    439: ("https://peraturan.bpk.go.id/Download/403089/2025pd3602001.pdf", 232, "Pengunjung umum"),
    440: ("https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf", 242, "Tarif dasar per orang"),
    441: ("https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf", 242, "Tarif dasar per orang"),
    442: ("https://peraturan.bpk.go.id/Download/414805/3306pd2026001.pdf", 242, "Hari biasa Rp8.000; hari besar/libur Rp10.000"),
    443: ("https://bakeu.ngawikab.go.id/home/public/files/ppd/PERDA%20NO%2010%20TAHUN%202023.pdf", 122, "Domestik dewasa per kunjungan"),
}


def kanon_provinsi(nama):
    return PROVINSI_ALIAS.get(str(nama).strip(), str(nama).strip())


def backup_sqlite(project_root):
    """Use SQLite backup API (also captures committed WAL); never commit sessions."""
    name = str(connection.settings_dict["NAME"])
    if connection.vendor != "sqlite" or name == ":memory:" or "mode=memory" in name:
        return None
    source = Path(name).resolve()
    if not source.is_file():
        return None
    directory = Path(project_root) / "archive/local_backups"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = directory / f"travelfit-before-java443-{stamp}-{uuid.uuid4().hex[:8]}.sqlite3"
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as original:
        with sqlite3.connect(target) as copy:
            original.backup(copy)
    return target


def _text(value):
    return "" if pd.isna(value) else str(value)


def _defaults(row, fingerprint):
    ticket_url, page, tariff_note = TICKET_SOURCES.get(int(row["place_id"]),
        (row["source_url"], None, "Harga snapshot dataset Kaggle; bukan jaminan tarif transaksi terkini."))
    provenance = {key: _text(row[key]) for key in
        ("source_dataset", "source_url", "rating_status", "rating_source_url", "rating_access_date")}
    provenance.update({"ticket_source_url": ticket_url, "ticket_pdf_page": page,
                       "tariff_note": tariff_note,
                       "coordinate_source": "OpenStreetMap (ODbL, © OpenStreetMap contributors)" if row["place_id"] > 437 else "Koordinat snapshot Kaggle",
                       "time_minutes": None if pd.isna(row["time_minutes"]) else float(row["time_minutes"])})
    quality = {
        "coordinate_review_required": bool(row["coordinate_review_required"]),
        "coordinate_review_note": _text(row["coordinate_review_note"]),
        "issues": _text(row["data_quality_issues"]).split("|") if _text(row["data_quality_issues"]) else [],
        "rating_model_note": _text(row["rating_model_note"]),
        "facility_review_note": _text(row["facility_review_note"]),
        "facility_description_missing": bool(row["facility_description_missing"]),
    }
    return {
        "nama": row["place_name"], "kota": row["city"], "provinsi": kanon_provinsi(row["province"]),
        "kategori": row["category_clean"], "harga_tiket": int(row["price"]),
        "rating": None if pd.isna(row["rating"]) else float(row["rating"]),
        "rating_model": float(row["c2_rating_for_model"]), "rating_imputed": bool(row["rating_imputed"]),
        "description": _text(row["description"]), "latitude": float(row["lat"]),
        "longitude": float(row["long"]), "tag_aktivitas": _text(row["activity_tags"]),
        "sumber_data": "kaggle_java" if row["place_id"] <= 437 else "curated_java",
        "provenance": provenance, "data_quality": quality, "pipeline_fingerprint": fingerprint,
        **{field: bool(row[f"facility_{key}_mentioned"]) for field, key in FACILITIES.items()},
    }


class Command(BaseCommand):
    help = "Impor atomik 437 Kaggle + 6 destinasi kurasi Jawa; backup sebelum penggantian."

    def add_arguments(self, parser):
        parser.add_argument("--project-root", default=str(BASE_DIR))
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--backup-only", action="store_true", help="Backup sebelum migrate, tanpa query schema destinasi.")

    def handle(self, *args, **options):
        root = Path(options["project_root"])
        if options["backup_only"]:
            path = backup_sqlite(root)
            self.stdout.write(f"Backup: {path or 'tidak diperlukan (database memory/belum ada)'}")
            return
        try:
            result = validate_artifacts(root)
        except (ValueError, FileNotFoundError) as error:
            raise CommandError(str(error)) from error
        fingerprint = result.manifest["pipeline_fingerprint"]
        rows = result.destinations.to_dict("records")
        ids = [int(row["place_id"]) for row in rows]
        existing = list(Destination.objects.values("pk", "source_id", "nama", "kota", "pipeline_fingerprint"))
        by_id = {row["source_id"]: row for row in existing if row["source_id"] is not None}
        by_name = {(row["nama"], row["kota"]): row for row in existing if row["source_id"] is None}
        matched = [by_id.get(int(row["place_id"])) or by_name.get((row["place_name"], row["city"])) for row in rows]
        retained_pks = {record["pk"] for record in matched if record}
        created = sum(record is None for record in matched)
        updated, deleted = 443 - created, len(existing) - len(retained_pks)
        if options["dry_run"]:
            self.stdout.write(f"DRY RUN: input=443 created={created} updated={updated} deleted={deleted}; tanpa perubahan.")
            return
        backup = backup_sqlite(root)
        if backup:
            self.stdout.write(f"Backup: {backup}")
        with transaction.atomic():
            for row, record in zip(rows, matched):
                defaults = _defaults(row, fingerprint)
                # Keep training only on an unchanged snapshot.
                if record is None or record["pipeline_fingerprint"] != fingerprint:
                    defaults["cluster_label"] = ""
                destination = Destination.objects.get(pk=record["pk"]) if record else Destination()
                destination.source_id = int(row["place_id"])
                for key, value in defaults.items():
                    setattr(destination, key, value)
                destination.save()
            Destination.objects.exclude(source_id__in=ids).delete()
            if Destination.objects.count() != 443:
                raise CommandError("Retensi database gagal; transaksi dibatalkan.")
        self.stdout.write(f"input=443 created={created} updated={updated} deleted={deleted} total=443 fingerprint={fingerprint}")
