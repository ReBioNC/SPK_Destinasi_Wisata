"""Exercise the notebook to catch dropped destinations and unsafe rating transfer."""

import json
from pathlib import Path
import re
import unittest

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def run_cells(start, stop, scope):
    notebook = json.loads((ROOT / 'notebooks/01_preprocessing_travelfit.ipynb').read_text(encoding='utf-8'))
    for cell in notebook['cells'][start:stop]:
        if cell['cell_type'] == 'code':
            exec(compile(''.join(cell['source']), 'preprocessing_notebook', 'exec'), scope)
    return scope


class PreprocessingRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = run_cells(2, 8, {
            'json': json, 're': re, 'pd': pd, 'np': np,
            'PROJECT_ROOT': ROOT, 'RAW_DIR': ROOT / 'data/raw',
        })

    def test_all_443_source_ids_survive_preprocessing(self):
        actual = self.scope['destinations']
        self.assertEqual(len(actual), 443)
        self.assertEqual(set(actual.place_id), set(range(1, 444)))
        self.assertTrue(actual.place_id.is_unique)

    def test_feature_matrix_retains_the_same_443_destinations(self):
        self.assertEqual(set(self.scope['kmeans_ready'].place_id), set(range(1, 444)))
        self.assertEqual(len(self.scope['kmeans_ready']), 443)

    def test_ambiguous_tahura_rating_stays_missing_without_losing_the_row(self):
        actual = self.scope['destinations'].set_index('place_id')
        self.assertIn(438, actual.index)
        if 438 in actual.index:
            self.assertTrue(pd.isna(actual.loc[438, 'rating']))
            self.assertEqual(actual.loc[438, 'rating_status'], 'pending_identity')

    def test_only_matched_additional_ratings_are_transferred(self):
        actual = self.scope['destinations'].set_index('place_id')
        for place_id, rating in [(439, 4.6), (440, 4.6), (441, 4.5), (442, 4.2), (443, 4.3)]:
            with self.subTest(place_id=place_id):
                self.assertIn(place_id, actual.index)
                if place_id in actual.index:
                    self.assertEqual(actual.loc[place_id, 'rating'], rating)
                    self.assertTrue(actual.loc[place_id, 'rating_source_url'].startswith('https://www.google.com/maps/place/'))

    def test_invalid_measurement_is_flagged_instead_of_dropping_destination(self):
        raw = pd.read_csv(ROOT / 'data/raw/tourism_with_id.csv').head(2)
        raw.loc[0, 'Rating'] = 9
        raw.loc[1, 'Price'] = -1
        scope = run_cells(3, 4, {
            're': re, 'pd': pd, 'np': np, 'destinations': raw,
            'ratings': pd.read_csv(ROOT / 'data/raw/tourism_rating.csv'),
        })
        actual = scope['destinations']
        self.assertEqual(set(actual.place_id), {1, 2})
        if len(actual) == 2:
            self.assertTrue(actual.data_quality_issues.str.contains('rating_out_of_range').any())
            self.assertTrue(actual.data_quality_issues.str.contains('price_invalid').any())


if __name__ == '__main__':
    unittest.main()
