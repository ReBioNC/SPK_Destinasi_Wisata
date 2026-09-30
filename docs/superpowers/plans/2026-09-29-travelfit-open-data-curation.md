# TravelFit Open-Data Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce separate, reviewable candidate, evidence, verified-subset, and audit-summary files without altering TravelFit's existing datasets or website.

**Architecture:** A small offline Python pipeline reads the 1,900 synthetic and 437 Kaggle rows, adds OSM candidates from a dated extract, computes C2 from mapped nearby services, and applies a strict per-attribute evidence gate. The pipeline writes only under `data/review/`; it neither imports to Django nor retrains K-Means during this project.

**Tech Stack:** Python 3.11+, standard library, pandas/openpyxl from `requirements.txt`, Django's existing `manage.py test` runner.

**Spec:** `docs/superpowers/specs/2026-09-29-travelfit-open-data-curation-design.md`

## Global Constraints

- Preserve `Dataset_Wisata_38_Provinsi.xlsx`, the 437-row CSV, existing processed files, README edits, database, models, website, and current clustering.
- Treat 1,900 and 437 rows as candidates; do not label generated prices, ratings, coordinates, descriptions, or facilities as verified.
- Use only no-cost sources with clear reuse terms; OSM needs attribution and ODbL handling. Do not bulk-copy the Sisparnas site or Google Maps ratings.
- C2 is the count of four distinct mapped service categories within 2 km: public transport, healthcare, ATM/bank, lodging. Zero means no matching **mapped** object, not absence in reality.
- C1 requires a destination-specific entrance-ticket source; free entry requires explicit evidence; unknown remains null. C4 requires explicit evidence for each of the four onsite indicators.
- Export `verified` only when identity/location, C1, C2 inputs, C4, C5, and C6 meet the spec's evidence requirements. No forced target count.

## Review Focus

1. `Price=0` from the generator is not verified free entry; Task 4 pins this with a failing test.
2. OSM's Indonesia-with-East-Timor extract is not a country filter; Task 2 tests refusal of snapshots without a recorded Indonesia-only boundary query.
3. A way/relation centroid is not automatically a verified entrance coordinate; Task 2 records geometry provenance and Task 4 blocks it until checked.
4. Missing OSM amenity tags are not proof that an onsite facility is absent; Task 4 tests explicit false evidence.
5. A candidate with the same name in two provinces is not a duplicate; Task 1 tests province-aware matching.

---

## File map

- `scripts/open_data_review/schema.py`: candidate, OSM point, source evidence, and review-result dataclasses plus CSV field names.
- `scripts/open_data_review/legacy.py`: read-only loading and inventory of existing XLSX and CSV.
- `scripts/open_data_review/osm.py`: parse dated Overpass JSON snapshots, map OSM tags, and preserve object IDs.
- `scripts/open_data_review/services.py`: C2 radius calculation and service-category rules.
- `scripts/open_data_review/evidence.py`: evidence validation and `verified`/`pending`/`rejected` decision.
- `scripts/open_data_review/export.py`: deterministic CSV/Markdown review outputs and source manifest.
- `scripts/open_data_review/cli.py`: offline orchestration; accepts snapshot and manually reviewed evidence paths, never updates Django.
- `recommender/tests/test_open_data_review.py`: focused unit and end-to-end tests for the new pipeline.
- `data/review/`: only new user-facing review files; raw input snapshots are separately identified by path/hash/date.

### Task 1: Inventory legacy candidates without trusting generated fields

**Files:** Create `scripts/open_data_review/schema.py`, `scripts/open_data_review/legacy.py`, `scripts/open_data_review/__init__.py`; test `recommender/tests/test_open_data_review.py`.

**Interfaces:** `load_legacy_candidates(xlsx_path: Path, kaggle_csv_path: Path) -> list[Candidate]`; `Candidate` carries stable `candidate_id`, `origin`, original name/city/province, raw values, and per-field legacy-trust flags. Later tasks consume `Candidate` objects.

