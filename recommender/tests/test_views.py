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
        extra = {k: over.pop(k) for k in list(over) if k.startswith("HTTP_")}
        data.update(over)
        return self.client.post("/", data, **extra)

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

    def test_budget_negatif_ditolak(self):
        r = self.post_valid(budget="-50000")
        self.assertContains(r, "Masukkan budget dalam angka")
        self.assertIsNone(r.context["hasil"])

    def test_kandidat_kosong_ramah(self):
        r = self.post_valid(budget="1000")
        self.assertContains(r, "longgarkan")

    def test_c6_nol_semua_tetap_jalan(self):
        r = self.post_valid(hobi=[])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["hasil"]), 10)

    def test_slider_mengubah_urutan(self):
        r = self.post_valid(**{"w1": "100", "w2": "0", "w3": "0", "w4": "0", "w5": "0", "w6": "0",
                               "sentuh_bobot": "1"})
        names = [h["nama"] for h in r.context["hasil"]]
        self.assertTrue(r.context["mode_custom"])
        self.assertEqual(names[0], "Museum Geologi Bandung")

    def test_slider_nol_semua_kembali_ke_profil(self):
        r = self.post_valid(**{f"w{i}": "0" for i in range(1, 7)}, sentuh_bobot="1")
        self.assertFalse(r.context["mode_custom"])
        self.assertContains(r, "dipakai bobot profil")

    def test_submit_normal_tanpa_sentuh_slider_pakai_profil(self):
        # Payload browser asli: slider selalu terkirim dengan nilai default.
        r = self.post_valid(**{"w1": "27", "w2": "18", "w3": "16", "w4": "8",
                               "w5": "16", "w6": "16", "sentuh_bobot": "0"})
        self.assertFalse(r.context["mode_custom"])
        self.assertNotContains(r, "Memakai bobot kustom")

    def test_slider_hasil_menampilkan_persen_bobot(self):
        r = self.post_valid()
        html = r.content.decode()
        for val in ['name="w1" min="0" max="100" value="27"',
                    'name="w4" min="0" max="100" value="8"']:
            self.assertIn(val, html)

    def test_satu_kandidat_tidak_500(self):
        Destination.objects.exclude(pk=Destination.objects.first().pk).delete()
        self.assertEqual(Destination.objects.count(), 1)
        satu = Destination.objects.get()
        r = self.post_valid(budget="999999999", wilayah=satu.provinsi,
                            kategori_utama=satu.kategori, kategori_sekunder=satu.kategori,
                            hobi=[])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["hasil"]), 1)
        self.assertEqual(r.context["hasil"][0]["vi"], 1.0)

    def test_wilayah_dari_peta_terisi_otomatis(self):
        r = self.client.get("/", {"wilayah": "Jawa Barat"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'value="Jawa Barat" selected')
        self.assertContains(r, "terisi dari peta")

    def test_wilayah_param_invalid_diabaikan(self):
        r = self.client.get("/", {"wilayah": "Atlantis"})
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "terisi dari peta")

    def test_profil_ada_deskripsi_bobot(self):
        r = self.client.get("/")
        self.assertContains(r, "profil-info")
        for teks in ["Hemat", "Kualitas", "Petualang", "Seimbang", "41%", "38%", "34%", "27%"]:
            self.assertContains(r, teks)

    def test_help_text_deskripsi_pilihan(self):
        r = self.client.get("/")
        self.assertContains(r, "otomatis tersaring")
        self.assertContains(r, "menentukan jarak")

    def test_profil_terpilih_terlihat_langsung(self):
        r = self.client.get("/")
        self.assertContains(r, ".profil-info:has(input:checked)")

    def test_profil_satu_sumber_status_terpilih(self):
        # Status terpilih hanya dari :has (sinkron DOM); tidak ada ring server
        # basi yang bisa tampil bersamaan dengan kartu yang benar-benar dicentang.
        r = self.client.get("/")
        self.assertNotContains(r, "ring-primary/20")

    def test_post_profil_hemat_tercerminkan(self):
        r = self.post_valid(profil="hemat")
        self.assertEqual(r.status_code, 200)
        self.assertRegex(r.content.decode(), r'checked=""[^>]*value="hemat"')

    def test_ajax_hasil_tanpa_refresh(self):
        r = self.post_valid(HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], 10)
        self.assertIn("Gunung Tangkuban Perahu", data["html"])
        self.assertNotIn("<html", data["html"])

    def test_ajax_form_invalid(self):
        r = self.post_valid(budget="gratis", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()["ok"])

    def test_budget_format_ribuan_hook(self):
        r = self.client.get("/")
        self.assertContains(r, "formatBudgetRibuan")

    def test_kota_asal_ratusan_kota_berkoordinat(self):
        from recommender.kota_asal import KOTA_ASAL
        self.assertGreaterEqual(len(KOTA_ASAL), 300)
        lat, lon = KOTA_ASAL["Badung"]
        self.assertAlmostEqual(lat, -8.5833, places=3)
        self.assertAlmostEqual(lon, 115.1833, places=3)
        for nama, (la, lo) in KOTA_ASAL.items():
            self.assertTrue(-90 <= la <= 90, nama)
            self.assertTrue(-180 <= lo <= 180, nama)

    def test_dataset_kota_file(self):
        import csv
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent.parent
        p = root / "data" / "kota_indonesia.csv"
        self.assertTrue(p.exists(), "data/kota_indonesia.csv tidak ada")
        with open(p, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(
            list(rows[0].keys()),
            ["nama", "tipe", "provinsi", "lat", "lon", "sumber"])
        self.assertGreaterEqual(len(rows), 300)
        self.assertTrue(all(r["sumber"].strip() for r in rows),
                        "setiap baris wajib punya sumber")
        self.assertTrue(any("Kemendagri" in r["sumber"] for r in rows))
        from recommender.kota_asal import KOTA_ASAL
        self.assertEqual(len(rows), len(KOTA_ASAL))

    def test_kota_searchable_di_form(self):
        r = self.client.get("/")
        self.assertContains(r, "kota_asal_input")
        self.assertContains(r, "kota-menu")
        self.assertContains(r, "Badung (Bali)")

    def test_kota_tanpa_lib_pihak_ketiga(self):
        # Combobox milik sendiri: tidak ada sisa Tom Select yang bisa merusak layer/tema.
        r = self.client.get("/")
        html = r.content.decode()
        self.assertNotIn("TomSelect", html)
        self.assertNotIn("tom-select", html)

    def test_kota_menu_punya_class_terstyle(self):
        # Menu dibuat via JS harus membawa class yang ditarget CSS (.kota-menu),
        # kalau tidak ia ter-render polos di ujung body, di luar viewport.
        r = self.client.get("/")
        self.assertContains(r, "menu.className = 'kota-menu'")

    def test_kota_dropdown_terlihat_penuh(self):
        # Menu milik sendiri: background/border/shadow eksplisit + di body.
        r = self.client.get("/")
        html = r.content.decode()
        self.assertIn(".kota-menu", html)
        self.assertNotIn("dropdownParent", html)  # sisa Tom Select harus hilang
        self.assertIn("background:#fff", html.replace(" ", ""))

    def test_post_kota_baru_valid(self):
        r = self.post_valid(kota_asal="Badung")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context["form"].errors)
        self.assertEqual(len(r.context["hasil"]), 10)


class HalamanTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        flags = ["fas_toilet", "fas_parkir", "fas_warung", "fas_mushola", "fas_penginapan"]
        for nama, harga, rating, lat, lon, kat, tag, n_true in FIXTURE:
            kw = {f: (i < n_true) for i, f in enumerate(flags)}
            Destination.objects.create(nama=nama, kota="Bandung", provinsi="Jawa Barat",
                                       kategori=kat, harga_tiket=harga, rating=rating,
                                       latitude=lat, longitude=lon,
                                       tag_aktivitas=tag, **kw)

    def test_peta_dan_tentang_200(self):
        self.assertEqual(self.client.get("/peta/").status_code, 200)
        self.assertEqual(self.client.get("/tentang/").status_code, 200)

    def test_peta_memakai_hasil_session(self):
        self.client.post("/", {"budget": "250000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                               "kategori_utama": "alam", "kategori_sekunder": "budaya",
                               "hobi": ["hiking", "fotografi"], "profil": "seimbang"})
        r = self.client.get("/peta/")
        self.assertContains(r, "Tangkuban Perahu")

    def test_peta_hasil_json_valid_array(self):
        import json
        import re
        self.client.post("/", {"budget": "250000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                               "kategori_utama": "alam", "kategori_sekunder": "budaya",
                               "hobi": ["hiking", "fotografi"], "profil": "seimbang"})
        r = self.client.get("/peta/")
        m = re.search(r'<script id="hasil-data" type="application/json">(.*?)</script>',
                      r.content.decode(), re.S)
        self.assertIsNotNone(m)
        data = json.loads(m.group(1))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0]["nama"], "Gunung Tangkuban Perahu")

    def test_peta_tanpa_session_fallback_agregat(self):
        r = self.client.get("/peta/")
        self.assertContains(r, "Jawa Barat")
