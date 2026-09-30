import io
from unittest.mock import patch
from django.core.management import call_command
from django.test import TestCase
from recommender.tests.test_views import _mock_rencanakan


class JavaUITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_destinations', stdout=io.StringIO())

    def test_home_has_native_form_and_source_counts(self):
        response=self.client.get('/')
        self.assertEqual(response.context['data_count'],443)
        self.assertTemplateUsed(response,'recommender/base.html')
        self.assertContains(response,'Lewati ke konten')
        self.assertContains(response,'443')
        self.assertContains(response,'travelfit.css')
        self.assertNotContains(response,'cdn.tailwindcss.com')
        self.assertNotContains(response,'2337')
        self.assertContains(response,'id="form-status"')

    def test_invalid_form_errors_and_ajax_summary(self):
        response=self.client.post('/',{'budget':'gratis'})
        self.assertContains(response,'id="form-errors"')
        self.assertContains(response,'href="#id_budget"')
        response=self.client.post('/',{'budget':'gratis'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code,400)
        self.assertTrue('budget' in response.json().get('errors',{}))

    def test_tahura_imputation_visible_without_expansion(self):
        data={'budget':'20000000','kota_asal':'Jakarta','wilayah':'Banten',
              'kategori_utama':'alam','kategori_sekunder':'budaya','profil':'seimbang',
              'hari':1,'moda':'mobil','mode_antar':'termurah'}
        with patch('recommender.views.rencanakan',side_effect=_mock_rencanakan),patch('recommender.views.jarak_table',return_value=[]):
            response=self.client.post('/',data,follow=True)
        self.assertContains(response,'Rating diimputasi')
        self.assertContains(response,'Kurasi Jawa')
        self.assertContains(response,'Estimasi total')
        self.assertNotContains(response,'★ None')

    def test_method_page_covers_crispdm_and_limits(self):
        response=self.client.get('/tentang/')
        for title in ('Business Understanding','Data Understanding','Data Preparation','Modeling','Evaluation','Deployment'):
            self.assertContains(response,title)
        self.assertContains(response,'belum hasil survei')
        self.assertContains(response,'bukan akurasi')
