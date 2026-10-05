from django.test import TestCase
from recommender.models import Destination


class TicketBudgetTests(TestCase):
    """Catch travel-cost filtering leaking into the ticket-only contract."""
    @classmethod
    def setUpTestData(cls):
        for sid, name, price in [(1, 'Gratis', 0), (2, 'Batas tepat', 10000), (3, 'Melebihi', 20000)]:
            Destination.objects.create(source_id=sid, nama=name, kota='Bandung', provinsi='Jawa Barat',
                kategori='alam', harga_tiket=price, rating=4.5, rating_model=4.5,
                latitude=-6.9175, longitude=107.6191, pipeline_fingerprint='fixture')

    def post(self, **overrides):
        values = dict(budget='10000', kota_asal='Bandung', wilayah='Jawa Barat',
            kategori_utama='alam', kategori_sekunder='alam', profil='hemat',
            sentuh_bobot='1', w1=100, w2=0, w3=0, w4=0, w5=0, w6=0)
        values.update(overrides)
        return self.client.post('/', values, follow=True)

    def test_ticket_boundary_and_c1_not_total_travel_cost(self):
        response = self.post()
        self.assertFalse(response.context['form'].errors)
        rows = response.context['hasil']
        self.assertEqual([r['source_id'] for r in rows], [1, 2])
        self.assertEqual([r['harga'] for r in rows], [0, 10000])
        self.assertEqual([r['sisa_budget'] for r in rows], [10000, 0])
        self.assertEqual([r['vi'] for r in rows], [1.0, 0.0])
        self.assertEqual([r['jarak_km'] for r in rows], [0.0, 0.0])

    def test_zero_budget_recommends_free_destination(self):
        response = self.post(budget='0')
        self.assertFalse(response.context['form'].errors)
        self.assertEqual([r['source_id'] for r in response.context['hasil']], [1])
        self.assertEqual(response.context['hasil'][0]['vi'], 1.0)

    def test_departure_distance_does_not_exclude_free_destination(self):
        response = self.post(budget='0', kota_asal='Badung')
        self.assertFalse(response.context['form'].errors)
        self.assertEqual(response.context['hasil'][0]['harga'], 0)
        self.assertGreater(response.context['hasil'][0]['jarak_km'], 0)

    def test_no_transport_fields_and_snapshot_disclaimer(self):
        response = self.client.get('/')
        fields = response.context['form'].fields
        self.assertNotIn('moda', fields)
        self.assertNotIn('hari', fields)
        self.assertNotIn('mode_antar', fields)
        for legacy in ('moda', 'hari', 'mode_antar'):
            self.assertNotIn(legacy, response.context['cur'])
        self.assertContains(response, 'Budget maksimal tiket masuk')
        self.assertNotContains(response, 'Biaya perjalanan adalah estimasi')
        response = self.post()
        self.assertContains(response, 'belum termasuk transportasi, makan, dan penginapan')
        self.assertContains(response, 'Sisa alokasi tiket')
