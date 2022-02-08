import json
import os
from pprint import pprint
from typing import List

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
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


class TestOrderAPI(APITestCase):
    def setUp(self) -> None:
        generate_mock_data()
        self.client.login(username='aweffr', password='unsafe')

    def test_order_create(self):
        from .models import User, Merchant, UserExpressAddress, Product

        u = User.objects.get(username='aweffr')
        m = Merchant.objects.get(name='沃尔玛')

        address = UserExpressAddress.objects.filter(creator=u).first()

        products: List[Product] = list(Product.objects.filter(merchant=m).all())

        url = reverse('order-list')

        items = [
            {'product_id': p.id, 'quantity': idx + 1}
            for idx, p in enumerate(products)
        ]

        data = {
            'address_id': address.id,
            'items': items
        }

        print("POST url=", url)
        print("POST data=", json.dumps(data, indent=2, ensure_ascii=False))
        resp = self.client.post(url, data, format='json')

        ret_data = json.dumps(resp.data, indent=2, ensure_ascii=False)

        print("POST data return:", ret_data)

        self.assertEqual(resp.data['user_id'], 1)
        self.assertEqual(resp.data['address']['address_full_txt'], "太阳市月亮村起飞起飞")
