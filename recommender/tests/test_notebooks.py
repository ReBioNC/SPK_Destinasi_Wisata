import json
import tempfile
import unittest
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from recommender.management.commands.train_clusters import _fit_kmeans  # noqa: E402
from recommender.tests.test_data_pipeline import ROOT, copy_sources  # noqa: E402

OUTPUTS = ("data/processed/destinations_clean_java443.csv", "data/processed/destinations_kmeans_features_java443.csv")


def run_notebook(name, root):
    notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    scope = {"PROJECT_ROOT": root, "display": lambda value: None}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # plt.show pada backend Agg.
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                exec(compile("".join(cell["source"]), name, "exec"), scope)
    plt.close("all")
    return scope


class TrainingNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = run_notebook("04_training_kmeans.ipynb", ROOT)

    def test_hasil_sama_dengan_laporan_tersimpan(self):
        self.assertIsNotNone(self.scope["comparison"])
        self.assertTrue(bool(self.scope["comparison"]["cocok"].all()))

    def test_kode_kmeans_sama_dengan_command_pelatihan(self):
        data = self.scope["X"]
        inertia, centers, labels = self.scope["fit_kmeans"](data, 3)
        expected = _fit_kmeans(data, 3, seed=42, starts=10)
        self.assertEqual(inertia, expected[0])
        self.assertTrue(np.array_equal(centers, expected[1]))
        self.assertTrue(np.array_equal(labels, expected[2]))

    def test_tidak_menulis_file(self):
        source = (ROOT / "notebooks/04_training_kmeans.ipynb").read_text(encoding="utf-8")
        for call in (".to_csv(", ".write_text(", ".write_bytes(", ".savefig("):
            self.assertNotIn(call, source)


class PreprocessingNotebookTests(unittest.TestCase):
    def test_output_tetap_identik_dengan_pipeline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root)
            run_notebook("03_preprocessing_simple.ipynb", root)
            for relative in OUTPUTS:
                self.assertEqual((root / relative).read_bytes(), (ROOT / relative).read_bytes(), relative)
