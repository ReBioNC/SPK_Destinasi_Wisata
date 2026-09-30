"""Pure shared Java443 transformations; no database or network side effects."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

PIPELINE_VERSION = "java443-v1"
SOURCE_PATHS = (
    "data/raw/tourism_with_id.csv",
    "data/review/gabungan_jawa/destinasi_jawa_review.csv",
    "data/review/gabungan_jawa/google_maps_rating_review.json",
    "data/raw/tourism_rating.csv",
)
OUTPUT_PATHS = {
    "destinations": "data/processed/destinations_clean_java443.csv",
    "features": "data/processed/destinations_kmeans_features_java443.csv",
    "summary": "reports/preprocessing/preprocessing_java443_summary.json",
    "manifest": "reports/preprocessing/preprocessing_java443_manifest.json",
}
BASE_URL = "https://raw.githubusercontent.com/akhiyarwaladi/indonesia_tourism/main/tourism_with_id.csv"


@dataclass
class PipelineResult:
    destinations: pd.DataFrame
    features: pd.DataFrame
    manifest: dict
    summary: dict


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _fingerprint(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _check_ids(frame):
    if len(frame) != 443 or not frame.place_id.is_unique or set(frame.place_id) != set(range(1, 444)):
        raise ValueError("Retensi wajib tepat 443 ID unik (1–443); ekspor/impor dibatalkan.")


def normalize_destinations(raw: pd.DataFrame) -> pd.DataFrame:
    destinations = raw.copy()
    def snake_case(value):
        return re.sub(r'[^0-9a-zA-Z]+', '_', str(value).strip()).strip('_').lower()

    destinations.columns = [snake_case(c) for c in destinations.columns]
    destinations = destinations.loc[:, ~destinations.columns.str.startswith('unnamed')].copy()

    for column in ['place_name', 'description', 'category', 'city']:
        destinations[column] = destinations[column].astype('string').str.replace(r'\s+', ' ', regex=True).str.strip()
    for column in ['place_id', 'price', 'rating', 'time_minutes', 'lat', 'long']:
        destinations[column] = pd.to_numeric(destinations[column], errors='coerce')

    # Pertahankan Marina beserta koordinat sumber; hanya tandai konflik yang diketahui.
    destinations['coordinate_review_required'] = (destinations['place_id'].eq(9)
        & destinations['place_name'].eq('Pelabuhan Marina')
        & np.isclose(destinations['lat'], 1.07888)
        & np.isclose(destinations['long'], 103.931398))
    destinations['coordinate_review_note'] = ''
    destinations.loc[destinations['coordinate_review_required'], 'coordinate_review_note'] = 'Label Jakarta bertentangan dengan koordinat sumber di luar Jawa; baris dipertahankan sesuai keputusan pengguna.'
    QUALITY_CHECKS = {
        'id_missing': destinations['place_id'].isna(),
        'id_duplicate': destinations['place_id'].duplicated(keep=False),
        'name_missing': destinations['place_name'].isna() | destinations['place_name'].eq('').fillna(False),
        'price_invalid': ~destinations['price'].ge(0),
        'rating_missing': destinations['rating'].isna(),
        'rating_out_of_range': destinations['rating'].notna() & ~destinations['rating'].between(1, 5),
        'latitude_invalid': ~destinations['lat'].between(-90, 90),
        'longitude_invalid': ~destinations['long'].between(-180, 180),
        'coordinate_location_conflict': destinations['coordinate_review_required'],
    }
    destinations['data_quality_issues'] = ''
    for issue, mask in QUALITY_CHECKS.items():
        destinations.loc[mask, 'data_quality_issues'] += issue + '|'
    destinations['data_quality_issues'] = destinations['data_quality_issues'].str.rstrip('|')
    # 2. Seragamkan wilayah dan kategori.
    CITY_TO_PROVINCE = {
        'Jakarta': 'DKI Jakarta', 'Bandung': 'Jawa Barat',
        'Semarang': 'Jawa Tengah', 'Yogyakarta': 'DI Yogyakarta',
        'Surabaya': 'Jawa Timur',
        'Pandeglang': 'Banten', 'Lebak': 'Banten',
        'Purworejo': 'Jawa Tengah', 'Ngawi': 'Jawa Timur',
    }
    CATEGORY_MAP = {
        'budaya': 'budaya', 'taman hiburan': 'hiburan',
        'cagar alam': 'alam', 'pusat perbelanjaan': 'belanja',
        'tempat ibadah': 'religi', 'bahari': 'bahari',
    }
    destinations['province'] = destinations['city'].map(CITY_TO_PROVINCE).astype('string')
    destinations['category_original'] = destinations['category']
    destinations['category_clean'] = destinations['category'].str.casefold().map(CATEGORY_MAP).astype('string')
    return destinations


def add_facilities(frame: pd.DataFrame) -> pd.DataFrame:
    destinations = frame.copy()
    # 4. Bentuk fitur fasilitas C4 dan tag aktivitas untuk C6.
    # Keduanya masih heuristik dari deskripsi dan perlu verifikasi untuk penelitian final.
    FACILITY_KEYWORDS = {
        'toilet': ['toilet', 'kamar mandi', 'wc umum'],
        'parking': ['parkir', 'parkiran', 'parking'],
        'food': ['warung', 'restoran', 'rumah makan', 'kafe', 'cafe', 'kuliner'],
        'worship': ['mushola', 'musala', 'masjid', 'tempat ibadah', 'gereja', 'pura', 'vihara'],
        'accessibility': ['disabilitas', 'difabel', 'kursi roda', 'wheelchair', 'aksesibel'],
        'information_center': ['pusat informasi', 'information center', 'layanan informasi'],
    }
    ACTIVITY_KEYWORDS = {
        'hiking': ['hiking', 'mendaki', 'pendakian', 'trekking'],
        'fotografi': ['fotografi', 'spot foto', 'berfoto', 'pemandangan', 'panorama'],
        'snorkeling': ['snorkeling', 'snorkel'],
        'diving': ['diving', 'menyelam', 'selam'],
        'camping': ['camping', 'berkemah', 'bumi perkemahan'],
        'kuliner': ['kuliner', 'makanan khas', 'jajanan', 'warung', 'restoran'],
        'sejarah': ['sejarah', 'bersejarah', 'peninggalan', 'museum', 'monumen'],
        'budaya': ['budaya', 'tradisi', 'kesenian', 'keraton'],
        'belanja': ['belanja', 'pusat perbelanjaan', 'pasar', 'mal', 'mall'],
        'berenang': ['berenang', 'kolam renang', 'waterpark', 'water park'],
        'edukasi': ['edukasi', 'pendidikan', 'belajar', 'museum'],
        'religi': ['ziarah', 'religi', 'ibadah', 'masjid', 'gereja', 'pura', 'vihara'],
        'rekreasi_keluarga': ['keluarga', 'wahana', 'taman bermain', 'taman hiburan'],
    }
    CATEGORY_TAGS = {
        'budaya': {'budaya'}, 'belanja': {'belanja'},
        'religi': {'religi'}, 'hiburan': {'rekreasi_keluarga'},
    }

    def normalize_text(value):
        return re.sub(r'\s+', ' ', str(value).casefold()).strip() if pd.notna(value) else ''

    def contains_keyword(text, keyword):
        escaped = re.escape(keyword.casefold()).replace(r'\ ', r'\s+')
        return re.search(rf'(?<!\w){escaped}(?!\w)', text) is not None

    description_text = destinations['description'].map(normalize_text)
    facility_columns = []
    for facility, keywords in FACILITY_KEYWORDS.items():
        column = f'facility_{facility}_mentioned'
        destinations[column] = description_text.map(
            lambda text, keys=keywords: int(any(contains_keyword(text, key) for key in keys))
        )
        facility_columns.append(column)
    # Review konteks: ID + nama + frasa harus cocok agar koreksi tidak salah sasaran.
    # Nilai 0 berarti tidak ada penyebutan yang diterima, bukan bukti fasilitas tidak ada.
    FACILITY_CONTEXT_REVIEW = {
        18: ('Museum Bank Indonesia', 'gereja ini dibongkar', ['worship'], 'Gereja dalam cerita sejarah telah dibongkar.'),
        57: ('Taman Lapangan Banteng', 'tidak jauh dari gereja katedral', ['worship'], 'Gereja adalah lokasi lain di dekat taman.'),
        94: ('Sumur Gumuling', 'pada masa lalu', ['worship'], 'Fungsi ibadah masa lalu, bukan fasilitas aktif terkonfirmasi.'),
        115: ('Monumen Sanapati', 'di taman depan gereja', ['worship'], 'Gereja adalah penanda lokasi di luar monumen.'),
        149: ('Goa Cerme', 'rencana pendirian masjid', ['worship'], 'Masjid disebut dalam cerita sejarah.'),
        176: ('Museum Gunung Merapi', 'ke depan juga akan dilengkapi', ['parking', 'information_center'], 'Parkir disebut sebagai rencana; layanan informasi adalah fungsi museum, bukan fasilitas terpisah yang dipastikan.'),
        213: ('Gedung Sate', 'gaya atap pura bali', ['worship'], 'Pura adalah perbandingan gaya arsitektur.'),
        232: ('Bukit Moko', 'kawasan bandung mampu menarik', ['food'], 'Kuliner dibahas sebagai daya tarik Bandung secara umum.'),
        249: ('Upside Down World Bandung', 'ruangan dengan tema', ['toilet'], 'Kamar mandi adalah ruangan bertema untuk foto.'),
        254: ('Teras Cikapundung BBWS', 'sebelumnya, taman ini', ['food'], 'Warung ada dalam cerita kondisi sebelumnya, bukan fasilitas saat ini yang dipastikan.'),
        270: ('Bukit Bintang', 'kuala lumpur, malaysia', ['food'], 'Deskripsi membahas tempat di negara lain; tidak dipakai sebagai bukti fasilitas record Bandung.'),
        295: ('Museum Nike Ardilla', 'hard rock cafe', ['food'], 'Cafe disebut sebagai perbandingan konsep desain.'),
        298: ('Gunung Lalakon', 'batu warung', ['food'], 'Batu Warung adalah nama batu, bukan warung makan.'),
        347: ('Taman Pandanaran', 'untuk mendapatkan parkir di sini cukup susah', ['parking'], 'Keluhan mencari parkir tidak mengonfirmasi area parkir destinasi.'),
        353: ('Taman Srigunting', 'di sisi barat terdapat gereja blenduk', ['worship'], 'Gereja adalah bangunan tetangga, bukan fasilitas taman.'),
        441: ('Pantai Jatimalang', 'bukan pintu masuk atau area parkir terverifikasi', ['parking'], 'Penyangkalan verifikasi koordinat, bukan bukti fasilitas parkir.'),
    }
    destinations['facility_keyword_score'] = destinations[facility_columns].mean(axis=1)
    destinations['facility_description_missing'] = description_text.eq('').astype(int)
    destinations['facility_review_note'] = ''
    for place_id, (name, phrase, rejected, note) in FACILITY_CONTEXT_REVIEW.items():
        matched = (destinations['place_id'].eq(place_id)
                   & destinations['place_name'].map(normalize_text).eq(normalize_text(name))
                   & description_text.str.contains(normalize_text(phrase), regex=False))
        destinations.loc[matched, [f'facility_{key}_mentioned' for key in rejected]] = 0
        destinations.loc[matched, 'facility_review_note'] = note
    destinations['c4_facility_score'] = destinations[facility_columns].mean(axis=1)

    def extract_activity_tags(row):
        text = normalize_text(f"{row['place_name']} {row['description']}")
        tags = set(CATEGORY_TAGS.get(row['category_clean'], set()))
        for tag, keywords in ACTIVITY_KEYWORDS.items():
            if any(contains_keyword(text, keyword) for keyword in keywords):
                tags.add(tag)
        return '|'.join(sorted(tags))

    destinations['activity_tags'] = destinations.apply(extract_activity_tags, axis=1)
    destinations['feature_source_note'] = 'C4: indikator deskripsi dengan koreksi konteks tertentu; 0 bukan bukti fasilitas tidak tersedia. Activity_tags tetap heuristik.'
    return destinations


def add_model_rating(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    frame = frame.copy()
    valid = frame.loc[frame.rating.between(1, 5), "rating"]
    median = float(valid.median()) if len(valid) else None
    frame["c2_rating"] = frame.rating.astype(float)
    frame["c2_rating_for_model"] = frame.c2_rating.where(frame.c2_rating.between(1, 5))
    frame["rating_imputed"] = (frame.place_id.eq(438)
        & frame.place_name.eq("Taman Hutan Raya Banten") & frame.rating.isna())
    if frame.rating_imputed.any():
        if median is None or not np.isfinite(median):
            raise ValueError("Median membutuhkan rating teramati valid.")
        frame.loc[frame.rating_imputed, "c2_rating_for_model"] = median
    frame["rating_model_note"] = ""
    frame.loc[frame.rating_imputed, "rating_model_note"] = (
        "Imputasi median rating teramati; bukan rating destinasi yang terverifikasi.")
    return frame, {"method": "median_observed_valid_ratings", "value": median,
                   "observed_rows": len(valid), "imputed_ids": frame.loc[frame.rating_imputed, "place_id"].astype(int).tolist(),
                   "calculation_column": "c2_rating_for_model", "source_rating_unchanged": True}


def build_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    numeric = frame[["c1_ticket_price", "c2_rating_for_model"]].to_numpy(dtype=float, copy=True)
    if (not np.isfinite(numeric).all() or (numeric[:, 0] < 0).any()
        or ((numeric[:, 1] < 1) | (numeric[:, 1] > 5)).any()
        or frame.category_clean.isna().any() or frame.category_clean.eq("").any()):
        raise ValueError("Fitur model belum lengkap/valid; destinasi tetap dipertahankan, jangan dropna.")
    cap = float(np.percentile(numeric[:, 0], 99))
    numeric[:, 0] = np.minimum(numeric[:, 0], cap)
    mean, scale = numeric.mean(axis=0), numeric.std(axis=0)
    scale[scale == 0] = 1
    categories = sorted(frame.category_clean.unique().tolist())
    columns = ["c1_ticket_price_z", "c2_rating_z"] + [f"category_{c}" for c in categories]
    one_hot = np.array([[int(c == category) for c in categories] for category in frame.category_clean])
    matrix = np.column_stack(((numeric - mean) / scale, one_hot))
    features = pd.DataFrame(matrix, columns=columns)
    features.insert(0, "place_id", frame.place_id.to_numpy())
    return features, {"feature_columns": columns, "categories": categories,
                      "ticket_price_cap_p99": cap, "mean": mean.tolist(), "scale": scale.tolist(),
                      "excluded": "C4 hanya SPK; indikator deskripsi bukan fasilitas lapangan terverifikasi."}


def build_pipeline(project_root: Path) -> PipelineResult:
    root = Path(project_root)
    for relative in SOURCE_PATHS:
        if not (root / relative).is_file():
            raise FileNotFoundError(f"Sumber wajib tidak tersedia: {relative}; jangan lanjut dengan dataset parsial.")
    base = pd.read_csv(root / SOURCE_PATHS[0])
    additional = pd.read_csv(root / SOURCE_PATHS[1])
    if len(base) != 437 or set(base.Place_Id) != set(range(1, 438)):
        raise ValueError("Sumber Kaggle harus 437 ID asli.")
    if len(additional) != 6 or set(additional.Place_Id) != set(range(438, 444)):
        raise ValueError("Tambahan Jawa harus enam ID 438–443.")
    base["source_dataset"] = "Indonesia Tourism Destination"
    base["source_url"] = BASE_URL
    base["rating_status"] = "dataset_original"
    base["rating_source_url"] = BASE_URL
    base["rating_access_date"] = ""
    additional["source_dataset"] = "Tambahan Jawa: tarif peraturan daerah dan lokasi OSM"
    additional["source_url"] = "data/review/gabungan_jawa/Dokumentasi.md"
    additional["rating_status"] = "missing"
    additional["rating_source_url"] = ""
    additional["rating_access_date"] = ""
    receipt = json.loads((root / SOURCE_PATHS[2]).read_text(encoding="utf-8"))
    for record in receipt["records"]:
        match = additional.Place_Id.eq(record["place_id"]) & additional.Place_Name.eq(record["dataset_name"])
        if record["integration_allowed"] and record["match_status"] == "matched_name_location":
            additional.loc[match, "Rating"] = record["rating_observed"]
            additional.loc[match, "rating_status"] = "google_maps_matched"
            additional.loc[match, "rating_source_url"] = record["maps_url"]
            additional.loc[match, "rating_access_date"] = receipt["access_date"]
        else:
            additional.loc[match, "rating_status"] = "pending_identity"
    destinations = normalize_destinations(pd.concat([base, additional], ignore_index=True))
    _check_ids(destinations)
    destinations = destinations.sort_values("place_id").reset_index(drop=True)
    ratings = pd.read_csv(root / SOURCE_PATHS[3])
    ratings.columns = [re.sub(r"[^0-9a-zA-Z]+", "_", c).lower() for c in ratings.columns]
    for column in ["user_id", "place_id", "place_ratings"]:
        ratings[column] = pd.to_numeric(ratings[column], errors="coerce")
    ratings = ratings.loc[ratings.user_id.notna() & ratings.place_id.notna()
                          & ratings.place_ratings.between(1, 5)].drop_duplicates(["user_id", "place_id"], keep="last")
    aggregate = ratings.groupby("place_id", as_index=False).agg(
        user_rating_mean=("place_ratings", "mean"), user_rating_count=("place_ratings", "count"),
        user_rating_std=("place_ratings", "std"))
    aggregate["user_rating_std"] = aggregate.user_rating_std.fillna(0)
    destinations = destinations.merge(aggregate, on="place_id", how="left", validate="one_to_one")
    destinations["c1_ticket_price"] = destinations.price.astype(float)
    destinations, imputation = add_model_rating(destinations)
    destinations = add_facilities(destinations)
    features, parameters = build_features(destinations)
    destinations["model_features_complete"] = True
    _check_ids(destinations)
    payload = {"pipeline_version": PIPELINE_VERSION,
               "source_hashes": {relative: _hash(root / relative) for relative in SOURCE_PATHS},
               "place_ids": destinations.place_id.astype(int).tolist(),
               "feature_parameters": parameters, "rating_imputation": imputation}
    manifest = {**payload, "pipeline_fingerprint": _fingerprint(payload)}
    summary = {
        "destination_rows": 443, "source_rows": {"kaggle": 437, "additional_java": 6},
        "rows_lost": 0, "missing_destination_ids": [],
        "missing_rating_ids": destinations.loc[destinations.rating.isna(), "place_id"].astype(int).tolist(),
        "imputed_rating_ids": imputation["imputed_ids"], "rating_imputation": imputation,
        "coordinate_review_ids": destinations.loc[destinations.coordinate_review_required, "place_id"].astype(int).tolist(),
        "data_quality_review_ids": destinations.loc[destinations.data_quality_issues.ne(""), "place_id"].astype(int).tolist(),
        "model_features_complete_rows": 443, "kmeans_training_ready": True,
        "rating_rows_valid": len(ratings),
        "cities": sorted(destinations.city.unique().tolist()), "categories": parameters["categories"],
        "destinations_with_facility_evidence": int(destinations.c4_facility_score.gt(0).sum()),
        "destinations_with_facility_keyword_matches": int(destinations.facility_keyword_score.gt(0).sum()),
        "destinations_with_facility_context_review": int(destinations.facility_review_note.ne("").sum()),
        "destinations_without_facility_description": int(destinations.facility_description_missing.sum()),
        "destinations_with_activity_tags": int(destinations.activity_tags.ne("").sum()),
        "facility_evidence_definition": "Penyebutan deskripsi yang diterima; bukan fasilitas terverifikasi di lapangan.",
        "feature_parameters": parameters, "pipeline_fingerprint": manifest["pipeline_fingerprint"],
        "missing_value_policy": "Pertahankan 443 destinasi; imputasi hanya rating model Tahura. Time_Minutes boleh kosong.",
    }
    return PipelineResult(destinations, features, manifest, summary)


def export_pipeline(result: PipelineResult, project_root: Path) -> dict[str, Path]:
    _check_ids(result.destinations)
    _check_ids(result.features)
    columns = result.manifest["feature_parameters"]["feature_columns"]
    if not np.isfinite(result.features[columns].to_numpy(dtype=float)).all():
        raise ValueError("Fitur nonfinite; ekspor dibatalkan.")
    paths = {name: Path(project_root) / relative for name, relative in OUTPUT_PATHS.items()}
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    result.destinations.to_csv(paths["destinations"], index=False, encoding="utf-8-sig", lineterminator="\n")
    result.features.to_csv(paths["features"], index=False, encoding="utf-8-sig", lineterminator="\n")
    paths["summary"].write_text(json.dumps(result.summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {**result.manifest, "output_hashes": {
        OUTPUT_PATHS[name]: _hash(paths[name]) for name in ("destinations", "features", "summary")}}
    paths["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    return paths


def validate_artifacts(project_root: Path) -> PipelineResult:
    root = Path(project_root)
    path = root / OUTPUT_PATHS["manifest"]
    if not path.is_file():
        raise ValueError("Manifest tidak tersedia; jalankan preprocess_destinations dahulu.")
    saved = json.loads(path.read_text(encoding="utf-8"))
    if saved.get("pipeline_version") != PIPELINE_VERSION:
        raise ValueError("Versi pipeline usang; jalankan preprocessing ulang.")
    for relative in SOURCE_PATHS:
        if not (root / relative).is_file() or saved.get("source_hashes", {}).get(relative) != _hash(root / relative):
            raise ValueError(f"Hash sumber berubah: {relative}; preprocessing ulang diperlukan.")
    for name in ("destinations", "features", "summary"):
        relative = OUTPUT_PATHS[name]
        if not (root / relative).is_file() or saved.get("output_hashes", {}).get(relative) != _hash(root / relative):
            raise ValueError(f"Hash output berubah: {relative}; preprocessing ulang diperlukan.")
    result = build_pipeline(root)
    for key in result.manifest:
        if saved.get(key) != result.manifest[key]:
            raise ValueError(f"Manifest tidak sesuai transformasi: {key}; preprocessing ulang diperlukan.")
    # Verify content, not just a digest supplied by the same potentially edited manifest.
    for name, expected in (("destinations", result.destinations), ("features", result.features)):
        actual = pd.read_csv(root / OUTPUT_PATHS[name])
        try:
            pd.testing.assert_frame_equal(actual, expected.replace("", np.nan), check_dtype=False,
                                          check_exact=False, rtol=1e-12, atol=1e-12)
        except AssertionError as error:
            raise ValueError(f"Output {name} tidak sesuai sumber/transformasi.") from error
    return result