- [ ] Write tests that assert 1,900 XLSX and 437 CSV rows can be inventoried, synthetic numeric/coordinate/facility fields are untrusted, Kaggle rows are not automatically verified, and identical names in different provinces remain distinct.
- [ ] Run `python manage.py test recommender.tests.test_open_data_review.LegacyInventoryTests -v 2`; expect failure because the loader is absent.
- [ ] Implement the minimal schema and loader; preserve original row IDs and source paths, and flag generated filler names without trusting them as real destinations.
- [ ] Run the focused tests and full `python manage.py test`; expect zero failures.
- [ ] Commit only Task 1 files with `feat(data): inventory legacy destination candidates`.

### Task 2: Import and identify lawful OSM candidates from a dated snapshot

**Files:** Create `scripts/open_data_review/osm.py`; extend `recommender/tests/test_open_data_review.py`.

**Interfaces:** `parse_osm_snapshot(payload: dict, snapshot_at: str, source_query: str) -> tuple[list[Candidate], list[OsmPoint]]`; consumes saved Overpass JSON whose recorded query restricts results to Indonesia's `ISO3166-1=ID`, `admin_level=2` boundary, not an implicit network scrape. `OsmPoint` contains `osm_type`, `osm_id`, coordinates, tags, and geometry origin; Task 3 consumes it.

- [ ] Write tests for named tourism attractions, node versus way/relation `center`, unique type+ID, hotel as service rather than attraction, unnamed objects, and refusal when the source query does not document an Indonesia-only boundary. Record that a way/relation center still needs item-level location review.
- [ ] Run `python manage.py test recommender.tests.test_open_data_review.OsmSnapshotTests -v 2`; expect failure for the missing parser.
- [ ] Implement parsing and a documented Overpass query template limited by Indonesia boundary and relevant tourism/service tags; record snapshot timestamp, endpoint/query, OSM IDs, and ODbL attribution. Do not download the 1.6 GB whole-region PBF or call Overpass during unit tests. Source size and East-Timor inclusion: <https://download.geofabrik.de/asia/indonesia.html>.
- [ ] Run focused and full tests; expect zero failures.
- [ ] Commit only Task 2 files with `feat(data): parse dated OSM destination snapshots`.

### Task 3: Compute the replacement C2 from mapped nearby services

**Files:** Create `scripts/open_data_review/services.py`; extend `recommender/tests/test_open_data_review.py`.

**Interfaces:** `nearby_service_evidence(lat: float, lon: float, points: list[OsmPoint], radius_km: float = 2.0) -> dict[str, list[str]]`; `service_score(evidence: dict[str, list[str]]) -> int`. The four keys are `transport`, `healthcare`, `atm_bank`, `lodging`.

- [ ] Write tests for zero mapped services, multiple objects in one category counting once, all four categories counting four, a point exactly at the 2 km boundary, a point beyond it, and a repeated OSM object not counting twice.
- [ ] Run `python manage.py test recommender.tests.test_open_data_review.ServiceScoreTests -v 2`; expect failure because functions are absent.
- [ ] Implement Haversine radius matching and explicit OSM tag mapping; include contributing IDs and snapshot date in C2 evidence, never infer real-world absence from zero.
- [ ] Run focused and full tests; expect zero failures.
- [ ] Commit only Task 3 files with `feat(data): score mapped nearby services for C2`.

### Task 4: Apply strict per-attribute provenance and duplication gates

**Files:** Create `scripts/open_data_review/evidence.py`; extend `recommender/tests/test_open_data_review.py`.

**Interfaces:** `review_candidate(candidate: Candidate, evidence: list[SourceEvidence], c2_ids: dict[str, list[str]]) -> ReviewResult`; `deduplicate_candidates(candidates: list[Candidate]) -> tuple[list[Candidate], list[ReviewResult]]`. Evidence records field, observed value, exact source URL/OSM ID, access date, reuse status, and verification note.

