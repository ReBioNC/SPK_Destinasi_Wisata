from django.test import TestCase

from recommender.models import JarakCache
from recommender.spk.biaya import GUGUS_PULAU, PETA_PULAU


class PulauTest(TestCase):
    def test_38_provinsi_terpetakan_7_gugus(self):
        self.assertEqual(len(PETA_PULAU), 38)
        self.assertEqual(set(PETA_PULAU.values()), set(GUGUS_PULAU))
        self.assertEqual(len(GUGUS_PULAU), 7)

    def test_contoh_pemetaan(self):
        self.assertEqual(PETA_PULAU["Bali"], "Bali-Nusa Tenggara")
        self.assertEqual(PETA_PULAU["Papua Pegunungan"], "Papua")
        self.assertEqual(PETA_PULAU["Daerah Istimewa Yogyakarta"], "Jawa")
        self.assertEqual(PETA_PULAU["Kepulauan Riau"], "Sumatera")


class JarakCacheTest(TestCase):
    def test_simpan_dan_ambil(self):
        JarakCache.objects.create(asal="-6.9,107.6", tujuan="-7.1,107.4",
                                  moda="mobil", jarak_km=36.5, sumber="osrm")
        c = JarakCache.objects.get(asal="-6.9,107.6", tujuan="-7.1,107.4", moda="mobil")
        self.assertEqual(c.jarak_km, 36.5)
        self.assertEqual(c.sumber, "osrm")

    def test_unik_per_pasangan_moda(self):
        JarakCache.objects.create(asal="A", tujuan="B", moda="mobil",
                                  jarak_km=10, sumber="osrm")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            JarakCache.objects.create(asal="A", tujuan="B", moda="mobil",
                                      jarak_km=11, sumber="fallback")
