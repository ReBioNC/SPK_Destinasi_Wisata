"""Impor gabungan destinasi: XLSX 38 provinsi (basis) + CSV Jawa (overlay).

- Basis: Dataset_Wisata_38_Provinsi.xlsx, sheet Destinasi_TravelFit_Ready.
- Koordinat: sheet Destinasi_Raw, join (nama, kota) case-insensitive.
- Overlay: data/processed/destinations_clean.csv + ratings_aggregated.csv,
  join (nama, kota); menimpa rating, tag, dan 4 flag fasilitas.
- Idempoten via update_or_create pada kunci natural (nama, kota).

Catatan: fas_penginapan selalu False karena tidak ada kolom sumber yang
berpadanan (flag accessibility/information_center tak dipetakan).
"""

from pathlib import Path

import openpyxl
import pandas as pd
from django.core.management.base import BaseCommand

from recommender.models import Destination

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
XLSX = BASE_DIR / "Dataset_Wisata_38_Provinsi.xlsx"
CLEAN_CSV = BASE_DIR / "data" / "processed" / "destinations_clean.csv"
RATINGS_CSV = BASE_DIR / "data" / "processed" / "ratings_aggregated.csv"


def norm(s):
    return str(s).strip().lower()


class Command(BaseCommand):
    help = "Impor destinasi dari XLSX 38 provinsi + overlay CSV Jawa."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Hitung tanpa menyimpan ke database.")

    def handle(self, *args, **opts):
        dry = opts["dry_run"]

        wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
        coords = {}
        ws_raw = wb["Destinasi_Raw"]
        h_raw = [c.value for c in next(ws_raw.iter_rows(min_row=1, max_row=1))]
        ir = {n: i for i, n in enumerate(h_raw)}
        for row in ws_raw.iter_rows(min_row=2, values_only=True):
            coords[(norm(row[ir["Place_Name"]]), norm(row[ir["City"]]))] = (
                row[ir["Lat"]], row[ir["Long"]])

        clean = pd.read_csv(CLEAN_CSV)
        rating_by_id = {}
        try:
            rag = pd.read_csv(RATINGS_CSV)
            rating_by_id = dict(zip(rag["place_id"], rag["user_rating_mean"]))
        except FileNotFoundError:
            pass
        overlay = {}
        for _, r in clean.iterrows():
            pid = r.get("place_id")
            rating = rating_by_id.get(pid) if pd.notna(pid) else None
            if rating is None or (isinstance(rating, float) and pd.isna(rating)):
                rating = r["c2_rating"]
            overlay[(norm(r["place_name"]), norm(r["city"]))] = {
                "rating": float(rating),
                "tags": "" if pd.isna(r["activity_tags"]) else str(r["activity_tags"]),
                "toilet": bool(r["facility_toilet_mentioned"]),
                "parkir": bool(r["facility_parking_mentioned"]),
                "warung": bool(r["facility_food_mentioned"]),
                "mushola": bool(r["facility_worship_mentioned"]),
            }

        ws = wb["Destinasi_TravelFit_Ready"]
        h = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
        ic = {n: i for i, n in enumerate(h)}
        basis = tanpa_koordinat = jawa = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            basis += 1
            nama, kota = str(row[ic["Place_Name"]]), str(row[ic["City"]])
            key = (norm(nama), norm(kota))
            lat, lon = coords.get(key, (None, None))
            if lat is None:
                tanpa_koordinat += 1
            ov = overlay.get(key)
            sumber = "xlsx38"
            rating = float(row[ic["c2_rating"]])
            tags = "" if row[ic["activity_tags"]] is None else str(row[ic["activity_tags"]])
            flags = {
                "fas_toilet": bool(row[ic["facility_toilet_mentioned"]]),
                "fas_parkir": bool(row[ic["facility_parking_mentioned"]]),
                "fas_warung": bool(row[ic["facility_food_mentioned"]]),
                "fas_mushola": bool(row[ic["facility_worship_mentioned"]]),
                "fas_penginapan": False,
            }
            if ov is not None:
                sumber = "csv_jawa"
                jawa += 1
                rating = ov["rating"]
                tags = ov["tags"]
                flags.update({"fas_toilet": ov["toilet"], "fas_parkir": ov["parkir"],
                              "fas_warung": ov["warung"], "fas_mushola": ov["mushola"]})
            if not dry:
                Destination.objects.update_or_create(
                    nama=nama, kota=kota,
                    defaults={
                        "provinsi": str(row[ic["Province"]]),
                        "kategori": str(row[ic["Category_Clean"]]),
                        "sub_kategori": "" if row[ic["Sub_Category"]] is None else str(row[ic["Sub_Category"]]),
                        "harga_tiket": int(row[ic["c1_ticket_price"]]),
                        "rating": rating,
                        "latitude": lat, "longitude": lon,
                        **flags,
                        "tag_aktivitas": tags,
                        "sumber_data": sumber,
                    })
        wb.close()
        basis_total = basis if dry else Destination.objects.count()

        # Fase 2: overlay + suplemen CSV Jawa. Baris yang cocok kunci natural
        # ditimpa; sisanya (nama sintetis XLSX tak sama dengan nama asli CSV)
        # diimpor sebagai baris baru agar data detail Jawa tidak hilang.
        jawa_overlay = jawa_baru = 0
        for _, r in clean.iterrows():
            nama, kota = str(r["place_name"]), str(r["city"])
            key = (norm(nama), norm(kota))
            ov = overlay[key]
            exists = Destination.objects.filter(nama=nama, kota=kota).exists()
            if exists:
                jawa_overlay += 1
            else:
                jawa_baru += 1
            if not dry:
                Destination.objects.update_or_create(
                    nama=nama, kota=kota,
                    defaults={
                        "provinsi": str(r["province"]),
                        "kategori": str(r["category_clean"]),
                        "sub_kategori": "",
                        "harga_tiket": int(r["c1_ticket_price"]),
                        "rating": ov["rating"],
                        "latitude": None if pd.isna(r["lat"]) else float(r["lat"]),
                        "longitude": None if pd.isna(r["long"]) else float(r["long"]),
                        "fas_toilet": ov["toilet"], "fas_parkir": ov["parkir"],
                        "fas_warung": ov["warung"], "fas_mushola": ov["mushola"],
                        "fas_penginapan": False,
                        "tag_aktivitas": ov["tags"],
                        "sumber_data": "csv_jawa",
                    })
        total = basis_total if dry else Destination.objects.count()
        self.stdout.write(
            f"basis={basis} overlay_jawa={jawa} tanpa_koordinat={tanpa_koordinat} "
            f"jawa_suplemen={jawa_baru} jawa_ditimpa={jawa_overlay} total={total}"
            + (" (dry-run)" if dry else ""))
