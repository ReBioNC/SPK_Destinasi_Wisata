import io
import json
import subprocess
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.core.management import call_command
from django.test import Client, TestCase
from recommender.models import Destination
from recommender.tests.test_data_pipeline import copy_sources

ROOT=Path(__file__).resolve().parents[2]


class Java443WorkflowTests(TestCase):
    def test_protected_text_checkout_preserves_original_line_endings(self):
        hashes=json.loads((ROOT/'recommender/tests/fixtures/java443_protected_hashes.json').read_text())
        for name in hashes:
            if Path(name).suffix not in ('.csv','.json','.md','.py'):
                continue
            data=(ROOT/name).read_bytes()
            if b'\n' not in data:
                continue
            expected='crlf' if b'\r\n' in data else 'lf'
            policy=subprocess.check_output(['git','check-attr','eol','--',name],cwd=ROOT,text=True).strip()
            if name=='data/raw/tourism_with_id.csv':
                continue  # Binary/-text snapshot is already byte-preserving.
            self.assertTrue(policy.endswith(': '+expected),policy)

    def test_preprocess_import_train_then_recommend_and_map(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            copy_sources(root)
            call_command('preprocess_destinations', project_root=str(root), stdout=io.StringIO())
            call_command('import_destinations', project_root=str(root), stdout=io.StringIO())
            call_command('train_clusters', project_root=str(root), stdout=io.StringIO())
            self.assertEqual(list(Destination.objects.order_by('source_id').values_list('source_id',flat=True)),list(range(1,444)))
            self.assertEqual(Destination.objects.exclude(cluster_label='').count(),443)
            response=self.client.post('/',{'budget':'20000000','kota_asal':'Jakarta','wilayah':'Banten',
                'kategori_utama':'alam','kategori_sekunder':'budaya','profil':'seimbang',
                'hari':1,'moda':'mobil','mode_antar':'termurah'},follow=True)
            self.assertTrue(response.context['hasil'])
            self.assertTrue(any(h['rating_imputed'] for h in response.context['hasil']))
            self.assertEqual(len(self.client.get('/peta/').context['map_destinations']),443)
            report=json.loads((root/'reports/clustering/kmeans_evaluation.json').read_text())
            manifest=json.loads((root/'reports/preprocessing/preprocessing_java443_manifest.json').read_text())
            self.assertEqual(report['pipeline_fingerprint'],manifest['pipeline_fingerprint'])

    def test_no_active_legacy_data_references(self):
        active=[ROOT/'recommender/management/commands/import_destinations.py',
                ROOT/'recommender/management/commands/train_clusters.py',
                ROOT/'notebooks/01_preprocessing_travelfit.ipynb']
        active+=list((ROOT/'recommender/templates/recommender').glob('*.html'))
        for path in active:
            content=path.read_text(encoding='utf-8')
            for retired in ('Dataset_Wisata_Gabungan_2337.xlsx','destinations_full_clean.csv',
                            'destinations_clean.csv','nusantara.js','cdn.tailwindcss.com'):
                self.assertNotIn(retired,content,str(path))
        self.assertFalse((ROOT/'notebooks/02_preprocessing_travelfit_full.ipynb').exists())
        self.assertTrue((ROOT/'archive/legacy/notebooks/02_preprocessing_travelfit_full.ipynb').exists())

    def test_sources_evidence_and_docx_unchanged(self):
        hashes=json.loads((ROOT/'recommender/tests/fixtures/java443_protected_hashes.json').read_text())
        for name,digest in hashes.items():
            self.assertEqual(sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_setup_documented_and_csrf_enforced(self):
        self.assertTrue((ROOT/'Dokumentasi.md').exists())
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('preprocess_destinations',readme)
        self.assertIn('train_clusters',readme)
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/',{'budget':'20000000'}).status_code,403)

    def test_notebook_has_unique_cell_ids(self):
        notebook=json.loads((ROOT/'notebooks/01_preprocessing_travelfit.ipynb').read_text())
        ids=[cell.get('id') for cell in notebook['cells']]
        self.assertTrue(all(ids))
        self.assertEqual(len(ids),len(set(ids)))

    def test_export_json_uses_portable_lf_bytes(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            copy_sources(root)
            call_command('preprocess_destinations',project_root=str(root),stdout=io.StringIO())
            for name in ('summary','manifest'):
                self.assertNotIn(b'\r\n',(root/f'reports/preprocessing/preprocessing_java443_{name}.json').read_bytes())
