"""Exercise the notebook to catch dropped destinations and unsafe rating transfer."""

import json
from pathlib import Path
import re
import unittest

import numpy as np
import pandas as pd
from recommender.data_pipeline import build_pipeline, normalize_destinations, add_model_rating


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
        result = build_pipeline(ROOT)
        cls.scope = {'destinations': result.destinations, 'kmeans_ready': result.features}

    def test_all_443_source_ids_survive_preprocessing(self):
        actual = self.scope['destinations']
        self.assertEqual(len(actual), 466)
        self.assertEqual(set(actual.place_id), set(range(1, 467)))
        self.assertTrue(actual.place_id.is_unique)

    def test_feature_matrix_retains_the_same_443_destinations(self):
        self.assertEqual(set(self.scope['kmeans_ready'].place_id), set(range(1, 467)))
        self.assertEqual(len(self.scope['kmeans_ready']), 466)

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

    def test_unmatched_november_ratings_stay_missing_and_use_median(self):
        actual = self.scope['destinations'].set_index('place_id')
        for place_id in (444, 446, 447, 451, 459, 462, 463):
            with self.subTest(place_id=place_id):
                self.assertTrue(pd.isna(actual.loc[place_id, 'rating']))
                self.assertEqual(actual.loc[place_id, 'rating_status'], 'pending_identity')
                self.assertEqual(actual.loc[place_id, 'c2_rating_for_model'], 4.5)
        self.assertEqual(actual.loc[445, 'rating_status'], 'google_maps_matched')
        self.assertFalse(actual.loc[445, 'rating_imputed'])

    def test_tahura_uses_median_only_in_calculation_column(self):
        row = self.scope['destinations'].set_index('place_id').loc[438]
        self.assertEqual(row.get('c2_rating_for_model'), 4.5)
        self.assertTrue(row.get('rating_imputed', False))
        self.assertTrue(pd.isna(row['rating']))
        self.assertTrue(pd.isna(row['c2_rating']))

    def test_all_443_numeric_feature_rows_are_finite_after_authorized_imputation(self):
        features = self.scope['kmeans_ready']
        values = features.drop(columns='place_id').to_numpy()
        self.assertTrue(np.isfinite(values).all())
        self.assertEqual(len(values), 466)

    def test_observed_ratings_are_not_replaced_with_median(self):
        actual = self.scope['destinations']
        self.assertIn('c2_rating_for_model', actual.columns)
        if 'c2_rating_for_model' in actual.columns:
            known = actual['rating'].notna()
            pd.testing.assert_series_equal(actual.loc[known, 'rating'], actual.loc[known, 'c2_rating_for_model'], check_names=False)
            self.assertEqual(set(actual.loc[actual.rating_imputed, 'place_id']), set([438, 444, 446, 447, 451, 459, 462, 463]))

    def test_marina_remains_with_original_coordinates_and_review_flag(self):
        row = self.scope['destinations'].set_index('place_id').loc[9]
        self.assertTrue(row.get('coordinate_review_required', False))
        self.assertEqual(row['place_name'], 'Pelabuhan Marina')
        self.assertAlmostEqual(row['lat'], 1.07888)
        self.assertAlmostEqual(row['long'], 103.931398)

    def test_kto_sari_alam_keeps_source_coordinates_with_review_flag(self):
        actual = self.scope['destinations'].set_index('place_id')
        row = actual.loc[323]
        self.assertEqual(row['place_name'], 'Kebun Tanaman Obat Sari Alam')
        self.assertTrue(row['coordinate_review_required'])
        self.assertIn('Ciwidey', row['coordinate_review_note'])
        self.assertAlmostEqual(row['lat'], -6.601321)
        self.assertAlmostEqual(row['long'], 106.632734)
        self.assertEqual(set(actual.index[actual.coordinate_review_required.astype(bool)]), {9, 323})

    def test_imputation_median_is_calculated_not_hardcoded(self):
        raw = pd.read_csv(ROOT / 'data/raw/tourism_with_id.csv').head(4).copy()
        raw['Place_Id'] = [438, 1, 2, 3]
        raw.loc[0, 'Place_Name'] = 'Taman Hutan Raya Banten'
        raw['Rating'] = [np.nan, 4.1, 4.2, 4.9]
        actual, _ = add_model_rating(normalize_destinations(raw))
        row = actual.set_index('place_id').loc[438]
        self.assertEqual(row.get('c2_rating_for_model'), 4.2)

    def test_invalid_measurement_is_flagged_instead_of_dropping_destination(self):
        raw = pd.read_csv(ROOT / 'data/raw/tourism_with_id.csv').head(2)
        raw.loc[0, 'Rating'] = 9
        raw.loc[1, 'Price'] = -1
        actual = normalize_destinations(raw)
        self.assertEqual(set(actual.place_id), {1, 2})
        if len(actual) == 2:
            self.assertTrue(actual.data_quality_issues.str.contains('rating_out_of_range').any())
            self.assertTrue(actual.data_quality_issues.str.contains('price_invalid').any())


if __name__ == '__main__':
    unittest.main()
