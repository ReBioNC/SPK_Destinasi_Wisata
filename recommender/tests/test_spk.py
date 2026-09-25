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


class AhpTest(SimpleTestCase):
    def test_bobot_seimbang_sama_dengan_spreadsheet(self):
        from recommender.spk import ahp, profiles
        m = profiles.matrix_from_upper(profiles.PROFILE_UPPERS["seimbang"])
        w = ahp.weights_from_matrix(m)
        for got, exp in zip(w, [0.2693, 0.1785, 0.1567, 0.0820, 0.1567, 0.1567]):
            self.assertAlmostEqual(got, exp, places=4)

    def test_cr_seimbang(self):
        from recommender.spk import ahp, profiles
        m = profiles.matrix_from_upper(profiles.PROFILE_UPPERS["seimbang"])
        res = ahp.consistency(m, ahp.weights_from_matrix(m))
        self.assertAlmostEqual(res["cr"], 0.008418, places=5)
        self.assertLess(res["cr"], 0.1)

    def test_semua_profil_aktif_konsisten(self):
        from recommender.spk import profiles
        self.assertEqual(set(profiles.ACTIVE_PROFILES), {"hemat", "kualitas", "petualang", "seimbang"})
        for p in profiles.ACTIVE_PROFILES.values():
            self.assertLess(p["cr"], 0.1)
            self.assertAlmostEqual(sum(p["weights"]), 1.0, places=6)
