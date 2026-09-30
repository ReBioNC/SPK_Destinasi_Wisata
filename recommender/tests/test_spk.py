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


# Fixture: matriks keputusan A1-A10 dari Perhitungan_SPK_TravelFit.xlsx (kolom C1..C6).
A10 = [
    [81000, 4.6, 36.5745, 0.8, 1.0, 0.50],   # A1
    [30000, 4.4, 17.5772, 0.8, 1.0, 0.50],   # A2
    [75000, 4.7, 4.5624, 0.8, 0.5, 0.20],    # A3
    [30000, 4.3, 9.5688, 0.8, 0.0, 0.50],    # A4
    [200000, 4.5, 2.1409, 1.0, 0.0, 0.25],   # A5
    [15000, 4.2, 143.2742, 1.0, 1.0, 0.40],  # A6
    [5000, 4.5, 1.8868, 0.6, 0.5, 0.0],      # A7
    [25000, 4.4, 14.3607, 1.0, 0.0, 0.50],   # A8
    [20000, 4.3, 39.6859, 0.6, 1.0, 0.40],   # A9
    [5000, 4.1, 8.4023, 0.8, 0.0, 0.20],     # A10
]
W_SEIMBANG = [0.269294111685416, 0.17848214587345024, 0.15674301543866762,
              0.08199469612513091, 0.15674301543866762, 0.15674301543866762]


class TopsisTest(SimpleTestCase):
    def test_invalid_numeric_inputs_rejected(self):
        from recommender.spk import topsis
        cases = [([[float('nan')]], [1], [False]), ([[float('inf')]], [1], [False]),
                 ([[1]], [-1], [False]), ([[1]], [0], [False]), ([[1,2]], [1], [False])]
        for scores, weights, costs in cases:
            with self.subTest(scores=scores, weights=weights), self.assertRaises(ValueError):
                topsis.rank(scores, weights, costs)

    def test_cost_benefit_and_ties(self):
        from recommender.spk import topsis
        self.assertEqual(topsis.rank([[1],[2]], [1], [True])[0]['idx'], 0)
        self.assertEqual(topsis.rank([[1],[2]], [1], [False])[0]['idx'], 1)
        self.assertEqual([r['vi'] for r in topsis.rank([[0],[0]], [1], [False])], [1,1])

    def test_urutan_sama_dengan_excel(self):
        from recommender.spk import topsis
        from recommender.spk.profiles import IS_COST
        res = topsis.rank(A10, W_SEIMBANG, IS_COST)
        self.assertEqual([r["idx"] for r in res], [1, 8, 6, 7, 9, 3, 2, 0, 5, 4])

    def test_spearman_topsis_vs_saw_rendah(self):
        from recommender.spk import topsis, validation
        from recommender.spk.profiles import IS_COST
        t = [r["idx"] for r in topsis.rank(A10, W_SEIMBANG, IS_COST)]
        s = [i for i, _ in validation.saw_rank(A10, W_SEIMBANG, IS_COST)]
        self.assertAlmostEqual(validation.spearman(t, s), 0.2970, places=3)

    def test_kolom_nol_semua_tidak_division_by_zero(self):
        from recommender.spk import topsis
        from recommender.spk.profiles import IS_COST
        nol_c6 = [row[:5] + [0.0] for row in A10]
        res = topsis.rank(nol_c6, W_SEIMBANG, IS_COST)
        self.assertEqual(len(res), 10)
        self.assertTrue(all(0.0 <= r["vi"] <= 1.0 for r in res))

    def test_satu_kandidat_vi_satu_tanpa_crash(self):
        from recommender.spk import topsis
        from recommender.spk.profiles import IS_COST
        res = topsis.rank([A10[1]], W_SEIMBANG, IS_COST)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["vi"], 1.0)

    def test_rentang_kriteria_tetap_dari_semua_kandidat(self):
        from recommender.spk import topsis
        res = topsis.rank([[1, 5], [2, 4], [10, 3]], [0.5, 0.5], [True, False])
        self.assertEqual(len(res), 3)
        self.assertTrue(all(len(row["span"]) == 2 for row in res))
        self.assertTrue(all(row["span"] == res[0]["span"] for row in res))

    def test_saw_menerima_harga_gratis_dan_kolom_nol(self):
        from recommender.spk import validation
        ranking = validation.saw_rank([[0, 0], [100, 0]], [0.5, 0.5], [True, False])
        self.assertEqual(ranking[0][0], 0)
        self.assertTrue(all(0 <= score <= 1 for _, score in ranking))
        self.assertEqual(validation.spearman([0], [0]), 1.0)
