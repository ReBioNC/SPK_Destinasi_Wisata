import os, sys, json, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.test import RequestFactory
from django.http import HttpResponse
from recommender import views
from recommender.models import Destination
from recommender.spk import profiles, topsis, geo
from recommender.kota_asal import KOTA_ASAL

OUT = Path(__file__).parent
protected = [ROOT/'db.sqlite3', ROOT/'Perhitungan_SPK_TravelFit.xlsx', ROOT/'Laporan_SPK_TravelFit.docx']
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.exists()}
data = list(Destination.objects.all())
calls = []
actual_rank = topsis.rank
def rank(matrix, weights, costs):
    result = actual_rank(matrix, weights, costs)
    calls.append({'matrix': matrix, 'weights': weights, 'rank': result})
    return result

captured = {}
def response(request, context, count):
    captured.update(context)
    return HttpResponse('captured')

settings = dict(budget='1000000', kota_asal='Bandung', wilayah='Jawa Barat', kategori_utama='alam', kategori_sekunder='budaya', hobi=['fotografi','edukasi'], profil='hemat', sentuh_bobot='')
def invoke(inputs, refresh=True):
    calls.clear()
    captured.clear()
    req = RequestFactory().post('/', inputs, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    req.session = {}
    patches = [patch.object(topsis, 'rank', side_effect=rank), patch.object(views, '_ajax_results', side_effect=response)]
    import contextlib
    with contextlib.ExitStack() as stack:
        for p in patches: stack.enter_context(p)
        views.rekomendasi(req)
    if captured.get('form') and captured['form'].errors:
        raise RuntimeError(str(captured['form'].errors))
    return {'inputs': inputs, 'results': captured.get('hasil') or [], 'candidate_count': (captured.get('ringkasan') or {}).get('n', 0), 'calculation': calls[-1] if calls else None}

baseline = invoke(settings)
origin = KOTA_ASAL[settings['kota_asal']]
master = []
for d in data:
    row = dict(d.__dict__)
    row.pop('_state',None)
    row['facility_score'] = d.facility_score()
    row['calculation_rating'] = d.calculation_rating()
    row['great_circle_km'] = geo.haversine(*origin,d.latitude,d.longitude)
    master.append(row)
assert len(master)==443
selected = [r for r in master if r['provinsi']==settings['wilayah']]
assert len(selected) == 124
tests = [baseline]
for profile in profiles.ACTIVE_PROFILES:
    if profile != 'hemat': tests.append(invoke(dict(settings,profil=profile),False))
tests.append(invoke(dict(settings,budget='25000'),False))
tests.append(invoke(dict(settings,budget='0'),False))
tests.append(invoke(dict(settings,hobi=[], kategori_utama='belanja', kategori_sekunder='religi'),False))
matrices = {k: profiles.matrix_from_upper(v) for k,v in profiles.PROFILE_UPPERS.items()}
payload = dict(timestamp=datetime.now(timezone.utc).isoformat(), origin=list(origin), baseline=baseline, tests=tests, master=master, matrices=matrices, profiles=profiles.ACTIVE_PROFILES, budget_basis='ticket', distance_basis='haversine', git_head=os.popen('git rev-parse HEAD').read().strip(), protected_hashes=hashes)
(OUT/'snapshot.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
for p,h in hashes.items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h, p
print(json.dumps({'master':len(master),'province':len(selected),'eligible':baseline['candidate_count'],'winner':baseline['results'][0]['nama'],'vi':baseline['results'][0]['vi'],'tests':len(tests),'protected_unchanged':True},ensure_ascii=False))
