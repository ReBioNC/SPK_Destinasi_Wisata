from django.test import TestCase

from recommender.models import Destination
from recommender.kota_asal import KOTA_ASAL

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


def _mock_rencanakan(lat1, lon1, prov1, lat2, lon2, prov2,
                     moda="mobil", mode="termurah"):
    """Pengganti deterministik tanpa network: darat bila sepulau."""
    from recommender.spk import biaya, geo
    from recommender.spk.biaya import PETA_PULAU
    gc = geo.haversine(lat1, lon1, lat2, lon2)
    if PETA_PULAU.get(prov1) == PETA_PULAU.get(prov2):
        return {"transport": biaya.transport_pp(gc, moda), "cara": "darat",
                "rincian": "mock darat", "sumber_jarak": "mock",
                "opsi": None, "jarak_km": gc}
    return {"transport": biaya.tarif_pesawat_pp(gc), "cara": "pesawat",
            "rincian": "mock udara", "sumber_jarak": "estimasi-pesawat",
            "opsi": None, "jarak_km": gc}


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
        data = {"budget": "500000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                "kategori_utama": "alam", "kategori_sekunder": "budaya",
                "hobi": ["hiking", "fotografi"], "profil": "seimbang",
                "moda": "mobil", "hari": "1", "mode_antar": "termurah"}
        extra = {k: over.pop(k) for k in list(over) if k.startswith("HTTP_")}
        data.update(over)
        return self.client.post("/", data, follow=True, **extra)

    def test_post_valid_menampilkan_10_hasil_urutan_benar(self):
        r = self.post_valid()
        self.assertEqual(r.status_code, 200)
        names = [h["nama"] for h in r.context["hasil"]]
        self.assertEqual(names[0], "Gunung Tangkuban Perahu")
        self.assertEqual(len(names), 10)
        self.assertTrue(all(not h['simulasi'] for h in r.context['hasil']))
        self.assertContains(r, "garis lurus")

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

    def test_budget_teks_campuran_ditolak(self):
        for budget in ["abc250000", "12,34", "Rp -250000"]:
            with self.subTest(budget=budget):
                r = self.post_valid(budget=budget)
                self.assertContains(r, "Masukkan budget dalam angka")

    def test_kandidat_kosong_ramah(self):
        r = self.post_valid(budget="1000")
        self.assertContains(r, "longgarkan")

    def test_c6_nol_semua_tetap_jalan(self):
        r = self.post_valid(hobi=[])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context["hasil"]), 10)
        self.assertTrue(all(h["bars"][5]["no_effect"] for h in r.context["hasil"]))
        self.assertTrue(all(h["bars"][5]["sub"] == "Hobi tidak dipilih" for h in r.context["hasil"]))

    def test_c4_memakai_enam_kelompok_deskripsi(self):
        destination = Destination.objects.get(nama="Kawah Putih Ciwidey")
        destination.fas_accessibility = True
        destination.fas_information_center = True
        self.assertEqual(destination.facility_score(), 1.0)
        destination.fas_toilet = False
        self.assertAlmostEqual(destination.facility_score(), 5/6)

    def test_penjelasan_kriteria_tetap_tidak_menyebut_unggul(self):
        from recommender.views import _bangun_alasan
        self.assertEqual(_bangun_alasan([0, 0], [0, 0]),
                         "Semua kandidat bernilai sama pada kriteria yang digunakan.")
        self.assertNotIn("Rating", _bangun_alasan([0.2, 0], [1, 0]))

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
        self.assertContains(r, "belum ada perbandingan")

    def test_refresh_membersihkan_hasil(self):        # Refresh = sesi baru: hasil hanya tampil sekali setelah redirect.
        r = self.post_valid()
        self.assertEqual(len(r.context["hasil"]), 10)
        r2 = self.client.get("/")
        self.assertIsNone(r2.context["hasil"])
        self.assertContains(r2, "Siap menghitung rekomendasi.")

    def test_c1_harga_tiket_dan_sisa_alokasi(self):
        r = self.post_valid()
        for row in r.context["hasil"]:
            source = Destination.objects.get(nama=row["nama"])
            self.assertEqual(row["harga"], source.harga_tiket)
            self.assertEqual(row["sisa_budget"], 500000 - source.harga_tiket)

    def test_budget_menyaring_tiket_bukan_total_perjalanan(self):
        r = self.post_valid(budget="100000")
        self.assertEqual(len(r.context["hasil"]), 9)
        self.assertNotIn("Trans Studio Bandung", [row["nama"] for row in r.context["hasil"]])

    def test_budget_6000_masih_menerima_tiket_5000(self):
        r = self.post_valid(budget="6000")
        self.assertEqual({row["nama"] for row in r.context["hasil"]},
                         {"Museum Geologi Bandung", "Masjid Raya Al Jabbar"})

    def test_parameter_transport_lama_diabaikan(self):
        r = self.post_valid(moda="helikopter", hari="0", mode_antar="unknown")
        self.assertFalse(r.context["form"].errors)
        self.assertNotIn("moda", self.client.session["preference_input"])
        self.assertNotIn("hari", self.client.session["preference_input"])

    def test_rekomendasi_tanpa_network_atau_cache(self):
        from unittest.mock import patch
        from recommender.models import JarakCache
        with patch("recommender.jarak._ambil_osrm", side_effect=AssertionError("Unexpected network")):
            r = self.post_valid()
        self.assertEqual(len(r.context["hasil"]), 10)
        self.assertEqual(JarakCache.objects.count(), 0)

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
        self.assertContains(r, "tiket masuk satu destinasi per orang")
        self.assertContains(r, "menentukan jarak")

    def test_profil_terpilih_terlihat_langsung(self):
        r = self.client.get("/")
        self.assertContains(r, 'value="seimbang" checked')
        self.assertContains(r, 'for="profile-seimbang"')
        self.assertContains(r, 'recommender/travelfit.css')

    def test_profil_satu_sumber_status_terpilih(self):
        # Status terpilih hanya dari :has (sinkron DOM); tidak ada ring server
        # basi yang bisa tampil bersamaan dengan kartu yang benar-benar dicentang.
        r = self.client.get("/")
        self.assertNotContains(r, "ring-primary/20")

    def test_post_profil_hemat_tercerminkan(self):
        r = self.post_valid(profil="hemat")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["ringkasan"]["profil"], "Hemat")

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

    def test_budget_invalid_tetap_bisa_diperbaiki(self):
        r = self.post_valid(budget="minus-seratus")
        self.assertContains(r, 'type="text" name="budget" value="minus-seratus"')
        self.assertTrue(r.context['form'].errors['budget'])

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
        self.assertContains(r, 'id="id_kota_asal"')
        self.assertContains(r, "Badung (Bali)")

    def test_kota_tanpa_lib_pihak_ketiga(self):
        # Combobox milik sendiri: tidak ada sisa Tom Select yang bisa merusak layer/tema.
        r = self.client.get("/")
        html = r.content.decode()
        self.assertNotIn("TomSelect", html)
        self.assertNotIn("tom-select", html)

    def test_kota_select_native_memuat_semua_pilihan(self):
        r = self.client.get("/")
        self.assertContains(r, '<select name="kota_asal"')
        self.assertEqual(len(r.context['form'].fields['kota_asal'].choices), len(KOTA_ASAL))

    def test_peta_bisa_dibuka_dari_beranda(self):
        r = self.client.get("/")
        self.assertContains(r, 'href="/peta/"')
        self.assertEqual(self.client.get('/peta/').status_code, 200)

    def test_kota_terpilih_tetap_ada_saat_validasi_gagal(self):
        r = self.post_valid(kota_asal="Badung", budget="gratis")
        self.assertContains(r, 'value="Badung" selected')
        self.assertContains(r, 'label for="id_kota_asal"')
        self.assertNotContains(r, 'dropdownParent')

    def test_post_kota_baru_valid(self):
        # Kota asal hanya mengubah C3, bukan harga tiket atau filter budget.
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
        self.client.post("/", {"budget": "500000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                               "kategori_utama": "alam", "kategori_sekunder": "budaya",
                               "hobi": ["hiking", "fotografi"], "profil": "seimbang",
                               "moda": "mobil", "hari": "1", "mode_antar": "termurah"})
        r = self.client.get("/peta/")
        self.assertContains(r, "Tangkuban Perahu")

    def test_peta_hasil_json_valid_array(self):
        import json
        import re
        self.client.post("/", {"budget": "500000", "kota_asal": "Bandung", "wilayah": "Jawa Barat",
                               "kategori_utama": "alam", "kategori_sekunder": "budaya",
                               "hobi": ["hiking", "fotografi"], "profil": "seimbang",
                               "moda": "mobil", "hari": "1", "mode_antar": "termurah"})
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
