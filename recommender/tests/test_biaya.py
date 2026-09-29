from django.test import SimpleTestCase

from recommender.spk import biaya


class BiayaTotalTest(SimpleTestCase):
    def test_day_trip_motor(self):
        # tiket 20000 + transport 2*40*250+5000=25000 + makan 150000 + inap 0
        r = biaya.estimasi_total(tiket=20000, jarak_km=40, moda="motor", hari=1)
        self.assertEqual(r["transport"], 25000)
        self.assertEqual(r["makan"], 150000)
        self.assertEqual(r["inap"], 0)
        self.assertEqual(r["total"], 195000)

    def test_menginap_dua_hari(self):
        r = biaya.estimasi_total(tiket=0, jarak_km=10, moda="bus", hari=2)
        self.assertEqual(r["transport"], 2 * 10 * 750)
        self.assertEqual(r["makan"], 300000)
        self.assertEqual(r["inap"], 350000)
        self.assertEqual(r["total"], 2 * 10 * 750 + 300000 + 350000)

    def test_moda_tak_dikenal_ditolak(self):
        with self.assertRaises(ValueError):
            biaya.estimasi_total(tiket=0, jarak_km=1, moda="helikopter", hari=1)

    def test_tarif_pesawat_pp(self):
        # 2 * (400000 + 1200*500) = 2.000.000
        self.assertEqual(biaya.tarif_pesawat_pp(500), 2000000)
