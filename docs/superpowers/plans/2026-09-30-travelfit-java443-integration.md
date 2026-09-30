# TravelFit Jawa443 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aplikasi, notebook, training, dan website memakai 443 destinasi aktif dengan transformasi bersama dan peta Jawa.

**Architecture:** Modul Python murni menghasilkan master, fitur, dan manifest yang dipakai notebook, importer, dan trainer. Django menyimpan rating sumber terpisah dari rating perhitungan. Template bersama dan aset lokal menggantikan halaman monolitik, tanpa mengubah stack.

**Tech Stack:** Django, SQLite, pandas, NumPy, HTML template, CSS lokal, JavaScript native; Python `.venv/Scripts/python.exe`.

**Spec:** `docs/superpowers/specs/2026-09-30-travelfit-java443-integration-design.md` (disetujui pengguna).

## Global Constraints

- Bekerja native di branch `new`, bukan membuat worktree atau task baru.
- Tidak kehilangan destinasi setelah preprocessing; ID 1–443 tetap lengkap.
- C4 tetap indikator fasilitas dari deskripsi, dengan koreksi konteks.
- Rating sumber Tahura tetap kosong; median snapshot sekarang 4,5 hanya untuk perhitungan dan ditandai.
- Pelabuhan Marina tetap dimasukkan; koordinat sumber 1,07888 / 103,931398 tidak diganti tebakan.
- Laporan DOCX tidak diubah.
- Commit lokal terpisah untuk setiap task yang selesai dan terverifikasi. Push tidak termasuk ruang lingkup.
- Pertanyaan berikutnya diberikan sebagai pilihan.
- Tidak mengarang survei, tarif, fasilitas, rating Google Maps, atau klaim semua data sebagai resmi pemerintah.
- K-Means memakai harga tiket p99 + Z-score, rating perhitungan + Z-score, dan one-hot kategori; C4 hanya SPK.
- AHP–TOPSIS tetap enam kriteria; C1 runtime estimasi total perjalanan, bukan harga tiket saja.

## Review Focus

1. Drive Colab kehilangan file modul/sumber: notebook berhenti jelas, tidak diam-diam mengekspor 437; diuji Task 1–2.
2. CSV/manifest usang atau diubah setelah preprocessing: importer/trainer menolak sebelum mutasi; diuji Task 1, 3, 4.
3. ID Tahura dipakai ulang untuk tempat lain atau muncul rating kosong baru: tidak mendapat imputasi otomatis; diuji Task 1.
4. Hasil sesi lama dari dataset 2337 dibuka sesudah migrasi: tidak muncul sebagai hasil aktif baru; diuji Task 3, 5.
5. Marina di luar frame, filter tanpa kandidat, atau JavaScript gagal: daftar/status tetap benar dan form server tetap berfungsi; diuji Task 5–7.

## File structure dan urutan

Satu rencana integrasi karena antarmuka pipeline → database → trainer → views saling bergantung. Setiap task berikut menghasilkan deliverable yang bisa ditolak/diterima secara terpisah; task data tidak bergantung pada desain UI.

| Task | ID outcome spec | Unit dan tanggung jawab |
| --- | --- | --- |
| 1 | T2 | `recommender/data_pipeline.py`: kontrak master/fitur/manifest dan aturan preprocessing |
| 2 | T2 | Notebook tipis dan command preprocessing; output reproducible |
| 3 | T2 | Model/migration dan importer atomik; database tepat 443 |
| 4 | T3 | Trainer seluruh 443 dan laporan evaluasi nyata |
| 5 | T3 | Rating/C4/quality metadata pada SPK serta invalidasi sesi |
| 6 | T4 | UI-UX Pro Max, template bersama dan alur form/hasil baru |
| 7 | T4 | SVG enam provinsi Jawa dan interaksi peta bersama |
| 8 | T5 | Cleanup terarah, dokumentasi, verifikasi akhir |

Untuk tiap task: RED yang gagal karena kontrak belum tersedia → implementasi → GREEN → review perubahan → commit. Jalankan `.venv/Scripts/python.exe manage.py test recommender.tests --noinput` sebelum commit; tes kontrak legacy disesuaikan pada task pemiliknya, bukan disembunyikan. Baca skill TDD sebelum kode, systematic-debugging jika menemukan kegagalan tak terduga, verification-before-completion sebelum klaim/commit. Tes menggunakan database sementara; penggantian database lokal hanya pada Task 3 setelah backup.

