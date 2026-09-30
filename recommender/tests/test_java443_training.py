import io
import json
from pathlib import Path
import tempfile
from django.core.management import call_command, CommandError
from django.test import TestCase
from recommender.data_pipeline import build_pipeline, build_features, export_pipeline
from recommender.models import Destination
from recommender.tests.test_data_pipeline import copy_sources


class Java443TrainingTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        copy_sources(cls.root)
        cls.result = build_pipeline(cls.root)
        export_pipeline(cls.result, cls.root)
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        call_command('import_destinations', project_root=str(cls.root), stdout=io.StringIO())

    def train(self, **options):
        try:
            call_command('train_clusters', project_root=str(self.root), stdout=io.StringIO(), **options)
        except (CommandError, TypeError) as error:
            self.fail(str(error))

    def test_report_and_labels_include_all_443(self):
        self.train()
        report = json.loads((self.root / 'reports/clustering/kmeans_evaluation.json').read_text(encoding='utf-8'))
        self.assertEqual(report['training_rows'], 443)
        self.assertEqual(report['assigned_rows'], 443)
        self.assertEqual(report['assigned_simulation_rows'], 0)
        self.assertEqual(report['rating_imputation']['imputed_ids'], [438])
        self.assertEqual(report['features'], self.result.manifest['feature_parameters']['feature_columns'])
        self.assertEqual(sum(c['all_rows'] for c in report['clusters']), 443)
        self.assertEqual(Destination.objects.exclude(cluster_label='').count(), 443)

    def test_dry_run_does_not_change_labels_or_report(self):
        Destination.objects.update(cluster_label='unchanged')
        path = self.root / 'reports/clustering/kmeans_evaluation.json'
        old = path.read_bytes() if path.exists() else None
        self.train(dry_run=True)
        self.assertEqual(Destination.objects.filter(cluster_label='unchanged').count(), 443)
        self.assertEqual(path.read_bytes() if path.exists() else None, old)

    def test_missing_extra_or_stale_database_rejected(self):
        for mutation in ('missing', 'extra', 'stale'):
            with self.subTest(mutation=mutation):
                call_command('import_destinations', project_root=str(self.root), stdout=io.StringIO())
                if mutation == 'missing':
                    Destination.objects.get(source_id=443).delete()
                elif mutation == 'extra':
                    Destination.objects.create(nama='Extra', kota='X', provinsi='Banten', kategori='alam', harga_tiket=0, rating=4)
                else:
                    Destination.objects.filter(source_id=1).update(rating_model=1.0)
                with self.assertRaises(CommandError):
                    call_command('train_clusters', project_root=str(self.root), dry_run=True, stdout=io.StringIO())

    def test_c4_does_not_enter_feature_distance(self):
        changed = self.result.destinations.copy()
        changed['c4_facility_score'] = 1
        frame, _ = build_features(changed)
        import pandas as pd
        pd.testing.assert_frame_equal(frame, self.result.features)
