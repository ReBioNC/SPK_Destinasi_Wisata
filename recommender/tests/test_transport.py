from unittest.mock import patch

from django.test import TestCase

from recommender import transport
from recommender.spk import geo


class TransportAntarPulauTest(TestCase):
    def test_sama_pulau_darat(self):
        with patch.object(transport, "jarak_darat", return_value=(36.5, "osrm")):
            r = transport.rencanakan(-6.9, 107.6, "Jawa Barat",
                                     -7.1, 107.4, "Jawa Barat", "mobil", "termurah")
            self.assertEqual(r["cara"], "darat")
            self.assertEqual(r["transport"], 2 * 36.5 * 850 + 10000)
            self.assertEqual(r["sumber_jarak"], "osrm")

    def test_beda_pulau_tanpa_koridor_pesawat(self):
        gc = geo.haversine(-6.9, 107.6, -5.1, 119.4)
        r = transport.rencanakan(-6.9, 107.6, "Jawa Barat",
                                 -5.1, 119.4, "Sulawesi Selatan", "mobil", "pesawat")
        self.assertEqual(r["cara"], "pesawat")
        self.assertEqual(r["transport"], 2 * (400000 + 1200 * gc))

    def test_koridor_termurah_memilih_feri(self):
        # Kaki darat dimock: 100 km + 50 km; feri PP 160rb + darat 255rb + parkir 10rb.
        with patch.object(transport, "jarak_darat",
                          side_effect=[(100.0, "osrm"), (50.0, "osrm")]):
            r = transport.rencanakan(-6.9, 107.6, "Jawa Barat",
                                     -5.4, 105.3, "Lampung", "mobil", "termurah")
            self.assertEqual(r["cara"], "feri")
            self.assertEqual(r["transport"], 2 * 80000 + (2 * 150.0 * 850 + 10000))
            self.assertIn("pesawat", r["opsi"])

    def test_darat_feri_tanpa_koridor_jatuh_ke_pesawat(self):
        r = transport.rencanakan(-6.9, 107.6, "Jawa Barat",
                                 -5.1, 119.4, "Sulawesi Selatan",
                                 "mobil", "darat_feri")
        self.assertEqual(r["cara"], "pesawat")
        self.assertIn("koridor", r["rincian"].lower())

    def test_provinsi_tak_dikenal_ditolak(self):
        with self.assertRaises(ValueError):
            transport.rencanakan(0, 0, "Atlantis", 0, 0, "Jawa Barat", "mobil", "termurah")

    def test_koridor_ports(self):
        kunci, pa, pt = transport.koridor_ports("Jawa Barat", "Lampung")
        self.assertEqual((kunci, pa, pt), ("merak_bakauheni", "merak", "bakauheni"))
        kunci, pa, pt = transport.koridor_ports("Lampung", "Jawa Barat")
        self.assertEqual((kunci, pa, pt), ("merak_bakauheni", "bakauheni", "merak"))
        self.assertIsNone(transport.koridor_ports("Jawa Barat", "Sulawesi Selatan"))
        kunci, _, _ = transport.koridor_ports("Jawa Barat", "Bali")
        self.assertEqual(kunci, "ketapang_gilimanuk")