## Task 1: Pipeline bersama dan kontrak versi

**Files:** Create `recommender/data_pipeline.py`, `recommender/tests/test_data_pipeline.py`; modify `recommender/tests/test_preprocessing_retention.py`, `recommender/tests/test_facility_preprocessing.py`.

**Interfaces:**

- `PipelineResult` dataclass: `destinations: pd.DataFrame`, `features: pd.DataFrame`, `manifest: dict`, `summary: dict`.
- `normalize_destinations(raw: pd.DataFrame) -> pd.DataFrame`: format/measurement flags tanpa retensi penuh untuk fixture kecil.
- `add_facilities(frame: pd.DataFrame) -> pd.DataFrame`: enam indikator dan koreksi konteks yang sudah disetujui.
- `add_model_rating(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]`: median pengamatan valid dan imputasi ID/nama Tahura saja.
- `build_features(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]`: metadata `place_id`, fitur price/rating Z dan kategori; parameters memuat urutan fitur, p99, mean, scale, kategori.
- `build_pipeline(project_root: Path) -> PipelineResult`: empat sumber aktif spec, validasi tepat ID 1–443, urutan ID stabil, hash SHA256, `pipeline_version="java443-v1"`.
- `export_pipeline(result: PipelineResult, project_root: Path) -> dict[str, Path]`: output CSV spec, summary, dan `reports/preprocessing/preprocessing_java443_manifest.json`, hash output disimpan manifest terakhir.
- `validate_artifacts(project_root: Path) -> PipelineResult`: memeriksa versi, hash sumber/output, ID dan parameter terhadap hasil pipeline; gagal tanpa menulis.
- `manifest["pipeline_fingerprint"]`: SHA256 JSON kanonik (`sort_keys=True`, separators `(',', ':')`) atas versi, hash empat sumber, urutan ID, parameter fitur dan imputasi. Timestamp/hash output tidak masuk fingerprint agar ekspor ulang sumber sama tetap idempoten.

- [ ] **1. Tulis tes gagal:** `test_exact_source_ids_retained` menegaskan 443 baris, ID unik `set(range(1,444))`; `test_model_features_exclude_c4` menegaskan hanya fitur price/rating/kategori, 443 nilai finite, harga master tidak dicap. `test_imputation_identity_guard` menegaskan ID438/nama lain tidak diimputasi; `test_unexpected_missing_rating_blocks_features` menegaskan baris tetap ada namun fitur tidak dibuat tanpa kebijakan. Pindahkan 17 assertions retensi/fasilitas yang ada ke API bersama; median fixture harus 4,2, snapshot 4,5.
- [ ] **2. Jalankan RED:** `.venv/Scripts/python.exe manage.py test recommender.tests.test_data_pipeline --noinput`; harus gagal karena API belum tersedia, bukan error fixture/path.
- [ ] **3. Implementasi modul:** pindahkan aturan notebook yang sudah diverifikasi, termasuk agregat interaksi dan tag aktivitas. Sumber/provenance tidak ditimpa; record yang tidak finite tetap master tetapi ekspor fitur berhenti. Jangan memakai Django atau melakukan IO saat import modul.
- [ ] **4. Tambah tes manifest:** `test_missing_source_fails_clearly`, `test_duplicate_or_missing_id_blocks_export`, `test_modified_output_or_source_rejected`, `test_stale_version_rejected`, `test_constant_numeric_scale_is_one`; gunakan salinan sumber di temporary directory, bukan mengubah file repository.
- [ ] **5. Jalankan GREEN:** tiga module tes preprocessing dan seluruh suite. Pastikan corrections description tetap tidak mengubah teks asli; Marina tetap flag, Tahura raw NaN, lima rating cocok tidak berubah.
- [ ] **6. Commit:** `refactor(data): share Java443 preprocessing contract` (stage hanya modul dan tes terkait).

## Task 2: Notebook tipis dan ekspor reproducible

