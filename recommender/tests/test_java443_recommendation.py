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

    def post(self, ajax=False, **changes):
        data = {'budget':'20000000','kota_asal':'Jakarta','wilayah':'Banten',
                'kategori_utama':'alam','kategori_sekunder':'budaya','profil':'seimbang',
                'moda':'mobil','hari':'1','mode_antar':'termurah'}
        data.update(changes)
        with patch('recommender.views.rencanakan',side_effect=_mock_rencanakan), patch('recommender.views.jarak_table',return_value=[]):
            return self.client.post('/',data,follow=True,**({'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'} if ajax else {}))

    def test_redirect_preserves_preferences_and_raw_custom_weights(self):
        Destination.objects.filter(source_id=438).update(tag_aktivitas='hiking|fotografi')
        response=self.post(kota_asal='Serang',profil='hemat',hobi=['hiking'],sentuh_bobot='1',
                           w1='42',w2='15',w3='14',w4='12',w5='8',w6='9',hari='2',moda='motor')
        form=response.context['form']
        for name,value in {'budget':'20000000','kota_asal':'Serang','profil':'hemat',
                           'hobi':['hiking'],'hari':'2','moda':'motor','sentuh_bobot':'1'}.items():
            self.assertEqual(form[name].value(),value,name)
        self.assertEqual([float(s['value']) for s in response.context['slider_fields']],[42,15,14,12,8,9])
        self.assertContains(response,'id="sentuh_bobot" value="1"')

    def test_validation_error_retains_custom_slider_values(self):
        response=self.post(budget='invalid',profil='hemat',sentuh_bobot='1',
                           w1='42',w2='15',w3='14',w4='12',w5='8',w6='9')
        self.assertEqual([float(s['value']) for s in response.context['slider_fields']],[42,15,14,12,8,9])
        self.assertContains(response,'id="sentuh_bobot" value="1"')

    def test_ajax_returns_current_map_recommendations_fragment(self):
        response=self.post(ajax=True)
        self.assertEqual(response.status_code,200)
        fragment=response.json().get('map_html','')
        self.assertIn('Taman Hutan Raya Banten',fragment)
        self.assertIn('id="hasil-data"',fragment)
        self.assertNotIn('svg',fragment)  # Do not resend all443 destination rows.

    def test_empty_search_clears_prior_map_results_in_both_filters(self):
        for budget in ('0','10000'):
            for ajax in (False,True):
                with self.subTest(budget=budget,ajax=ajax):
                    self.post()
                    self.assertTrue(self.client.session['hasil_terakhir'])
                    response=self.post(ajax=ajax,budget=budget)
                    self.assertEqual(self.client.session.get('hasil_terakhir'),[])
                    self.assertEqual(self.client.get('/peta/').context['hasil_json'],[])
                    if ajax:
                        self.assertIn('map_html',response.json())
                        self.assertNotIn('Taman Hutan Raya Banten',response.json()['map_html'])

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
