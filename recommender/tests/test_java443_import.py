import io
from pathlib import Path
import tempfile
from unittest.mock import patch
from django.core.management import call_command, CommandError
from django.test import TestCase
from recommender.data_pipeline import build_pipeline, export_pipeline
from recommender.models import Destination
from recommender.tests.test_data_pipeline import ROOT, copy_sources


class Java443ImportTests(TestCase):
    def import_data(self, **options):
        call_command('import_destinations', stdout=io.StringIO(), **options)

    def test_exact_443_and_idempotence(self):
        self.import_data()
        self.assertEqual(Destination.objects.count(), 443)
        self.import_data()
        self.assertEqual(set(Destination.objects.values_list('source_id', flat=True)), set(range(1,444)))
        self.assertEqual(Destination.objects.filter(sumber_data='kaggle_java').count(), 437)
        self.assertEqual(Destination.objects.filter(sumber_data='curated_java').count(), 6)

    def test_tahura_raw_null_model_median(self):
        self.import_data()
        row = Destination.objects.get(nama='Taman Hutan Raya Banten')
        self.assertIsNone(row.rating)
        self.assertEqual(row.calculation_rating(), 4.5)
        self.assertTrue(row.rating_imputed)
        self.assertEqual(row.provenance['rating_source_url'], '')

    def test_facility_six_groups_matches_master(self):
        self.import_data()
        domes = Destination.objects.get(source_id=145)
        self.assertAlmostEqual(domes.facility_score(), 4/6)
        self.assertTrue(Destination.objects.get(source_id=394).fas_accessibility)
        self.assertEqual(Destination.objects.get(source_id=441).facility_score(), 0)

    def test_import_dry_run_leaves_database_unchanged(self):
        old = Destination.objects.create(nama='Legacy', kota='X', provinsi='Bali', kategori='alam', harga_tiket=0, rating=4)
        self.import_data(dry_run=True)
        self.assertEqual(list(Destination.objects.values_list('pk',flat=True)), [old.pk])

    def test_import_rolls_back_on_mid_transaction_error(self):
        old = Destination.objects.create(nama='Legacy', kota='X', provinsi='Bali', kategori='alam', harga_tiket=0, rating=4)
        original = Destination.save
        def fail_second(instance, *args, **kwargs):
            if getattr(instance, 'source_id', None) == 2:
                raise RuntimeError('controlled write failure')
            return original(instance, *args, **kwargs)
        with patch.object(Destination, 'save', fail_second), self.assertRaisesRegex(RuntimeError, 'controlled'):
            self.import_data()
        self.assertEqual(list(Destination.objects.values_list('pk',flat=True)), [old.pk])

    def test_stale_artifacts_rejected_before_delete(self):
        old = Destination.objects.create(nama='Legacy', kota='X', provinsi='Bali', kategori='alam', harga_tiket=0, rating=4)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root)
            paths = export_pipeline(build_pipeline(root), root)
            with paths['features'].open('a') as stream:
                stream.write('\n')
            with self.assertRaises(CommandError):
                self.import_data(project_root=str(root))
        self.assertTrue(Destination.objects.filter(pk=old.pk).exists())

    def test_existing_natural_keys_rebound_without_duplicates(self):
        old = Destination.objects.create(nama='Monumen Nasional', kota='Jakarta', provinsi='DKI Jakarta', kategori='budaya', harga_tiket=0, rating=4)
        self.import_data()
        actual = Destination.objects.get(source_id=1)
        self.assertEqual(actual.pk, old.pk)
        self.assertEqual(actual.rating, 4.6)
        self.assertEqual(Destination.objects.count(), 443)

    def test_marina_retained_and_legacy_removed(self):
        Destination.objects.create(nama='Legacy', kota='X', provinsi='Bali', kategori='alam', harga_tiket=0, rating=4)
        self.import_data()
        self.assertFalse(Destination.objects.filter(nama='Legacy').exists())
        row = Destination.objects.get(source_id=9)
        self.assertAlmostEqual(row.latitude, 1.07888)
        self.assertTrue(row.data_quality['coordinate_review_required'])