**Files:** Modify `notebooks/01_preprocessing_travelfit.ipynb`; create `recommender/management/commands/preprocess_destinations.py`, `recommender/tests/test_preprocessing_entrypoints.py`; regenerate dua CSV java443 dan dua JSON summary/manifest melalui API Task 1.

**Interfaces:** Notebook dan command memanggil `build_pipeline`/`export_pipeline`. Command `preprocess_destinations --project-root PATH` default repository; notebook `PROJECT_ROOT` lokal atau `/content/drive/MyDrive/TravelFit`, lalu `sys.path` root dan import module lokal.

- [ ] **1. Tes gagal:** `test_command_exports_443_and_manifest` membandingkan output temporary directory dengan `PipelineResult`; `test_notebook_calls_shared_pipeline` menjalankan cell preprocessing dengan root lokal tanpa mount; `test_missing_colab_module_explains_required_file` memeriksa pesan yang menyebut `recommender/data_pipeline.py`, bukan download kode remote.
- [ ] **2. RED:** `.venv/Scripts/python.exe manage.py test recommender.tests.test_preprocessing_entrypoints --noinput`.
- [ ] **3. Implementasi:** notebook hanya setup Drive/path, panggil pipeline, ringkasan kualitas dan preview, ekspor. Markdown jelaskan enam grup C4, imputasi bukan Google Maps, metadata bukan fitur clustering, dan file wajib. Tidak lagi mengandalkan nomor cell untuk tes perilaku pipeline.
- [ ] **4. GREEN dan regenerate:** jalankan tes entrypoint dan suite; `.venv/Scripts/python.exe manage.py preprocess_destinations`. Verifikasi CSV 443, summary median4,5, imputasi[438], coordinate review[9], feature schema sama manifest, raw tidak berubah.
- [ ] **5. Commit:** `feat(data): export shared Java443 preprocessing from notebook`.

## Task 3: Database dan importer 443 yang aman

**Files:** Modify `recommender/models.py`, `recommender/management/commands/import_destinations.py`, `.gitignore`, `recommender/tests/test_import.py`; create `recommender/migrations/0003_destination_java443.py`, `recommender/tests/test_java443_import.py`.

**Interfaces:** `Destination.source_id: PositiveIntegerField(unique=True,null=True)` untuk migrasi record lama; `rating` nullable rating sumber; `rating_model` nullable, `rating_imputed` boolean; `description` text; `fas_accessibility`, `fas_information_center` boolean; `provenance` JSON; `data_quality` JSON; `pipeline_fingerprint` string. `facility_score() -> float` enam flag /6; `calculation_rating() -> float` model rating jika ada, fallback rating teramati untuk fixture/migrasi lama, error jika keduanya tidak valid. Natural-key constraint dipertahankan untuk nama/kota yang unik snapshot.

Importer mengonsumsi `validate_artifacts`; `--project-root PATH`, `--dry-run`; sumber `kaggle_java` 437 dan `curated_java` 6. Tidak menghitung median sendiri. Upsert cocok source_id; record lama dengan natural key sama diberi source_id sebelum insert untuk menghindari unique collision. Transaksi menghapus hanya record di luar ID aktif; semua cluster label hasil training lama dihapus jika fingerprint berubah. Ringkasan created/updated/deleted dan fingerprint keluar.

- [ ] **1. Tes gagal:** impor dua kali jumlah tetap443 dan source split437/6; `test_tahura_raw_null_model_median`, `test_facility_six_groups_matches_master`, `test_import_dry_run_leaves_database_unchanged`, `test_import_rolls_back_on_mid_transaction_error`, `test_stale_artifacts_rejected_before_delete`, `test_existing_natural_keys_rebound_without_duplicates`. Tes import1900/437 overlay diganti kontrak443; tes view fasilitas4/4 diganti6/6 tanpa menghilangkan coverage.
- [ ] **2. RED:** module import/model terkait; catat failures yang diharapkan.
- [ ] **3. Implementasi model/migration/importer:** sebelum mutasi database SQLite file nyata gunakan `sqlite3.Connection.backup` ke `archive/local_backups/travelfit-before-java443-<timestamp>.sqlite3`; backup test in-memory tidak dipaksa. Tambah ignore `archive/local_backups/`. Backup gagal → stop; validasi gagal → tidak ada delete. Sesi flash lama memakai fingerprint untuk invalidasi Task5.
- [ ] **4. GREEN:** suite + `.venv/Scripts/python.exe manage.py makemigrations --check --dry-run` dan `.venv/Scripts/python.exe manage.py check`.
- [ ] **5. Operasi lokal:** backup **sebelum migrate** karena schema berubah; jalankan migrate, importer dry-run, importer nyata, dan importer ulang. Audit count443, unique443, source split, nullable raw438, model4,5, Marina retained. Tampilkan jumlah record lama dihapus dan path backup pemulihan.
- [ ] **6. Commit:** `feat(data): replace legacy imports with atomic Java443 dataset` (database dan backup tidak masuk Git).

