from unittest.mock import patch
from urllib.error import URLError

from django.test import TestCase

from recommender import jarak
from recommender.models import JarakCache
from recommender.spk import geo


class JarakDaratTest(TestCase):
    ARGS = (-6.9175, 107.6191, -7.1662, 107.4022)

    def test_fetch_osrm_dan_cache(self):
        body = b'{"code":"Ok","routes":[{"distance":36574.5}]}'
        with patch.object(jarak, "_ambil_osrm", return_value=body) as m:
            km, sumber = jarak.jarak_darat(*self.ARGS)
            self.assertAlmostEqual(km, 36.5745, places=3)
            self.assertEqual(sumber, "osrm")
            self.assertEqual(m.call_count, 1)
            km2, sumber2 = jarak.jarak_darat(*self.ARGS)
            self.assertEqual((km2, sumber2), (km, "cache"))
            self.assertEqual(m.call_count, 1)  # tak ada request kedua
        self.assertEqual(JarakCache.objects.count(), 1)

    def test_offline_fallback_haversine(self):
        with patch.object(jarak, "_ambil_osrm", side_effect=URLError("offline")):
            km, sumber = jarak.jarak_darat(*self.ARGS)
            self.assertEqual(sumber, "fallback")
            self.assertAlmostEqual(km, geo.haversine(*self.ARGS) * 1.3, places=3)

    def test_noroute_fallback(self):
        body = b'{"code":"NoRoute","routes":[]}'
        with patch.object(jarak, "_ambil_osrm", return_value=body):
            km, sumber = jarak.jarak_darat(*self.ARGS)
            self.assertEqual(sumber, "fallback")
