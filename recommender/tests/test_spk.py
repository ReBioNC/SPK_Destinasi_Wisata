from django.test import SimpleTestCase

from recommender.spk import geo, similarity


class GeoSimilarityTest(SimpleTestCase):
    def test_haversine_bandung_kawah_putih(self):
        self.assertAlmostEqual(geo.haversine(-6.9175, 107.6191, -7.1662, 107.4022), 36.5745, places=3)

    def test_haversine_nol_untuk_titik_sama(self):
        self.assertEqual(geo.haversine(-6.9, 107.6, -6.9, 107.6), 0.0)

    def test_jaccard_contoh_laporan(self):
        user = {"hiking", "fotografi", "kuliner"}
        dest = {"hiking", "fotografi", "keluarga"}
        self.assertEqual(similarity.jaccard(user, dest), 0.5)

    def test_jaccard_keduanya_kosong(self):
        self.assertEqual(similarity.jaccard(set(), set()), 1.0)