## Task 4: Training seluruh 443

**Files:** Modify `recommender/management/commands/train_clusters.py`, `recommender/tests/test_clustering.py`; create `recommender/tests/test_java443_training.py`; regenerate `reports/clustering/kmeans_evaluation.json`.

**Interfaces:** Consume `validate_artifacts`, feature order/parameters/fingerprint Task1, DB source_id Task3. Tetap `_fit_kmeans(data,k,seed=42,starts=10,max_iter=100)` dan `_silhouette(data,labels)`. `--dry-run` tidak mengubah label/laporan. Training DB harus tepat443 source IDs dan nilai numeric/category/fingerprint sesuai master; bila stale, stop dengan instruksi impor ulang.

- [ ] **1. Tes gagal:** report `training_rows==443`, assigned443, `assigned_simulation_rows==0`, imputasi IDs[438], fitur persis manifest; dry-run tidak menulis; missing/extra/stale destination ditolak; seed sama menghasilkan label/centroid sama; C4 berubah tidak mengubah matriks clustering.
- [ ] **2. RED:** `.venv/Scripts/python.exe manage.py test recommender.tests.test_java443_training --noinput`.
- [ ] **3. Implementasi:** urut source_id; K2–6, inertia/silhouette/ukuran minimum `max(5,round(443*0.05))`, aturan fallback tetap. Simpan centroid, scaler, kategori, pipeline fingerprint, median dan limitation dalam report. Update label atomik; tidak menganggap silhouette akurasi atau label sebagai filter ranking.
- [ ] **4. GREEN:** clustering tests + suite; command dry-run lalu training nyata; assert seluruh443 label nonblank, jumlah cluster di report menjumlah443. Catat selected_k/silhouette dari run, tidak dari angka target.
- [ ] **5. Commit:** `feat(model): train and evaluate K-Means on all 443 destinations`.

## Task 5: SPK konsisten dan metadata kualitas

**Files:** Modify `recommender/views.py`, `recommender/spk/topsis.py`, `recommender/tests/test_spk.py`, `recommender/tests/test_views.py`; create `recommender/tests/test_java443_recommendation.py`.

**Interfaces:** Runtime consume `Destination.calculation_rating()`, `facility_score()`, provenance/quality/fingerprint Task3. Context result memiliki `source_id`, `rating` nullable, `rating_model`, `rating_imputed`, `source_label`, `quality_notes`. Simpan session flash/map dengan `dataset_fingerprint`; sesi tanpa fingerprint/salah versi dibuang. Nama C1 runtime menjadi `Estimasi biaya total`; matriks C1 total, C2 calculation_rating, C3 jarak, C4 fasilitas6, C5 kategori, C6 Jaccard. Sumber biaya dan catatan Artha Tirta tidak dicampur dengan estimasi transport.

- [ ] **1. Tes gagal:** mock rute tanpa external requests: Tahura C2=4,5 namun rating sumber null dan label imputasi; filter berbeda tidak mengubah median; Marina tidak hilang dan quality warning ada; C4 sama master; stale session dibuang; import baru tidak mempertahankan flash2337; budget0/empty kandidat/invalid POST biasa dan AJAX tetap tertangani.
- [ ] **2. Tes TOPSIS gagal:** `rank([[float('nan')]], [1],[False])`, infinity, bobot negatif/semua0, panjang mismatch → ValueError; satu kandidat/tie/allzero finite; benefit dan cost berbalik ranking sesuai nilai. AHP seluruh profil CR<0,1; custom sliders masih sensitivitas, bukan klaim CR matriks baru.
- [ ] **3. RED:** tes SPK dan rekomendasi baru; implementasi validation sebelum normalisasi, metadata context, label enam fasilitas, invalidasi fingerprint. Tetap rute dan estimasi antar-pulau karena origin luar Jawa sah. Tidak menghilangkan candidate lewat cluster labels.
- [ ] **4. GREEN:** suite view/SPK/biaya/transport/jarak dan full suite. Fixture lama tanpa rating_model memakai rating valid via fallback; tidak memakai fallback untuk menghilangkan provenance Tahura.
- [ ] **5. Commit:** `fix(spk): align rating facilities and data quality with Java443`.

