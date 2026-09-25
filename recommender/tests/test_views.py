from django.test import TestCase

from recommender.models import Destination

# (nama, harga, rating, lat, lon, kategori, tags, n_fasilitas_True)
FIXTURE = [
    ("Kawah Putih Ciwidey", 81000, 4.6, -7.1662, 107.4022, "alam", "hiking", 4),
    ("Gunung Tangkuban Perahu", 30000, 4.4, -6.7597, 107.6097, "alam", "hiking", 4),
    ("Saung Angklung Udjo", 75000, 4.7, -6.8977, 107.6553, "budaya", "fotografi|musik|seni|budaya", 4),
    ("Farmhouse Lembang", 30000, 4.3, -6.8330, 107.6027, "hiburan", "hiking", 4),
    ("Trans Studio Bandung", 200000, 4.5, -6.9258, 107.6366, "hiburan", "hiking|keluarga|belanja", 5),
    ("Pantai Pangandaran", 15000, 4.2, -7.6950, 108.6550, "alam", "hiking|fotografi|pantai|renang|ombak", 5),
    ("Museum Geologi Bandung", 5000, 4.5, -6.9007, 107.6215, "budaya", "sejarah|edukasi", 3),
    ("Dusun Bambu Lembang", 25000, 4.4, -6.7960, 107.5750, "kuliner", "hiking", 5),
    ("Situ Patenggang", 20000, 4.3, -7.1650, 107.3600, "alam", "hiking|fotografi|danau|keluarga|sampan", 3),
    ("Masjid Raya Al Jabbar", 5000, 4.1, -6.9450, 107.6900, "religi", "fotografi|religi|ibadah|arsitektur", 4),
]


class RekomendasiViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        flags = ["fas_toilet", "fas_parkir", "fas_warung", "fas_mushola", "fas_penginapan"]
        for nama, harga, rating, lat, lon, kat, tag, n_true in FIXTURE:
            kw = {f: (i < n_true) for i, f in enumerate(flags)}
            Destination.objects.create(nama=nama, kota="Bandung", provinsi="Jawa Barat",
                                       kategori=kat, harga_tiket=harga, rating=rating,
                                       latitude=lat, longitude=lon,
                                       tag_aktivitas=tag, **kw)

    def post_valid(self, **over):
        data = {"budget": "250000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                "kategori_utama": "alam", "kategori_sekunder": "budaya",
                "hobi": ["hiking", "fotografi"], "profil": "seimbang"}
        data.update(over)
        return self.client.post("/", data)

    def test_post_valid_menampilkan_10_hasil_urutan_benar(self):
        r = self.post_valid()
        self.assertEqual(r.status_code, 200)
        names = [h["nama"] for h in r.context["hasil"]]
        self.assertEqual(names[0], "Gunung Tangkuban Perahu")
        self.assertEqual(len(names), 10)

    def test_budget_format_ribuan_diterima(self):
        for b in ["250.000", "Rp 250000", "250,000"]:
            r = self.post_valid(budget=b)
            self.assertEqual(r.status_code, 200)
            self.assertIn("hasil", r.context)

    def test_budget_invalid_ada_pesan(self):
        r = self.post_valid(budget="gratis")
        self.assertContains(r, "Masukkan budget dalam angka")

    def test_kandidat_kosong_ramah(self):
        r = self.post_valid(budget="1000")
        self.assertContains(r, "longgarkan")

    def test_c6_nol_semua_tetap_jalan(self):
        r = self.post_valid(hobi=[])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["hasil"]), 10)

    def test_slider_mengubah_urutan(self):
        r = self.post_valid(**{"w1": "100", "w2": "0", "w3": "0", "w4": "0", "w5": "0", "w6": "0"})
        names = [h["nama"] for h in r.context["hasil"]]
        self.assertTrue(r.context["mode_custom"])
        self.assertEqual(names[0], "Museum Geologi Bandung")

    def test_slider_nol_semua_kembali_ke_profil(self):
        r = self.post_valid(**{f"w{i}": "0" for i in range(1, 7)})
        self.assertFalse(r.context["mode_custom"])
        self.assertContains(r, "dipakai bobot profil")
