# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

TravelFit is a decision-support system (SPK) that recommends tourist destinations in Java. It uses AHP weights and TOPSIS ranking over 443 destinations: 437 from Kaggle plus 6 curated from Java sources. K-Means only adds a segment label. It does **not** filter or rank candidates. The stack is Django 5.2 with SQLite, server-rendered templates, and plain JS/CSS. There is no frontend build step. Docs, comments, UI text and error messages are in Indonesian, so keep new user-facing text in Indonesian.

`README.md` holds the authoritative description of the method: the criteria C1–C6, the formulas and the CR values. `Dokumentasi.md` documents data sources and their limits. Design decisions live in `docs/decisions/`.

## Commands

The project runs on Windows with a local venv. Call the venv interpreter directly:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.txt   # requirements.txt is UTF-16 encoded
.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000

# Tests (temporary DB)
.venv/Scripts/python.exe manage.py test recommender.tests --noinput
.venv/Scripts/python.exe manage.py test recommender.tests.test_spk                       # one module
.venv/Scripts/python.exe manage.py test recommender.tests.test_spk.SomeTestCase.test_x   # one test
.venv/Scripts/python.exe manage.py check
.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
```

The data pipeline must run in this order. Each command accepts `--project-root PATH`. If you change source data or transformations, repeat every step after the change:

```powershell
manage.py preprocess_destinations             # writes data/processed/*_java443.csv + reports/preprocessing/*manifest.json
manage.py import_destinations --backup-only   # run before migrate on an existing DB
manage.py migrate
manage.py import_destinations [--dry-run]     # SQLite backup to archive/local_backups/, then atomic upsert/delete
manage.py train_clusters [--dry-run]          # writes cluster_label + reports/clustering/kmeans_evaluation.json
```

## Architecture

**Offline pipeline (`recommender/data_pipeline.py`).** This module holds pure pandas transforms with no DB or network access. It is the canonical preprocessing implementation. The management commands and `notebooks/01_preprocessing_travelfit.ipynb` both import it. Notebooks 02 and 03 re-implement the cleaning steps inline and are meant to reproduce its output byte-for-byte, so update them if you change a transform. `build_pipeline` → `export_pipeline` writes the output CSVs and a manifest. The manifest holds a `PIPELINE_VERSION`, SHA-256 hashes of the source and output files, and a `pipeline_fingerprint`. `validate_artifacts`, called by the importer and the trainer, re-runs the full pipeline and refuses to proceed when hashes or content are stale. Never hand-edit the processed CSVs or the manifest. Re-run `preprocess_destinations` instead. The pipeline requires exactly IDs 1–443 (`_check_ids`). Dropping a destination is not allowed: rows with data problems are kept and flagged in `data_quality`. Examples are the Pelabuhan Marina coordinates and the imputed Tahura rating.

**Online recommendation (`recommender/views.py::rekomendasi`).**
1. Filter by province with `harga_tiket <= budget`.
2. Build the C1–C6 decision matrix.
3. Call `spk/topsis.rank` with the weights from `spk/profiles.ACTIVE_PROFILES`.
4. Show the top 10.

The four AHP profiles are defined as upper-triangle Saaty matrices in `spk/profiles.py`. Their weights and CR are computed at import time, and a profile with CR ≥ 0.1 is silently dropped. When a user moves the weight sliders, the view normalizes the slider values directly. That path does not run AHP. Results follow POST-Redirect-GET: they are stored once in the session under `flash_hasil`. AJAX requests (`X-Requested-With`) get JSON with rendered partials instead. A session's `dataset_fingerprint` (`ticket-v1:` + pipeline fingerprint) clears stale results after a re-import.

**Modules under `recommender/spk/`.** These are mostly stdlib-only pure functions: `ahp`, `topsis`, `geo` (Haversine distance used for C3), `similarity` (Jaccard index used for C6) and `validation` (SAW/Spearman, used only by tests). The modules `spk/biaya.py`, `transport.py`, `jarak.py` and the `JarakCache` model are **historical code**. They modelled travel cost and OSRM road distance and are no longer called by the active recommendation. Their tests are kept. See `docs/decisions/2026-10-05-ticket-budget.md`: budget covers only one destination's ticket per person.

**Other areas.**
- `scripts/open_data_review/` is an isolated offline review CLI that does not import Django.
- `data/review/` holds curation evidence: PDFs, OSM/Nominatim snapshots, and per-region `validate_*.py` scripts.
- `outputs/*/_build/` contains generators for report deliverables (Excel, DOCX, schedule images), not app code.
- `archive/legacy/` holds archived pre-Java443 workflows. Do not revive them as the active pipeline. See `docs/maintenance/java443-cleanup.md`.

## Integrity constraints

- `recommender/tests/fixtures/java443_protected_hashes.json` pins byte-exact SHA-256 hashes of raw data, review evidence and `Laporan_SPK_TravelFit.docx`. Tests fail if those files change, including changes to line endings alone.
- `.gitattributes` fixes the EOL for each of these files. When adding or editing protected files, preserve their line endings and encoding. Processed CSVs are written as UTF-8 with BOM and LF line endings.
- Many numbers are stated in README, Dokumentasi and the reports. They include 443/437/6, CR values, cluster sizes 414/29 and silhouette 0.54302. If code changes alter any of them, update those docs too.