## Task 6: Website baru dengan UI-UX Pro Max

**Files:** Modify `recommender/templates/recommender/base.html`, `beranda.html`, `_hasil.html`, `tentang.html`; create `_preferences.html`, `_quality_notes.html`, `recommender/static/recommender/travelfit.css`, `travelfit.js`, `docs/design/travelfit-java-ui.md`; modify `recommender/tests/test_views.py`; create `recommender/tests/test_java_ui.py`.

**Interfaces:** Context Task5, form field names tidak diganti. Beranda/tentang/peta extend base; result fragment dipakai POST biasa dan AJAX. CSS tokens krem/teal/ink ditentukan workflow skill UI-UX Pro Max. JS enhancement form/profil/slider, tanpa kewajiban JS untuk submit server; CSRF tetap.

- [ ] **1. Baca UI-UX Pro Max lengkap serta reference wajib; jalankan workflow rekomendasi desain untuk native HTML/CSS dan dokumentasikan keputusan.** Jangan memigrasikan framework atau memasang layanan berbayar.
- [ ] **2. Tes gagal:** halaman extend base dengan nav/focus/label/error visible, no runtime Tailwind CDN, jumlah data context443, no claim1900/2337aktif, result sumber/imputasi terlihat, biaya breakdown dan tooltip bukan satu-satunya catatan. POST biasa tetap menghasilkan hasil; AJAX400 memuat error yang bisa diumumkan dengan live region.
- [ ] **3. RED lalu implementasi:** layout editorial krem–teal, header jelas, form bertahap secara visual, preset+advanced sliders, results skor dan alasan C1–C6, ringkasan kandidat, empty/loading/error states. Tentang menjelaskan seluruh CRISP-DM, fitur clustering, kriteria runtime, sumber dan keterbatasan.
- [ ] **4. GREEN:** UI/view suite; start dev server dengan loopback. Baca skill browser verification sebelum browser; cek desktop dan mobile, keyboard, noJS server POST, custom slider dan AJAX, CSRF, reflow, reduced motion dan browser console. Simpan checklist/screenshot bukti tanpa menyebut tes otomatis menggantikan inspeksi visual.
- [ ] **5. Commit:** `feat(ui): redesign TravelFit Java recommendation experience`.

## Task 7: Peta Jawa bersama dan retensi Marina

**Files:** Modify `recommender/templates/recommender/peta.html`, `beranda.html`, `recommender/views.py`; create `_java_map.html`, `recommender/static/recommender/java-map.css`, `java-map.js`, `recommender/tests/test_java_map.py`; audit `nusantara.js`/`nusantara.css` references for cleanup Task8.

**Interfaces:** Shared `_java_map.html` menerima enam provinsi kanonik, counts runtime dan hasil session valid Task5. JSON via Django `json_script`, bukan inline unsafe interpolation. SVG memakai enam geometri Jawa dari aset lama; projection Java viewBox diuji dengan koordinat sumber yang valid. Point di luar frame tidak mengubah framing dan mendapat `outside_frame` status di list; quality flag tidak dianggap coordinate correction.

- [ ] **1. Tes gagal:** SVG exact provinsi DKI/Banten/Jabar/Jateng/DIY/Jatim, tidak ada 32 provinsi lain; klik provinsi memprefill form; source counts total443; Marina tetap list dengan outside-frame/review label; invalid session result tidak dimuat; data nama berisi markup tidak jadi HTML executable; empty list/peta tetap200.
- [ ] **2. RED:** `.venv/Scripts/python.exe manage.py test recommender.tests.test_java_map --noinput`.
- [ ] **3. Implementasi:** satu SVG + handler untuk dua halaman, framing Jawa, zoom/pan bounded, tombol keyboard provinsi, status/list saat point di luar frame. Legenda membedakan cluster/deskripsi sumber tanpa mengklaim verifikasi semua koordinat.
- [ ] **4. GREEN dan browser:** klik keenam provinsi, back/reset, mobile pan/zoom, keyboard, map result session, Marina tidak memperlebar map, console bebas error. Verifikasi satu destination normal diproyeksikan di provinsinya tanpa klaim audit seluruh437.
- [ ] **5. Commit:** `feat(map): focus shared destination map on Java`.

