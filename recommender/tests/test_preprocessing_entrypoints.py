import io
import json
from pathlib import Path
import tempfile
import unittest
from django.core.management import call_command, CommandError
from recommender.tests.test_data_pipeline import ROOT, copy_sources


class PreprocessingEntrypointsTests(unittest.TestCase):
    def run_notebook(self, root):
        notebook = json.loads((ROOT / 'notebooks/01_preprocessing_travelfit.ipynb').read_text(encoding='utf-8'))
        scope = {'PROJECT_ROOT': root, 'display': lambda value: None}
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                exec(compile(''.join(cell['source']), 'java443_notebook', 'exec'), scope)
        return scope

    def test_command_exports_443_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root)
            try:
                call_command('preprocess_destinations', project_root=str(root), stdout=io.StringIO())
            except CommandError as error:
                self.fail(str(error))
            import pandas as pd
            frame = pd.read_csv(root / 'data/processed/destinations_clean_java443.csv')
            self.assertEqual(len(frame), 443)
            self.assertTrue((root / 'reports/preprocessing/preprocessing_java443_manifest.json').is_file())

    def test_notebook_calls_shared_pipeline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_sources(root)
            (root / 'recommender').mkdir()
            import shutil
            shutil.copy2(ROOT / 'recommender/data_pipeline.py', root / 'recommender/data_pipeline.py')
            scope = self.run_notebook(root)
            self.assertTrue('result' in scope, 'Notebook must use shared PipelineResult')
            self.assertEqual(len(scope['result'].destinations), 443)
            self.assertEqual(scope['result'].summary['imputed_rating_ids'], [438])

    def test_missing_colab_module_explains_required_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(FileNotFoundError, 'recommender/data_pipeline.py'):
                self.run_notebook(Path(temporary))
