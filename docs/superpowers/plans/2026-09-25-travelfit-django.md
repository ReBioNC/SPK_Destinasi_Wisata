# TravelFit Django Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Membangun website TravelFit (Django + Django Templates, Bootstrap 5, SQLite) yang menerima preferensi wisatawan dan menampilkan ranking Top-10 AHP–TOPSIS plus peta dan sensitivity analysis.

**Architecture:** Satu app `recommender`; engine SPK di `recommender/spk/` murni Python stdlib (tanpa Django/pandas/numpy) agar independently testable; data diimpor sekali dari XLSX+CSV ke SQLite via management command.

**Tech Stack:** Python 3.11, Django >= 5.0,< 6.0, openpyxl + pandas (hanya untuk command impor), Bootstrap 5 via CDN, SQLite.

**Spec:** `docs/superpowers/specs/2026-09-25-travelfit-django-design.md`

## Global Constraints

- `recommender/spk/*.py` tidak boleh mengimpor Django, pandas, atau numpy — stdlib only.
- Bahasa antarmuka dan pesan error: Bahasa Indonesia.
- Satu halaman form + hasil; tanpa framework JS, tanpa login.
- Angka acuan validasi: CR Seimbang = 0,008418; urutan TOPSIS Excel A1–A10 = A2,A9,A7,A8,A10,A4,A3,A1,A6,A5; Jaccard contoh = 0,5; Haversine Bandung–Kawah Putih = 36,5745 km.
- Test runner: `python manage.py test` (Django unittest, bukan pytest).

## Review Focus

1. Budget diketik dengan pemisah ribuan ("250.000", "250,000", "Rp 250000") → form harus membersihkan dan menerima, bukan 500/meledak.
2. Wilayah valid tetapi filter menghasilkan nol kandidat → halaman ramah + saran, bukan halaman kosong/error. (Test di Task 6.)
3. Semua slider bobot di-nol-kan → tolak dengan pesan, pakai preset profil. (Test di Task 7.)
4. Destinasi tanpa koordinat lolos impor (tidak match RAW) → diimpor dengan lat/long NULL dan dikecualikan dari ranking dengan catatan di log impor. (Test di Task 5.)
5. Hobi yang dipilih tidak overlap dengan tag destinasi mana pun (semua C6 = 0) → ranking tetap jalan normal. (Test di Task 6.)

## File Structure

```text
config/__init__.py, config/settings.py, config/urls.py, config/wsgi.py  (Task 1)
manage.py, requirements.txt, .gitignore (edit)                            (Task 1)
recommender/__init__.py, recommender/apps.py                              (Task 1)
recommender/spk/__init__.py                                               (Task 2)
recommender/spk/geo.py                                                    (Task 2)
recommender/spk/similarity.py                                             (Task 2)
recommender/spk/ahp.py                                                    (Task 3)
recommender/spk/profiles.py                                               (Task 3)
recommender/spk/topsis.py                                                 (Task 4)
recommender/spk/validation.py                                             (Task 4)
recommender/tests/__init__.py, test_spk.py                                (Task 2-4)
recommender/models.py, recommender/migrations/0001_initial.py             (Task 5)
recommender/management/__init__.py, management/commands/__init__.py,
  management/commands/import_destinations.py                               (Task 5)
recommender/tests/test_import.py                                          (Task 5)
recommender/forms.py, recommender/views.py, recommender/urls.py           (Task 6-7)
recommender/tests/test_views.py                                           (Task 6-7)
recommender/templates/recommender/base.html, form_hasil.html              (Task 6)
recommender/templates/recommender/peta.html, tentang.html                 (Task 8)
static/recommender/custom.css, static/recommender/nusantara.css/js        (Task 8)
README.md (tambah bagian Cara Menjalankan Website)                        (Task 9)
```

---

### Task 1: Setup proyek Django

