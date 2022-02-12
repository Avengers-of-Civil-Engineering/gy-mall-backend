import json
import os
from pprint import pprint
from typing import List

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import AppImage, Order, OrderStatus
from .generate_mock_data import generate_mock_data
from random import shuffle


# Create your tests here.
class TestGenerateMockData(TestCase):
    def test_generate(self):
        generate_mock_data()

    def tearDown(self) -> None:
        for image in AppImage.objects.all():
            print(f'removing {image.img.path}')
            os.remove(image.img.path)


def _generate_test_order_by_merchant(username, merchant_name):
    from .models import User, Merchant, UserExpressAddress, Product
    u = User.objects.get(username=username)
    m = Merchant.objects.get(name=merchant_name)
    address = UserExpressAddress.objects.filter(creator=u).first()

    products: List[Product] = list(Product.objects.filter(merchant=m).all())
    shuffle(products)
    products = products[:2]

    items = [
        {'product_id': p.id, 'quantity': idx + 1}
        for idx, p in enumerate(products)
    ]

    payload = {
        'address_id': address.id,
        'merchant_id': m.id,
        'items': items
    }
    return payload


class TestOrderAPI(APITestCase):
    def setUp(self) -> None:
        generate_mock_data()
        self.client.login(username='aweffr', password='unsafe')

    def test_order_create(self):
        payload = _generate_test_order_by_merchant(username='aweffr', merchant_name='沃尔玛')
        url = reverse('order-list')
        print("POST url=", url)
        print("POST data=", json.dumps(payload, indent=2, ensure_ascii=False))
        resp = self.client.post(url, payload, format='json')

        ret_data = json.dumps(resp.data, indent=2, ensure_ascii=False)

        print("POST data return:", ret_data)

        self.assertEqual(resp.data['user_id'], 1)
        self.assertEqual(resp.data['address']['address_full_txt'], "太阳市月亮村起飞起飞")
        order_id = resp.data['id']
        print(f"order_id = {order_id}")
        self.assertEqual(len(order_id), 21)

        data_update_status = {
            'order_id': order_id,
            'status': OrderStatus.STATUS_PAID_SUCCEED,
        }
        url2 = reverse('order-update-status', kwargs={'pk': order_id})
        print("POST url2=", url2, 'payload=', json.dumps(data_update_status, indent=2, ensure_ascii=False))
        resp2 = self.client.post(url2, data_update_status, format='json')
        print("POST url2 data return:", json.dumps(resp2.data, indent=2, ensure_ascii=False))
        self.assertEqual(resp2.data['status'], OrderStatus.STATUS_PAID_SUCCEED)

    def tearDown(self) -> None:
        for image in AppImage.objects.all():
            print(f'removing {image.img.path}')
            os.remove(image.img.path)


class TestOrderCollectionAPI(APITestCase):
    def setUp(self) -> None:
        generate_mock_data()
        self.client.login(username='aweffr', password='unsafe')

    def test_order_collection_create(self):
        from .models import User, Merchant, UserExpressAddress, Product
        u = User.objects.get(username='aweffr')
        order1 = _generate_test_order_by_merchant(username='aweffr', merchant_name='沃尔玛')
        order2 = _generate_test_order_by_merchant(username='aweffr', merchant_name='山姆会员店')
        url = reverse("ordercollection-list")

        payload = {
            'user_id': u.id,
            'orders': [
                order1,
                order2,
            ]
        }
        print("POST url=", url)
        print("POST data=", json.dumps(payload, indent=2, ensure_ascii=False))
        resp = self.client.post(url, payload, format='json')

        ret_data = json.dumps(resp.data, indent=2, ensure_ascii=False)

        print("POST data return:", ret_data)
        order_collection_id = resp.data['id']

        url2 = reverse('ordercollection-update-status', kwargs={'pk': order_collection_id})
        data_update_status = {
            'order_collection_id': order_collection_id,
            'status': OrderStatus.STATUS_PAID_SUCCEED,
        }
        print("POST url2=", url2, 'payload=', json.dumps(data_update_status, indent=2, ensure_ascii=False))
        resp2 = self.client.post(url2, data_update_status, format='json')
        print("POST url2 data return:", json.dumps(resp2.data, indent=2, ensure_ascii=False))
        self.assertEqual(resp2.data['status'], OrderStatus.STATUS_PAID_SUCCEED)

    def tearDown(self) -> None:
        for image in AppImage.objects.all():
            print(f'removing {image.img.path}')
            os.remove(image.img.path)


class TestAddressAPI(APITestCase):
    def setUp(self) -> None:
        generate_mock_data()
        self.client.login(username='aweffr', password='unsafe')

    def test_address_create(self):
        url = reverse('userexpressaddress-list')

        data = {
            "name": "小浣熊",
            "phone_number": "123456890",
            "city": "宇宙",
            "address_full_txt": "太阳市月球村村长之家的楼梯间"
        }
        print("POST url=", url)
        print("POST data=", json.dumps(data, indent=2, ensure_ascii=False))
        resp = self.client.post(url, data, format='json')
        print("POST data return:", json.dumps(resp.data, indent=2, ensure_ascii=False))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)



class TestUserAPI(APITestCase):

    def setUp(self) -> None:
        generate_mock_data()

    def test_register_user(self):
        url = reverse('user-list')

        data = {
            'username': 'test111',
            'email': 'test111@aweffr.com',
            'first_name': '小浣熊',
            'phone_number': '1588888888',
            'password': 'unsafe',
        }

        print("POST url=", url)
        print("POST data=", json.dumps(data, indent=2, ensure_ascii=False))
        resp = self.client.post(url, data, format='json')
        print("POST data return:", json.dumps(resp.data, indent=2, ensure_ascii=False))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


        self.client.login(username='test111', password='unsafe')

        url2 = reverse('user-detail', kwargs={'username': 'test111'})
        print("POST url2=", url2)
        resp2 = self.client.get(url2, format='json')
        print("POST data return:", json.dumps(resp2.data, indent=2, ensure_ascii=False))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)








