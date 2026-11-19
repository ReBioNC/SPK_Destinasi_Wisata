from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from recommender.data_pipeline import TOTAL_DESTINATIONS, build_pipeline, export_pipeline


class Command(BaseCommand):
    help = 'Preprocessing bersama: pertahankan seluruh destinasi Jawa dan ekspor manifest.'

    def add_arguments(self, parser):
        parser.add_argument('--project-root', default=str(Path(__file__).resolve().parents[3]))

    def handle(self, *args, **options):
        root = Path(options['project_root'])
        try:
            result = build_pipeline(root)
            paths = export_pipeline(result, root)
        except (ValueError, FileNotFoundError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write(f'{TOTAL_DESTINATIONS} destinasi; 437 Kaggle + {TOTAL_DESTINATIONS - 437} kurasi; tidak ada ID hilang.')
        for name, path in paths.items():
            self.stdout.write(f'{name}: {path}')
