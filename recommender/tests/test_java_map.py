import io
import json
import re
from django.core.management import call_command
from django.test import TestCase
from recommender.models import Destination

PROVINCES = {'Banten','DKI Jakarta','Jawa Barat','Jawa Tengah',
             'Daerah Istimewa Yogyakarta','Jawa Timur'}


class JavaMapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('import_destinations', stdout=io.StringIO())

    def test_shared_map_exact_six_provinces_on_both_pages(self):
        for url in ('/','/peta/'):
            response=self.client.get(url)
            self.assertTemplateUsed(response,'recommender/_java_map.html')
            self.assertEqual(set(re.findall(r'data-province="([^"]+)"',response.content.decode())), PROVINCES)
            self.assertContains(response,'viewBox="220 287 242 97"')
            self.assertNotContains(response,'prov-aceh')

    def test_counts_and_province_links_prefill_form(self):
        response=self.client.get('/peta/')
        self.assertEqual(sum(p['count'] for p in response.context['map_provinces']),443)
        for province in PROVINCES:
            response=self.client.get('/',{'wilayah':province})
            self.assertEqual(response.context['form']['wilayah'].value(),province)
            self.assertContains(response,'terisi dari peta')

    def test_marina_retained_outside_frame_and_monas_inside(self):
        response=self.client.get('/peta/')
        self.assertEqual(len(response.context['map_destinations']),443)
        marina=next(d for d in response.context['map_destinations'] if d['source_id']==9)
        monas=next(d for d in response.context['map_destinations'] if d['source_id']==1)
        self.assertTrue(marina['outside_frame'])
        self.assertTrue(marina['quality_notes'])
        self.assertFalse(monas['outside_frame'])
        # Actual inherited Jakarta polygon, tested with ray casting rather than
        # treating a point inside the viewBox as proof it is inside the province.
        vertices=[(258.2,305.8),(257.4,307.8),(259.3,311.3),(262.3,312.1),(263.4,305.8)]
        x,y=monas['x'],monas['y']
        inside=False
        for (ax,ay),(bx,by) in zip(vertices,vertices[1:]+vertices[:1]):
            if (ay>y)!=(by>y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
                inside=not inside
        self.assertTrue(inside)
        self.assertContains(response,'Pelabuhan Marina')
        self.assertContains(response,'Di luar bingkai Jawa')
        self.assertContains(response,'id="destination-9"')
        self.assertNotContains(response,'data-point-id="9"')

    def test_json_escape_and_stale_session(self):
        Destination.objects.filter(source_id=1).update(nama='<script>alert(1)</script>')
        session=self.client.session
        session['dataset_fingerprint']='obsolete'
        session['hasil_terakhir']=[{'nama':'OLD RESULT'}]
        session.save()
        response=self.client.get('/peta/')
        self.assertNotContains(response,'OLD RESULT')
        self.assertNotContains(response,'<script>alert(1)</script>')
        raw=re.search(r'<script id="map-data" type="application/json">(.*?)</script>',response.content.decode(),re.S)
        self.assertIsNotNone(raw)
        self.assertEqual(json.loads(raw.group(1))[0]['nama'],'<script>alert(1)</script>')

    def test_empty_map_remains_usable(self):
        Destination.objects.all().delete()
        response=self.client.get('/peta/')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Belum ada destinasi aktif')
        self.assertEqual(len(response.context['map_provinces']),6)
