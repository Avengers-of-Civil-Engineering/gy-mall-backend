from django.core.management.base import BaseCommand
from mall.generate_mock_data import generate_mock_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_mock_data()