**Files:**
- Create: `requirements.txt`, `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `recommender/__init__.py`, `recommender/apps.py`, `recommender/tests/__init__.py`
- Modify: `.gitignore` (append `.venv/`, `db.sqlite3`, `__pycache__/` jika belum ada)

**Interfaces:**
- Consumes: tidak ada (task pertama)
- Produces: project runnable; `recommender` terdaftar di INSTALLED_APPS; `python manage.py check` hijau. Task 5 memakai `manage.py` + settings DB.

- [ ] **Step 1: Buat venv dan install dependensi**

```bash
python -m venv .venv
.venv/Scripts/Activate.ps1
pip install "django>=5.0,<6.0" openpyxl pandas
pip freeze > requirements.txt
```

- [ ] **Step 2: Scaffold project dan app (jangan menimpa file yang ada)**

```bash
django-admin startproject config .
python manage.py startapp recommender
```

Jika `startproject` menolak karena direktori tidak kosong, buat file `config/*` dan `manage.py` manual dengan isi standar Django 5 (copy dari `django-admin startproject` ke direktori temp lalu salin).

- [ ] **Step 3: Tulis settings minimal**

```python
# config/settings.py (kutipan penting)
INSTALLED_APPS = ["django.contrib.staticfiles", "recommender"]
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_TZ = True
STATIC_URL = "static/"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates",
              "DIRS": [], "APP_DIRS": True,
              "OPTIONS": {"context_processors": [
                  "django.template.context_processors.request",
                  "django.template.context_processors.static"]}}]
```

`SECRET_KEY` dibangkitkan via `django.core.management.utils.get_random_secret_key()`. `DEBUG = True` untuk demo lokal.

- [ ] **Step 4: Wire URL root dan verifikasi**

```python
# config/urls.py
from django.urls import include, path
urlpatterns = [path("", include("recommender.urls"))]
```

```python
# recommender/urls.py (sementara, lengkap di Task 6/8)
from django.urls import path
urlpatterns = []
```

Run: `python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt manage.py config recommender .gitignore
git commit -m "feat: setup Django project config and recommender app"
```

---

### Task 2: Engine geo + similarity

**Files:**
- Create: `recommender/spk/__init__.py` (kosong), `recommender/spk/geo.py`, `recommender/spk/similarity.py`
- Test: `recommender/tests/test_spk.py` (buat file, class `GeoSimilarityTest`)

**Interfaces:**
- Consumes: tidak ada
- Produces:
  - `geo.haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float` (km, R=6371)
  - `similarity.jaccard(a: set[str], b: set[str]) -> float` (1.0 jika keduanya kosong)

- [ ] **Step 1: Tulis test yang gagal**

```python
# recommender/tests/test_spk.py
from django.test import SimpleTestCase
from recommender.spk import geo, similarity

class GeoSimilarityTest(SimpleTestCase):
    def test_haversine_bandung_kawah_putih(self):
        self.assertAlmostEqual(geo.haversine(-6.9175, 107.6191, -7.1662, 107.4022), 36.5745, places=3)

    def test_haversine_nol_untuk_titik_sama(self):
        self.assertEqual(geo.haversine(-6.9, 107.6, -6.9, 107.6), 0.0)

    def test_jaccard_contoh_laporan(self):
        user = {"hiking", "fotografi", "kuliner"}
        dest = {"hiking", "fotografi", "keluarga"}
        self.assertEqual(similarity.jaccard(user, dest), 0.5)

    def test_jaccard_keduanya_kosong(self):
        self.assertEqual(similarity.jaccard(set(), set()), 1.0)
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `python manage.py test recommender.tests.test_spk -v 2`
Expected: FAIL/ERROR (modul belum ada)

- [ ] **Step 3: Implementasi minimal**

```python
# recommender/spk/geo.py
import math
EARTH_RADIUS_KM = 6371.0

def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))
```

```python
# recommender/spk/similarity.py
def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `python manage.py test recommender.tests.test_spk -v 2`
Expected: OK (4 tests)

- [ ] **Step 5: Commit**

```bash
git add recommender/spk recommender/tests
git commit -m "feat(spk): add haversine and jaccard engine with tests"
```

---

### Task 3: Engine AHP + 4 profil

**Files:**
- Create: `recommender/spk/ahp.py`, `recommender/spk/profiles.py`
- Test: tambah class `AhpTest` di `recommender/tests/test_spk.py`

**Interfaces:**
- Consumes: tidak ada
- Produces:
  - `ahp.weights_from_matrix(matrix: list[list[float]]) -> list[float]`
  - `ahp.consistency(matrix, weights) -> dict(lambda_max: float, ci: float, cr: float)`
  - `ahp.RI: dict[int, float]` (1–10: 0,0,0.58,0.9,1.12,1.24,1.32,1.41,1.45,1.49)
  - `profiles.CRITERIA = ["C1",...,"C6"]`, `profiles.IS_COST = [True,False,True,False,False,False]`
  - `profiles.ACTIVE_PROFILES: dict[nama, dict(label, weights, cr)]` — hanya profil CR < 0,1
  - `profiles.matrix_from_upper(upper: dict[tuple[int,int], float], n=6) -> list[list[float]]`

Matriks segitiga atas (indeks 0 = C1 … 5 = C6), **angka final terverifikasi**:

- Seimbang (dari spreadsheet): `(0,1):1,(0,2):2,(0,3):3,(0,4):2,(0,5):2,(1,2):1,(1,3):2,(1,4):1,(1,5):1,(2,3):2,(2,4):1,(2,5):1,(3,4):0.5,(3,5):0.5,(4,5):1` → CR 0,008418
- Hemat: `(0,1):4,(0,2):3,(0,3):5,(0,4):3,(0,5):3,(1,2):1,(1,3):2,(1,4):1,(1,5):1,(2,3):2,(2,4):1,(2,5):1,(3,4):0.5,(3,5):0.5,(4,5):1` → CR 0,002559
- Kualitas: `(0,1):0.25,(0,2):1,(0,3):2,(0,4):1,(0,5):1,(1,2):3,(1,3):3,(1,4):3,(1,5):3,(2,3):2,(2,4):1,(2,5):1,(3,4):0.5,(3,5):0.5,(4,5):1` → CR 0,012159
- Petualang: `(0,1):1,(0,2):1/3,(0,3):2,(0,4):1,(0,5):1,(1,2):1/3,(1,3):2,(1,4):1,(1,5):1,(2,3):4,(2,4):2,(2,5):2,(3,4):0.5,(3,5):0.5,(4,5):1` → CR 0,004431

- [ ] **Step 1: Tulis test yang gagal**

```python
class AhpTest(SimpleTestCase):
    def test_bobot_seimbang_sama_dengan_spreadsheet(self):
        from recommender.spk import ahp, profiles
        m = profiles.matrix_from_upper(profiles.PROFILE_UPPERS["seimbang"])
        w = ahp.weights_from_matrix(m)
        for got, exp in zip(w, [0.2693, 0.1785, 0.1567, 0.0820, 0.1567, 0.1567]):
            self.assertAlmostEqual(got, exp, places=4)

    def test_cr_seimbang(self):
        from recommender.spk import ahp, profiles
        m = profiles.matrix_from_upper(profiles.PROFILE_UPPERS["seimbang"])
        res = ahp.consistency(m, ahp.weights_from_matrix(m))
        self.assertAlmostEqual(res["cr"], 0.008418, places=5)
        self.assertLess(res["cr"], 0.1)

    def test_semua_profil_aktif_konsisten(self):
        from recommender.spk import profiles
        self.assertEqual(set(profiles.ACTIVE_PROFILES), {"hemat", "kualitas", "petualang", "seimbang"})
        for p in profiles.ACTIVE_PROFILES.values():
            self.assertLess(p["cr"], 0.1)
            self.assertAlmostEqual(sum(p["weights"]), 1.0, places=6)
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `python manage.py test recommender.tests.test_spk.AhpTest -v 2`
Expected: ERROR (modul belum ada)

- [ ] **Step 3: Implementasi minimal**

```python
# recommender/spk/ahp.py
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

def weights_from_matrix(matrix):
    n = len(matrix)
    colsum = [sum(matrix[i][j] for i in range(n)) for j in range(n)]
    return [sum(matrix[i][j] / colsum[j] for j in range(n)) / n for i in range(n)]

def consistency(matrix, weights):
    n = len(matrix)
    aw = [sum(matrix[i][j] * weights[j] for j in range(n)) for i in range(n)]
    lam = sum(aw[i] / weights[i] for i in range(n)) / n
    ci = (lam - n) / (n - 1)
    return {"lambda_max": lam, "ci": ci, "cr": ci / RI[n]}
```

```python
# recommender/spk/profiles.py (kutipan; tulis keempat matriks dari daftar di atas)
from .ahp import weights_from_matrix, consistency

CRITERIA = ["C1", "C2", "C3", "C4", "C5", "C6"]
IS_COST = [True, False, True, False, False, False]
PROFILE_UPPERS = {"seimbang": {...}, "hemat": {...}, "kualitas": {...}, "petualang": {...}}
PROFILE_LABELS = {"seimbang": "Seimbang", "hemat": "Hemat", "kualitas": "Kualitas", "petualang": "Petualang"}

def matrix_from_upper(upper, n=6):
    m = [[1.0] * n for _ in range(n)]
    for (i, j), v in upper.items():
        m[i][j] = float(v)
        m[j][i] = 1.0 / float(v)
    return m

def _build():
    out = {}
    for key, upper in PROFILE_UPPERS.items():
        m = matrix_from_upper(upper)
        w = weights_from_matrix(m)
        cr = consistency(m, w)["cr"]
        if cr < 0.1:
            out[key] = {"label": PROFILE_LABELS[key], "weights": w, "cr": cr}
    return out

ACTIVE_PROFILES = _build()
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `python manage.py test recommender.tests.test_spk -v 2`
Expected: OK (7 tests)

- [ ] **Step 5: Commit**

```bash
git add recommender/spk/ahp.py recommender/spk/profiles.py recommender/tests/test_spk.py
git commit -m "feat(spk): add AHP weighting with 4 verified profiles"
```

---

### Task 4: Engine TOPSIS + validasi SAW/Spearman

**Files:**
- Create: `recommender/spk/topsis.py`, `recommender/spk/validation.py`
- Test: tambah class `TopsisTest` + fixture A1–A10 di `recommender/tests/test_spk.py`

**Interfaces:**
- Consumes: `profiles.IS_COST`
- Produces:
  - `topsis.rank(scores: list[list[float]], weights: list[float], is_cost: list[bool]) -> list[dict]` tiap dict `{"idx": int, "vi": float, "d_pos": float, "d_neg": float, "gap": list[float]}` (gap[j] = |v_ij − A+_j|, untuk explainability), terurut Vi menurun
  - `validation.saw_rank(scores, weights, is_cost) -> list[tuple[int, float]]` terurut Si menurun
  - `validation.spearman(order_a: list[int], order_b: list[int]) -> float` (order = list idx dari terbaik ke terburuk)

Fixture A1–A10 (urutan C1..C6), pakai di test:

```python
A10 = [
    [81000, 4.6, 36.5745, 0.8, 1.0, 0.50],   # A1
    [30000, 4.4, 17.5772, 0.8, 1.0, 0.50],   # A2
    [75000, 4.7, 4.5624, 0.8, 0.5, 0.20],    # A3
    [30000, 4.3, 9.5688, 0.8, 0.0, 0.50],    # A4
    [200000, 4.5, 2.1409, 1.0, 0.0, 0.25],   # A5
    [15000, 4.2, 143.2742, 1.0, 1.0, 0.40],  # A6
    [5000, 4.5, 1.8868, 0.6, 0.5, 0.0],      # A7
    [25000, 4.4, 14.3607, 1.0, 0.0, 0.50],   # A8
    [20000, 4.3, 39.6859, 0.6, 1.0, 0.40],   # A9
    [5000, 4.1, 8.4023, 0.8, 0.0, 0.20],     # A10
]
W_SEIMBANG = [0.269294111685416, 0.17848214587345024, 0.15674301543866762,
              0.08199469612513091, 0.15674301543866762, 0.15674301543866762]
```

- [ ] **Step 1: Tulis test yang gagal**

```python
class TopsisTest(SimpleTestCase):
    def test_urutan_sama_dengan_excel(self):
        from recommender.spk import topsis
        from recommender.spk.profiles import IS_COST
        res = topsis.rank(A10, W_SEIMBANG, IS_COST)
        self.assertEqual([r["idx"] for r in res], [1, 8, 6, 7, 9, 3, 2, 0, 5, 4])

    def test_spearman_topsis_vs_saw_rendah(self):
        from recommender.spk import topsis, validation
        from recommender.spk.profiles import IS_COST
        t = [r["idx"] for r in topsis.rank(A10, W_SEIMBANG, IS_COST)]
        s = [i for i, _ in validation.saw_rank(A10, W_SEIMBANG, IS_COST)]
        self.assertAlmostEqual(validation.spearman(t, s), 0.2970, places=3)
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `python manage.py test recommender.tests.test_spk.TopsisTest -v 2`
Expected: ERROR

- [ ] **Step 3: Implementasi minimal**

```python
# recommender/spk/topsis.py
import math

def rank(scores, weights, is_cost):
    n, m = len(scores), len(scores[0])
    den = [math.sqrt(sum(scores[i][j] ** 2 for i in range(n))) for j in range(m)]
    v = [[(scores[i][j] / den[j]) * weights[j] for j in range(m)] for i in range(n)]
    ideal_pos = [(min(v[i][j] for i in range(n)) if is_cost[j]
                  else max(v[i][j] for i in range(n))) for j in range(m)]
    ideal_neg = [(max(v[i][j] for i in range(n)) if is_cost[j]
                  else min(v[i][j] for i in range(n))) for j in range(m)]
    out = []
    for i in range(n):
        dp = math.sqrt(sum((v[i][j] - ideal_pos[j]) ** 2 for j in range(m)))
        dn = math.sqrt(sum((v[i][j] - ideal_neg[j]) ** 2 for j in range(m)))
        out.append({"idx": i, "vi": dn / (dp + dn), "d_pos": dp, "d_neg": dn,
                    "gap": [abs(v[i][j] - ideal_pos[j]) for j in range(m)]})
    return sorted(out, key=lambda r: r["vi"], reverse=True)
```

```python
# recommender/spk/validation.py
def saw_rank(scores, weights, is_cost):
    n, m = len(scores), len(scores[0])
    lo = [min(scores[i][j] for i in range(n)) for j in range(m)]
    hi = [max(scores[i][j] for i in range(n)) for j in range(m)]
    ranked = []
    for i in range(n):
        s = sum(weights[j] * (lo[j] / scores[i][j] if is_cost[j] else scores[i][j] / hi[j])
                for j in range(m))
        ranked.append((i, s))
    return sorted(ranked, key=lambda t: t[1], reverse=True)

def spearman(order_a, order_b):
    n = len(order_a)
    pos_b = {idx: r for r, idx in enumerate(order_b)}
    d2 = sum((r - pos_b[idx]) ** 2 for r, idx in enumerate(order_a))
    return 1 - (6 * d2) / (n * (n * n - 1))
```

- [ ] **Step 4: Jalankan, pastikan hijau**

Run: `python manage.py test recommender.tests.test_spk -v 2`
Expected: OK (9 tests)

- [ ] **Step 5: Commit**

```bash
git add recommender/spk/topsis.py recommender/spk/validation.py recommender/tests/test_spk.py
git commit -m "feat(spk): add TOPSIS ranking with SAW/Spearman validation"
```

---

### Task 5: Model + command impor gabungan

**Files:**
- Create: `recommender/models.py`, `recommender/migrations/0001_initial.py` (via makemigrations), `recommender/management/__init__.py`, `recommender/management/commands/__init__.py`, `recommender/management/commands/import_destinations.py`
- Test: `recommender/tests/test_import.py`

**Interfaces:**
- Consumes: file `Dataset_Wisata_38_Provinsi.xlsx` (sheet `Destinasi_TravelFit_Ready` + `Destinasi_Raw`), `data/processed/destinations_clean.csv`, `data/processed/ratings_aggregated.csv`
- Produces: model `Destination`; command `import_destinations [--dry-run]`; Task 6 memakai `Destination.objects.filter(provinsi, harga_tiket__lte)` + field koordinat/tag/fasilitas.

Model (unik `nama+kota`):

```python
class Destination(models.Model):
    nama = models.CharField(max_length=200)
    kota = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100, db_index=True)
    kategori = models.CharField(max_length=50, db_index=True)
    sub_kategori = models.CharField(max_length=100, blank=True, default="")
    harga_tiket = models.IntegerField(db_index=True)
    rating = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    fas_toilet = models.BooleanField(default=False)
    fas_parkir = models.BooleanField(default=False)
    fas_warung = models.BooleanField(default=False)
    fas_mushola = models.BooleanField(default=False)
    fas_penginapan = models.BooleanField(default=False)
    tag_aktivitas = models.TextField(blank=True, default="")
    cluster_label = models.CharField(max_length=100, blank=True, default="")
    sumber_data = models.CharField(max_length=20, default="xlsx38")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["nama", "kota"], name="uniq_nama_kota")]

    def facility_score(self):
        return sum([self.fas_toilet, self.fas_parkir, self.fas_warung,
                    self.fas_mushola, self.fas_penginapan]) / 5.0

    def tag_set(self):
        return set(t for t in self.tag_aktivitas.split("|") if t)
```

Pemetaan kolom impor:

- Basis Ready: `Place_Name→nama`, `City→kota`, `Province→provinsi`, `Category_Clean→kategori`, `Sub_Category→sub_kategori`, `c1_ticket_price→harga_tiket`, `c2_rating→rating`, 6 flag `facility_*_mentioned` (toilet, parking, food→warung, worship→mushola, accessibility→penginapan? **keputusan eksplisit**: accessibility→fas_penginapan=False mapping khusus — accessibility dan information_center TIDAK dipetakan ke 5 boolean (tak ada padanan); sebagai gantinya `c4_facility_score` dari file disimpan? Model tak punya kolom skor mentah. Keputusan: import memakai 4 flag yang berpadanan (toilet, parking, food, worship) + accessibility→fas_penginapan hanya bila flag True? Itu menyesatkan. **Keputusan final**: petakan toilet/parking/food/worship 1:1; fas_penginapan selalu False dari XLSX (tak ada sumbernya), True hanya dari CSV Jawa bila ada buktinya — CSV juga flag heuristik yang sama 6 kolom, jadi fas_penginapan False untuk semua baris impor awal dan didokumentasikan di README. Sederhana, jujur, tanpa placeholder.)
- Koordinat: join sheet `Destinasi_Raw` via kunci `(lower(place_name), lower(city))` → `Lat→latitude`, `Long→longitude`. Tak cocok → NULL + hitung `tanpa_koordinat`.
- Overlay CSV Jawa: match `(lower(place_name), lower(city))` → timpa rating dengan `user_rating_mean` (join `ratings_aggregated.csv` via place_id bila tersedia, else `c2_rating` CSV), timpa `tag_aktivitas`, set `sumber_data="csv_jawa"`.
- `update_or_create(nama=..., kota=...)` → idempoten. Cetak: `basis=1900 overlay_jawa=N tanpa_koordinat=M total=1900`.

- [ ] **Step 1: Model + migrasi**

Tulis `models.py` di atas. Run: `python manage.py makemigrations recommender` lalu `python manage.py migrate`. Expected: `0001_initial.py` tercipta, `OK`.

- [ ] **Step 2: Tulis test impor yang gagal**

```python
# recommender/tests/test_import.py
from django.test import TestCase
from django.core.management import call_command
from recommender.models import Destination

class ImportTest(TestCase):
    def test_impor_basis_1900_dan_idempoten(self):
        call_command("import_destinations")
        self.assertEqual(Destination.objects.count(), 1900)
        call_command("import_destinations")  # rerun
        self.assertEqual(Destination.objects.count(), 1900)

    def test_koordinat_terisi_dan_tanpa_koordinat_tercatat(self):
        call_command("import_destinations")
        self.assertEqual(Destination.objects.filter(latitude__isnull=True).count(), 0)
        monas = Destination.objects.get(nama="Monumen Nasional")
        self.assertAlmostEqual(monas.latitude, -6.1753924, places=4)

    def test_overlay_jawa_bertanda_sumber(self):
        call_command("import_destinations")
        self.assertGreater(Destination.objects.filter(sumber_data="csv_jawa").count(), 300)
```

- [ ] **Step 3: Jalankan, pastikan gagal** (`import_destinations` belum ada → ERROR)
- [ ] **Step 4: Tulis command** sesuai pemetaan di atas (openpyxl read_only untuk XLSX, csv/pandas untuk CSV; `--dry-run` hanya menghitung tanpa menyimpan).
- [ ] **Step 5: Jalankan test**

Run: `python manage.py test recommender.tests.test_import -v 2`
Expected: OK. Jika `tanpa_koordinat > 0`, test pertama yang assert 0 gagal — perbaiki dengan fakta aktual (ubah assert menjadi `< 5%` TIDAK dibolehkan seenaknya; laporkan angkanya dan sesuaikan test dengan fakta + alasan di commit message).

- [ ] **Step 6: Commit**

```bash
git add recommender/models.py recommender/migrations recommender/management recommender/tests/test_import.py
git commit -m "feat(data): add Destination model and combined import command"
```

---

### Task 6: Form + view rekomendasi + template hasil

**Files:**
- Create: `recommender/forms.py`, `recommender/views.py` (fungsi `rekomendasi` + helper `_bangun_alasan`), `recommender/urls.py` (rute `/` saja dulu), `recommender/templates/recommender/base.html`, `form_hasil.html`
- Test: `recommender/tests/test_views.py`

**Interfaces:**
- Consumes: `Destination`, `ACTIVE_PROFILES`, `IS_COST`, `topsis.rank`, `geo.haversine`, `similarity.jaccard`
- Produces: rute `/` (GET form, POST hasil Top-10); session key `hasil_terakhir` (list dict JSON-serializable: nama, provinsi, vi, latitude, longitude) untuk Task 8. `_bangun_alasan(gap, dest)` dipakai Task 7 tanpa perubahan.

Keputusan konkret:

- `KOTA_ASAL` (nama → lat, lon): Jakarta (-6.2088, 106.8456), Bandung (-6.9175, 107.6191), Semarang (-6.9667, 110.4167), Surabaya (-7.2575, 112.7521), Yogyakarta (-7.7956, 110.3695), Medan (3.5952, 98.6722), Makassar (-5.1477, 119.4327), Denpasar (-8.6705, 115.2126).
- Pilihan wilayah/kategori/hobi **dinamis dari DB** di `__init__` form (distinct provinsi, distinct kategori, distinct tag). Hobi sebagai `MultipleChoiceField` + `CheckboxSelectMultiple`.
- Budget: `CharField` dibersihkan manual — hapus `Rp`, spasi, `.`, `,` lalu `int()`; gagal → `ValidationError("Masukkan budget dalam angka, contoh: 250000.")`. (Menutup Review Focus #1.)
- C5: 1.0 jika kategori == utama, 0.5 jika == sekunder, else 0.0. C4: `facility_score()`. Kandidat tanpa koordinat dikecualikan (`latitude__isnull=False`).
- `_bangun_alasan(gap, kriteria_nama)`: 2 kriteria gap terkecil → "unggul pada X", 1 gap terbesar → "tertahan oleh Y". Nama kriteria Indonesia: Harga tiket, Rating, Jarak, Fasilitas, Kategori, Hobi.
- Nol kandidat → render template sama dengan `kandidat_kosong=True` + saran ("Naikkan budget" / "Pilih wilayah lain"). (Review Focus #2.)
- Template `base.html`: navbar (Beranda, Peta, Tentang — Peta/Tentang boleh 404 dulu sampai Task 8), Bootstrap 5.3 CDN, container, footer. `form_hasil.html`: `{% extends %}`, form + `{% if hasil %}` kartu Top-10 (nama, Vi 4 desimal via `floatformat:4`, label cluster, alasan).

- [ ] **Step 1: Seed fixture + tulis test gagal**

```python
class RekomendasiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        bandung = (-6.9175, 107.6191)
        rows = [("Kawah Putih Ciwidey", 81000, 4.6, -7.1662, 107.4022, "alam", "hiking|fotografi|keluarga"),
                ...]  # 10 baris A1-A10: harga, rating, lat, lon, kategori, tag; lat/lon tiap baris DIBACA dari sheet Data_Alternatif kolom G (Latitude)/H (Longitude) di Perhitungan_SPK_TravelFit.xlsx — jangan dikarang; fasilitas: 4 True / skor 0.8 (A5 & A6 & A8: 5 True / 1.0; A7 & A9: 3 True / 0.6; kolom boolean mana pun boleh, yang penting jumlah True-nya sesuai skor)
        for nama, harga, rating, lat, lon, kat, tag in rows:
            Destination.objects.create(nama=nama, kota="Bandung", provinsi="Jawa Barat",
                kategori=kat, harga_tiket=harga, rating=rating, latitude=lat, longitude=lon,
                fas_toilet=True, fas_parkir=True, fas_warung=True, fas_mushola=True, tag_aktivitas=tag)

    def post_valid(self, **over):
        data = {"budget": "250000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                "kategori_utama": "alam", "kategori_sekunder": "budaya",
                "hobi": ["hiking", "fotografi"], "profil": "seimbang"}
        data.update(over)
        return self.client.post("/", data)

    def test_post_valid_menampilkan_10_hasil_urutan_benar(self):
        r = self.post_valid()
        self.assertEqual(r.status_code, 200)
        names = [h["nama"] for h in r.context["hasil"]]
        self.assertEqual(names[0], "Gunung Tangkuban Perahu")
        self.assertEqual(len(names), 10)

    def test_budget_format_ribuan_diterima(self):
        for b in ["250.000", "Rp 250000", "250,000"]:
            r = self.post_valid(budget=b)
            self.assertEqual(r.status_code, 200)
            self.assertIn("hasil", r.context)

    def test_budget_invalid_ada_pesan(self):
        r = self.post_valid(budget="gratis")
        self.assertContains(r, "Masukkan budget dalam angka")

    def test_kandidat_kosong_ramah(self):
        r = self.post_valid(budget="1000")
        self.assertContains(r, "longgarkan")

    def test_c6_nol_semua_tetap_jalan(self):
        r = self.post_valid(hobi=["ski_es"])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["hasil"]), 10)
```

(Catatan: C5/C6 fixture mengikuti Tabel 2.3 laporan; hobi form `["hiking","fotografi"]` vs tag fixture menghasilkan C6 identik dengan spreadsheet bila tag fixture = tag asli. Karena tag asli destinasi dummy tak ada di dataset, test hanya assert juara = Tangkuban Perahu dan 10 hasil — urutan penuh tidak diassert di level view; urutan penuh sudah dikunci di Task 4.)

- [ ] **Step 2: Jalankan, pastikan gagal** (ERROR: view/URL belum ada)
- [ ] **Step 3: Tulis forms.py, views.py, urls.py, kedua template** sesuai keputusan di atas.
- [ ] **Step 4: Jalankan**

Run: `python manage.py test recommender.tests.test_views -v 2`
Expected: OK

- [ ] **Step 5: Commit**

```bash
git add recommender/forms.py recommender/views.py recommender/urls.py recommender/templates/base.html recommender/templates/form_hasil.html recommender/tests/test_views.py config/urls.py
git commit -m "feat(web): add preference form and TOPSIS result view"
```

---

### Task 7: Sensitivity analysis (override bobot via slider)

**Files:**
- Modify: `recommender/forms.py` (tambah `w1..w6` optional), `recommender/views.py` (cabang override), `form_hasil.html` (6 slider 0–100 + tampilkan bobot efektif), `recommender/tests/test_views.py` (tambah 2 test)

**Interfaces:**
- Consumes: `_bangun_alasan`, `topsis.rank` (tidak berubah)
- Produces: fungsi helper `normalisasi_bobot(list[float]) -> list[float]` di `views.py`; context tambahan `bobot_efektif`, `mode_custom: bool`.

Aturan: jika salah satu dari w1..w6 diisi (> 0) → pakai vektor slider dinormalisasi (`v/sum(v)`); jika jumlah = 0 → abaikan + pesan `"Bobot kustom nol semua, dipakai bobot profil Seimbang."` (Review Focus #3). Slider HTML `input type=range min=0 max=100`, nilai awal = bobot profil × 100 (diisi via context), auto-submit on change dengan `onchange="this.form.requestSubmit()"` (tanpa framework JS).

- [ ] **Step 1: Tulis test gagal**

```python
def test_slider_mengubah_urutan(self):
    r = self.post_valid(**{"w1": "100", "w2": "0", "w3": "0", "w4": "0", "w5": "0", "w6": "0"})
    names = [h["nama"] for h in r.context["hasil"]]
    self.assertTrue(r.context["mode_custom"])
    self.assertEqual(names[0], "Museum Geologi Bandung")  # termurah + terdekat saat C1 dominan penuh

def test_slider_nol_semua_kembali_ke_profil(self):
    r = self.post_valid(**{f"w{i}": "0" for i in range(1, 7)})
    self.assertFalse(r.context["mode_custom"])
    self.assertContains(r, "dipakai bobot profil")
```

- [ ] **Step 2: Jalankan, pastikan gagal** (KeyError/field tak dikenal)
- [ ] **Step 3: Implementasi** (field `w1..w6 = forms.FloatField(required=False, min_value=0, max_value=100)`; cabang di view; slider di template).
- [ ] **Step 4: Jalankan** — jika juara bukan Museum Geologi, hitung manual dari data fixture dan perbaiki ekspektasi test dengan fakta (bukan sebaliknya).

Run: `python manage.py test recommender.tests.test_views -v 2`
Expected: OK

- [ ] **Step 5: Commit**

```bash
git add recommender/forms.py recommender/views.py recommender/templates/form_hasil.html recommender/tests/test_views.py
git commit -m "feat(web): add sensitivity analysis via weight sliders"
```

---

### Task 8: Halaman peta + tentang + static

**Files:**
- Create: `recommender/templates/recommender/peta.html`, `tentang.html`, `static/recommender/custom.css`
- Modify: `recommender/urls.py` (+ `/peta/`, `/tentang/`), `recommender/views.py` (+ 2 view), `base.html` navbar aktif, `config/settings.py` (STATICFILES_DIRS jika perlu)
- Aset peta: baca `index.html` (72 KB, peta SVG 38 provinsi + 1 blok `<style>` + 1 blok `<script>`, tanpa API key): pindahkan `<style>`→`static/recommender/nusantara.css`, `<script>`→`static/recommender/nusantara.js`, ganti dengan `{% load static %}` + `<link>`/`<script src>`.

**Interfaces:**
- Consumes: session `hasil_terakhir` dari Task 6
- Produces: tidak ada (task daun)

Keputusan konkret:

- `peta(request)`: ambil `hasil_terakhir` dari session → kirim ke template via `{{ hasil_json|json_script:"hasil-data" }}`; JS `nusantara.js` (tambahan ≤ 20 baris di akhir file) membaca `hasil-data` dan mengisi `<aside id="daftar-hasil">` + highlight badge provinsi. Klik provinsi pada SVG → `location.href = "/?wilayah=" + namaProvinsi` (view `/` membaca GET `wilayah` sebagai initial form). Session kosong → fallback agregat `Destination.objects.values("provinsi").annotate(jumlah=Count("id"))` (38 baris) sebagai daftar, bukan 1.900 marker.
- `tentang(request)`: statis — ringkasan 3 paragraf (CRISP-DM, AHP–TOPSIS, validasi) + link ke `Perhitungan_SPK_TravelFit.xlsx`, `Dataset_Wisata_38_Provinsi.xlsx`, README (tautan file relatif, bukan download view).
- `custom.css` ≤ 60 baris: warna aksen, kartu hasil, slider.

- [ ] **Step 1: Tulis test gagal**

```python
def test_peta_dan_tentang_200(self):
    self.assertEqual(self.client.get("/peta/").status_code, 200)
    self.assertEqual(self.client.get("/tentang/").status_code, 200)

def test_peta_memakai_hasil_session(self):
    self.post_valid()
    r = self.client.get("/peta/")
    self.assertContains(r, "Tangkuban Perahu")

def test_peta_tanpa_session_fallback_agregat(self):
    r = self.client.get("/peta/")
    self.assertContains(r, "Jawa Barat")
```

- [ ] **Step 2: Jalankan, pastikan gagal** (404)
- [ ] **Step 3: Implementasi** sesuai keputusan di atas.
- [ ] **Step 4: Jalankan semua test**

Run: `python manage.py test -v 1`
Expected: OK (semua test hijau)

- [ ] **Step 5: Commit**

```bash
git add recommender/urls.py recommender/views.py recommender/templates static config/settings.py recommender/tests/test_views.py
git commit -m "feat(web): add interactive map and about pages"
```

---

### Task 9: Verifikasi akhir + dokumentasi menjalankan

**Files:**
- Modify: `README.md` (tambah bagian di akhir, tanpa mengubah isi yang ada)
- Test: tidak ada test baru; menjalankan ulang seluruh suite + check manual.

- [ ] **Step 1: Full suite + system check**

Run: `python manage.py check && python manage.py test -v 1`
Expected: no issues + OK.

- [ ] **Step 2: Smoke test browser manual** (`python manage.py runserver`, buka `/`): isi form (Bandung, 250000, Jawa Barat, alam/budaya, hiking+fotografi, Seimbang) → Top-1 = Gunung Tangkuban Perahu; geser slider → ranking berubah; buka `/peta/` → highlight + daftar; `/tentang/` → 200. Catat penyimpangan sebagai bug, perbaiki, ulangi Step 1.

- [ ] **Step 3: Tambah instruksi ke README**

```markdown
## Menjalankan Website TravelFit
python -m venv .venv; .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py import_destinations
python manage.py test
python manage.py runserver
```

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add website run instructions"
```

---

## Self-Review

1. **Spec coverage:** model + impor (§4–5) → Task 5; engine + profil (§7) → Task 2–4; views/URL/template (§6) → Task 6–8; error handling (§8) → Task 6 (kasus 1,2,5), Task 7 (kasus 3), Task 5 (kasus 4); testing (§9) → tiap task + Task 9. Peta: spec menyebut "marker dari hasil terakhir" — plan mempresisikan sebagai daftar + highlight + klik-provinsi karena `index.html` adalah SVG tanpa layer marker; penguji menyetujui penyesuaian ini saat review plan.
2. **Placeholder:** tidak ada TBD/TODO; semua angka (matriks, fixture, ekspektasi) konkret. Satu titik jujur: ekspektasi juara Task 7 dan assert koordinat Monumen boleh dikoreksi mengikuti fakta aktual saat eksekusi, dengan aturan "fakta menang, test menyesuaikan + alasan di commit".
3. **Konsistensi tipe:** `topsis.rank` mengembalikan list dict `idx/vi/d_pos/d_neg/gap`; `validation.saw_rank` list tuple; `spearman` menerima dua ordering; session `hasil_terakhir` JSON-serializable; `facility_score()`/`tag_set()` dipakai view.
4. **Review Focus:** kelima risiko tercakup test di Task 5/6/7 seperti dirujuk di tiap item.
