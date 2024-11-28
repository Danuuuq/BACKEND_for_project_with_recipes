import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle(self, *args, **kwargs):

        data_dir = settings.BASE_DIR / 'data'

        self.import_data(data_dir / 'ingredients.csv',
                         Ingredient, ['name', 'measurement_unit'])

    def import_data(self, file_path, model, fields):
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = {field: row[field] for field in fields}
                model.objects.get_or_create(**data)
        self.stdout.write(self.style.SUCCESS('Successfully loaded'
                                             f'data from {file_path}'))
