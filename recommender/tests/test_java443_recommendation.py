from unittest.mock import patch
from django.test import TestCase
from recommender.models import Destination
from recommender.tests.test_views import _mock_rencanakan


class Java443RecommendationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Destination.objects.create(source_id=438, nama='Taman Hutan Raya Banten', kota='Pandeglang', provinsi='Banten',
            kategori='alam', harga_tiket=8000, rating=None, rating_model=4.5, rating_imputed=True,
            latitude=-6.2926599, longitude=105.8412076, sumber_data='curated_java', pipeline_fingerprint='test-snapshot',
            data_quality={'rating_model_note':'Imputasi median'}, provenance={'rating_source_url':''})
        Destination.objects.create(source_id=439, nama='Museum Multatuli', kota='Lebak', provinsi='Banten',
            kategori='budaya', harga_tiket=2000, rating=4.6, rating_model=4.6,
            latitude=-6.3605, longitude=106.2472, sumber_data='curated_java', pipeline_fingerprint='test-snapshot')
        Destination.objects.create(source_id=9, nama='Pelabuhan Marina', kota='Jakarta', provinsi='DKI Jakarta',
            kategori='bahari', harga_tiket=0, rating=4.4, rating_model=4.4,
            latitude=1.07888, longitude=103.931398, sumber_data='kaggle_java', pipeline_fingerprint='test-snapshot',
            data_quality={'coordinate_review_required':True,'coordinate_review_note':'Koordinat perlu review'})

    def post(self, **changes):
        data = {'budget':'20000000','kota_asal':'Jakarta','wilayah':'Banten',
                'kategori_utama':'alam','kategori_sekunder':'budaya','profil':'seimbang',
                'moda':'mobil','hari':'1','mode_antar':'termurah'}
        data.update(changes)
        with patch('recommender.views.rencanakan',side_effect=_mock_rencanakan), patch('recommender.views.jarak_table',return_value=[]):
            return self.client.post('/',data,follow=True)

    def test_tahura_model_rating_and_provenance_retained(self):
        response = self.post()
        row = next(h for h in response.context['hasil'] if h['nama']=='Taman Hutan Raya Banten')
        self.assertIsNone(row['rating'])
        self.assertEqual(row['rating_model'],4.5)
        self.assertTrue(row['rating_imputed'])
        self.assertEqual(Destination.objects.get(source_id=438).rating_model,4.5)

    def test_marina_not_lost_and_warning_in_context(self):
        response = self.post(wilayah='DKI Jakarta')
        row = response.context['hasil'][0]
        self.assertEqual(row['source_id'],9)
        self.assertIn('Koordinat perlu review', row['quality_notes'])

    def test_stale_session_cleared_for_get_and_map(self):
        for url in ('/','/peta/'):
            session=self.client.session
            session['dataset_fingerprint']='old2337'
            session['flash_hasil']={'hasil':[{'nama':'OLD RESULT'}]}
            session['hasil_terakhir']=[{'nama':'OLD RESULT'}]
            session.save()
            response=self.client.get(url)
            self.assertNotContains(response,'OLD RESULT')

    def test_zero_budget_and_invalid_ajax(self):
        response=self.post(budget='0')
        self.assertTrue(response.context['kandidat_kosong'])
        response=self.client.post('/',{'budget':'invalid'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,400)
