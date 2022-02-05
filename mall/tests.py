import os
from django.test import TestCase
from .models import AppImage
from .generate_mock_data import generate_mock_data


# Create your tests here.
class TestGenerateMockData(TestCase):
    def test_generate(self):
        generate_mock_data()

    def tearDown(self) -> None:
        for image in AppImage.objects.all():
            print(f'removing {image.img.path}')
            os.remove(image.img.path)
