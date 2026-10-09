"""Read-only verification of active destinations, notebook code, and report math."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.http import HttpResponse
from django.test import RequestFactory
from recommender import views
from recommender.data_pipeline import validate_artifacts
from recommender.models import Destination
from recommender.spk import topsis

build = Path(__file__).resolve().parent
snapshot = json.loads((build / 'snapshot.json').read_text(encoding='utf-8'))
evidence = json.loads((ROOT / 'outputs/uts_travelfit/_build/evidence.json').read_text(encoding='utf-8'))
sources = validate_artifacts(ROOT)
assert len(sources.destinations) == 443
assert set(sources.destinations.place_id) == set(range(1, 444))
actual = list(Destination.objects.order_by('source_id'))
assert len(actual) == 443
for item, old in zip(actual, sorted(snapshot['master'], key=lambda r: r['source_id'])):
    row = dict(item.__dict__)
    row.pop('_state')
    assert all(row[k] == old[k] for k in row), item.source_id
    assert item.facility_score() == old['facility_score']
    assert item.calculation_rating() == old['calculation_rating']

for path, expected in evidence['protected_hashes'].items():
    if path == 'db.sqlite3':
        continue  # Browser checks legitimately update sessions; rows checked above.
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
for path in ['notebooks/01_preprocessing_travelfit.ipynb',
             'notebooks/02_preprocessing_lengkap_cleaning.ipynb',
             'notebooks/03_preprocessing_simple.ipynb']:
    old = json.loads(subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT))
    current = json.loads((ROOT / path).read_text(encoding='utf-8'))
    code = lambda nb: [c['source'] for c in nb['cells'] if c['cell_type'] == 'code']
    assert code(old) == code(current), path

captured, calls = {}, []
original_rank = topsis.rank
def rank(matrix, weights, costs):
    result = original_rank(matrix, weights, costs)
    calls.append((matrix, result))
    return result
def response(request, context, count):
    captured.update(context)
    return HttpResponse('verified')
req = RequestFactory().post('/', {'budget': '10000', 'kota_asal': 'Serang',
    'wilayah': 'Banten', 'kategori_utama': 'alam', 'kategori_sekunder': 'budaya',
    'hobi': [], 'profil': 'hemat', 'sentuh_bobot': ''},
    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
req.session = {}
with patch.object(topsis, 'rank', side_effect=rank), patch.object(views, '_ajax_results', side_effect=response):
    views.rekomendasi(req)
assert captured['ringkasan']['n'] == 2
assert calls[0][0] == evidence['decision']
for report_row, web_row in zip(evidence['rank'], calls[0][1]):
    assert report_row['idx'] == web_row['idx']
    assert abs(report_row['vi'] - web_row['vi']) < 1e-12
    assert set(report_row) == set(web_row)
    for key in ('vi', 'd_pos', 'd_neg'):
        assert abs(report_row[key] - web_row[key]) < 1e-12, key
    for key in ('gap', 'span'):
        assert all(abs(a-b) < 1e-12 for a,b in zip(report_row[key], web_row[key])), key
print(json.dumps({'destination_rows_unchanged': 443,
    'source_and_archive_hashes_unchanged': True, 'notebook_code_unchanged': True,
    'report_matrix_equal_web_and_ranking_within_1e_minus12': True,
    'report_winner': captured['hasil'][0]['nama'], 'report_vi': captured['hasil'][0]['vi']}, ensure_ascii=False))
