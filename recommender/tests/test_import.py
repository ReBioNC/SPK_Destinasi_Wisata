from django.core.management import call_command
from django.test import TestCase

from recommender.models import Destination


class ImportTest(TestCase):
    def test_impor_jawa443_dan_idempoten(self):
        call_command("import_destinations")
        total = Destination.objects.count()
        self.assertEqual(total, 443)
        call_command("import_destinations")  # rerun
        self.assertEqual(Destination.objects.count(), total)

    def test_koordinat_terisi_dan_contoh_benar(self):
        call_command("import_destinations")
        self.assertEqual(Destination.objects.filter(latitude__isnull=True).count(), 0)
        monas = Destination.objects.get(nama="Monumen Nasional")
        self.assertAlmostEqual(monas.latitude, -6.1753924, places=4)

    def test_dua_sumber_jawa_bertanda(self):
        call_command("import_destinations")
        self.assertEqual(Destination.objects.filter(sumber_data="kaggle_java").count(), 437)
        self.assertEqual(Destination.objects.filter(sumber_data="curated_java").count(), 6)
        self.assertEqual(Destination.objects.get(nama="Monumen Nasional").rating, 4.6)

    def test_provinsi_tepat_enam_tanpa_alias(self):
        call_command("import_destinations")
        prov = set(Destination.objects.values_list("provinsi", flat=True).distinct())
        self.assertEqual(len(prov), 6)
        self.assertNotIn("DI Yogyakarta", prov)
