import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from recommender import model_report
from recommender.management.commands.train_clusters import _silhouette


class SilhouetteSamplesTest(SimpleTestCase):
    def test_hitungan_manual_dua_cluster(self):
        data = np.array([[0.0], [2.0], [10.0]])
        a, b, s = model_report.silhouette_samples(data, [0, 0, 1])
        self.assertEqual(a[0], 2.0)
        self.assertEqual(b[0], 10.0)
        self.assertAlmostEqual(s[0], 0.8)
        self.assertEqual(s[2], 0.0)  # Anggota tunggal bernilai 0.

    def test_rata_rata_sama_dengan_fungsi_pelatihan(self):
        data = np.array([[0.0], [0.1], [9.9], [10.0]])
        labels = np.array([0, 0, 1, 1])
        self.assertEqual(_silhouette(data, labels), float(model_report.silhouette_samples(data, labels)[2].mean()))


class ModelReportTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = model_report.load_report(settings.BASE_DIR)

    def test_silhouette_dihitung_ulang_sama_dengan_laporan(self):
        self.assertTrue(self.report["available"])
        self.assertAlmostEqual(self.report["computed_silhouette"], self.report["stored_silhouette"], places=5)

    def test_label_tersimpan_adalah_pusat_terdekat(self):
        stored = json.loads((Path(settings.BASE_DIR) / model_report.REPORT_PATH).read_text(encoding="utf-8"))
        rows = model_report._read_csv(Path(settings.BASE_DIR) / model_report.FEATURES_PATH)
        data = np.array([[float(r[c]) for c in stored["features"]] for r in rows])
        centers = np.array(stored["centroids"])
        nearest = ((data[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
        self.assertEqual(nearest.tolist(), [a["cluster_id"] for a in stored["assignments"]])

    def test_semua_destinasi_ada_pada_grafik(self):
        self.assertEqual(len(self.report["rows"]), 443)
        self.assertEqual(len(self.report["chart_samples"]["hover"]), 443)
        self.assertEqual(len(self.report["chart_scatter"]["points"]), 443)

    def test_artefak_hilang_tidak_melempar_error(self):
        with TemporaryDirectory() as empty:
            self.assertFalse(model_report.load_report(empty)["available"])

    def test_format_angka_indonesia(self):
        self.assertEqual(model_report.num(1234.5, 1), "1.234,5")
        self.assertEqual(model_report.num(-0.052), "−0,052")
        self.assertEqual(model_report.rupiah(275800), "Rp275.800")


class ModelPageTest(SimpleTestCase):
    def test_halaman_memuat_perhitungan_dan_grafik(self):
        response = self.client.get("/model/")
        self.assertEqual(response.status_code, 200)
        for text in ("k = 2", "0,54302", "876,03", "Mengapa k = 2", "Monumen Nasional", "bukan akurasi rekomendasi",
                     "Calinski", "Davies", "414", "Pusat Segmen 2"):
            self.assertContains(response, text)
        self.assertEqual(response.content.decode().count('<svg class="chart"'), 4)

    def test_koordinat_svg_tidak_memakai_koma_desimal(self):
        html = self.client.get("/model/").content.decode()
        self.assertIsNone(re.search(r'\b(?:cx|cy|x1|x2|y1|y2)="-?\d+,\d', html))
        self.assertTrue(re.search(r'cx="\d+\.\d+"', html))

    def test_nama_destinasi_tidak_dirender_mentah(self):
        report = dict(model_report.load_report(settings.BASE_DIR))
        rows = [dict(row) for row in report["rows"]]
        rows[0]["nama"] = "<script>alert(1)</script>"
        report["rows"] = rows
        with patch("recommender.views.model_report.load_report", return_value=report):
            html = self.client.get("/model/").content.decode()
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_pesan_jelas_saat_laporan_belum_ada(self):
        with patch("recommender.views.model_report.load_report", return_value={"available": False}):
            response = self.client.get("/model/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laporan model belum tersedia")

    def test_tautan_navigasi_dan_halaman_metode(self):
        self.assertContains(self.client.get("/model/"), 'href="/model/"')
        self.assertContains(self.client.get("/model/"), 'aria-current="page"')