- [ ] Write tests: generator zero price remains pending; explicit sourced free entry is 0; uncertain ticket type/currency is pending; missing or inferred facility negatives are pending; valid all-field evidence is verified; coordinate conflict and ambiguous same-name matching require review; unclear reuse rights cannot be `verified`.
- [ ] Run `python manage.py test recommender.tests.test_open_data_review.EvidenceGateTests -v 2`; expect failure for absent functions.
- [ ] Implement the gate and conservative deduplication: normalized name+province creates candidate pairs, but conflicting city/coordinates are flagged rather than silently merged. C5/C6 mappings require item-specific tags or sources; generator templates never count.
- [ ] Run focused and full tests; expect zero failures.
- [ ] Commit only Task 4 files with `feat(data): gate verified destinations on field evidence`.

### Task 5: Export review artifacts without modifying production data

**Files:** Create `scripts/open_data_review/export.py`, `scripts/open_data_review/cli.py`; extend `recommender/tests/test_open_data_review.py`.

**Interfaces:** `write_review_outputs(candidates: list[Candidate], results: list[ReviewResult], output_dir: Path) -> None`; CLI accepts `--legacy-xlsx`, `--kaggle-csv`, `--osm-json`, `--evidence-csv`, `--output-dir` and defaults output to `data/review/`.

- [ ] Write an integration test with temporary input/output directories asserting the four spec outputs exist, verified CSV excludes pending/rejected, evidence CSV preserves field sources, summary counts balance, rerun is deterministic, and original input hashes are unchanged.
- [ ] Run `python manage.py test recommender.tests.test_open_data_review.ReviewExportTests -v 2`; expect failure for missing exporter.
- [ ] Implement deterministic CSV/Markdown outputs and a source manifest with query, snapshot date, SHA-256, and attribution; refuse an output path that aliases any input or production dataset path.
- [ ] Run focused and full tests; expect zero failures.
- [ ] Commit only Task 5 files with `feat(data): export standalone destination review files`.

### Task 6: Execute a bounded real-source review and report actual yield

**Files:** Create `data/review/destinations_candidate_audit.csv`, `data/review/destinations_verified_open.csv`, `data/review/destination_evidence.csv`, `data/review/audit_summary.md`; optionally add `data/review/source_manifest.json`; extend `recommender/tests/test_open_data_review.py` only for bugs reproduced in real data.

**Interfaces:** Consumes Task 5 CLI. The real-source run uses a dated OSM snapshot from an approved free endpoint or a locally supplied snapshot; manual ticket/facility evidence is added only when its source and reuse rights are documented.

- [ ] Run read-only source/license checks and a bounded extraction, retaining only OSM objects provably inside Indonesia. If a provider refuses or rate-limits, stop that source and record the limitation; do not circumvent it.
- [ ] Run the CLI against the actual 1,900 + 437 legacy files and available lawful OSM snapshot; record candidate, pending, rejected, and fully verified counts plus province/category coverage. Do not fabricate values to raise the verified count.
- [ ] Inspect a cross-province/category sample manually and correct any reproducible parser or mapping bug by writing a failing regression test before code changes.
- [ ] Run `python manage.py test`, `git diff --check`, and compare hashes of production datasets with their pre-run values; record exact outputs and any unverified source gaps in the audit summary.
- [ ] Commit only new `data/review/` artifacts and related bug-fix tests/code with `data: publish review-only open destination audit`.

## Self-review against the spec

Tasks 1–5 cover inventory, OSM candidate/source provenance, C2, all-field evidence, deduplication, and isolated exports. Task 6 covers the real dataset and honest actual yield; it does **not** claim 1,900 verified rows before source evidence exists. Active Django import, AHP recalibration, K-Means retraining, UI changes, and rewriting the current dataset are intentionally outside this review-only plan and require a later approved integration plan.
