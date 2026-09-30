"""Shared transformations must preserve identity and reject stale artifacts."""
import importlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ['data/raw/tourism_with_id.csv', 'data/raw/tourism_rating.csv',
           'data/review/gabungan_jawa/destinasi_jawa_review.csv',
           'data/review/gabungan_jawa/google_maps_rating_review.json']


def copy_sources(root):
    for relative in SOURCES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, path)


class DataPipelineTests(unittest.TestCase):
    def setUp(self):
        try:
            self.pipeline = importlib.import_module('recommender.data_pipeline')
        except ModuleNotFoundError:
            self.pipeline = None
        self.assertIsNotNone(self.pipeline, 'Shared Java443 pipeline is not implemented')

    def test_exact_source_ids_retained(self):
        result = self.pipeline.build_pipeline(ROOT)
        self.assertEqual(len(result.destinations), 443)
        self.assertEqual(set(result.destinations.place_id), set(range(1, 444)))
        self.assertTrue(result.destinations.place_id.is_unique)

    def test_model_features_exclude_c4(self):
        result = self.pipeline.build_pipeline(ROOT)
        columns = result.manifest['feature_parameters']['feature_columns']
        self.assertEqual(len(result.features), 443)
        self.assertEqual(columns[:2], ['c1_ticket_price_z', 'c2_rating_z'])
        self.assertTrue(all(c.startswith('category_') for c in columns[2:]))
        self.assertTrue(np.isfinite(result.features[columns].to_numpy()).all())
        self.assertEqual(result.destinations.set_index('place_id').loc[3, 'price'], 270000)

    def test_imputation_identity_guard(self):
        frame = pd.DataFrame({'place_id': [438, 1, 2, 3], 'place_name': ['Other', 'a', 'b', 'c'],
                              'rating': [np.nan, 4.1, 4.2, 4.9]})
        actual, _ = self.pipeline.add_model_rating(frame)
        self.assertFalse(actual.loc[0, 'rating_imputed'])
        self.assertTrue(pd.isna(actual.loc[0, 'c2_rating_for_model']))
        frame.loc[0, 'place_name'] = 'Taman Hutan Raya Banten'
        actual, metadata = self.pipeline.add_model_rating(frame)
        self.assertEqual(actual.loc[0, 'c2_rating_for_model'], 4.2)
        self.assertTrue(pd.isna(actual.loc[0, 'rating']))
        self.assertEqual(metadata['observed_rows'], 3)

    def test_unexpected_missing_rating_blocks_features(self):
        frame = self.pipeline.build_pipeline(ROOT).destinations.copy()
        frame.loc[frame.place_id.eq(1), 'c2_rating_for_model'] = np.nan
        with self.assertRaisesRegex(ValueError, '(?i)fitur|feature'):
            self.pipeline.build_features(frame)
        self.assertEqual(len(frame), 443)

    def test_constant_numeric_scale_is_one(self):
        frame = pd.DataFrame({'place_id': [1,2], 'c1_ticket_price': [0,0],
                              'c2_rating_for_model': [4,4], 'category_clean': ['alam','alam']})
        features, params = self.pipeline.build_features(frame)
        self.assertEqual(params['scale'], [1.0, 1.0])
        self.assertEqual(features.c1_ticket_price_z.tolist(), [0,0])

    def test_missing_source_fails_clearly(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(FileNotFoundError, 'tourism_with_id.csv'):
                self.pipeline.build_pipeline(Path(temporary))

    def test_duplicate_or_missing_id_blocks_export(self):
        result = self.pipeline.build_pipeline(ROOT)
        result.destinations.loc[0, 'place_id'] = 2
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                self.pipeline.export_pipeline(result, Path(temporary))
            self.assertFalse((Path(temporary) / 'data/processed').exists())

    def test_modified_output_or_source_rejected(self):
        for target in ('data/processed/destinations_clean_java443.csv', SOURCES[0]):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                copy_sources(root)
                result = self.pipeline.build_pipeline(root)
                self.pipeline.export_pipeline(result, root)
                self.assertEqual(self.pipeline.validate_artifacts(root).manifest['pipeline_fingerprint'],
                                 result.manifest['pipeline_fingerprint'])
                with (root / target).open('a', encoding='utf-8') as stream:
                    stream.write('\n')
                with self.assertRaisesRegex(ValueError, 'hash|berubah'):
                    self.pipeline.validate_artifacts(root)

    def test_stale_version_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root)
            paths = self.pipeline.export_pipeline(self.pipeline.build_pipeline(root), root)
            manifest = json.loads(paths['manifest'].read_text(encoding='utf-8'))
            manifest['pipeline_version'] = 'legacy'
            paths['manifest'].write_text(json.dumps(manifest), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '(?i)versi|version'):
                self.pipeline.validate_artifacts(root)