## Task 8: Cleanup dan verifikasi final

**Files:** Modify `README.md`, `Dokumentasi.md` dan `.gitignore` jika perlu; create `docs/maintenance/java443-cleanup.md`, `recommender/tests/test_java443_workflow.py`. Candidate removal/archive: notebook02/03, XLSX1900/2337, CSV437processed, prototype Design/index dan old static/templates **hanya setelah audit referensi**; bukan daftar delete otomatis. Bukti kurasi/audit tetap, spreadsheet SPK dan DOCX tidak dihapus.

- [ ] **1. Inventaris read-only:** `git ls-files`, `rg -n` nama setiap candidate pada folder aktif terpilih; catat path tepat, pemilik/dependensi, delete/archive/retain dan cara restore. Jika audit script masih membutuhkan dataset legacy, pindahkan workflow historis bersama fixture ke arsip jelas atau pertahankan dependensi dokumentatif; jangan merusak suite audit dengan mengabaikan tes.
- [ ] **2. Tes gagal workflow:** preprocess → migrate/import temporary DB → train → GET/POST/peta menghasilkan443/label lengkap/provenance. `test_no_active_legacy_data_references` memeriksa importer/trainer/notebook/frontend, bukan melarang sejarah dokumentatif. Hash raw/evidence dan DOCX harus tidak berubah.
- [ ] **3. Cleanup via apply_patch/file operations:** delete file teks eksplisit atau native Move-Item `-LiteralPath` target workspace tervalidasi, satu shell end-to-end. Tidak recursive delete workspace, tidak menyentuh perubahan pengguna. Catat barang dipindah/dihapus dan recovery Git/archive.
- [ ] **4. Dokumentasi:** daftar file Drive wajib, perintah preprocess/migrate/import/dry-run/train/runserver, 437+6 sumber bukan seluruhnya pemerintah, enamfield C4, Tahuraimpute, Marinaflag, p99hanyafitur, median snapshot, budget estimasi, profile belum survei. Update doc workflow lama sebagai historical/inactive, jangan mengubah DOCX.
- [ ] **5. Final checks:** full Django suite, check, migration consistency, preprocessing regenerate di temporary output untuk reproducibility, import ulang lokal, training report matchedfingerprint, count443/source split437+6, browser desktop/mobile end-to-end tanpa external mutation. DOCX SHA256 awal `34EE9ED27A65CE2233D0A58B04519119DEBF5411F42F2F4347EF81C2E7259304` harus sama.
- [ ] **6. Review akhir:** gunakan requesting-code-review sesuai native skill dan tools yang tersedia; jangan membuat/mengirim pesan ke task lain tanpa izin. Jika fresh reviewer tidak tersedia, laporkan keterbatasan, lakukan self-review terdokumentasi, jangan klaim independent review.
- [ ] **7. Commit:** `chore: retire legacy data workflow and document Java443 setup`; berikan ringkasan actualtests, actualtraining, daftarcommits, backup recoverypath, remaining limitations. Jangan push atau klaim selesai bila task produk belum diverifikasi.

## Review rencana dan handoff

Self-review: seluruh 12 bagian spec dipetakan Task1–8; lima Review Focus masing-masing memiliki test owner; fungsi/field konsumsi sesuai definisi sebelumnya. Tidak ada angka silhouette yang diasumsikan. Baseline T1 tetap tercatat, bukan dikerjakan ulang.

Metode yang sudah dipilih pengguna: **native/current session**. Rencana menunggu persetujuan pengguna sebelum implementasi; setelah persetujuan baca `superpowers:executing-plans` dan laksanakan Task1–8 tanpa worktree, dengan commit terpisah. UI-UX Pro Max dibaca/diterapkan pada Task6.
