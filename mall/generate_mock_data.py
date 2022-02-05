import decimal
import os
from pathlib import Path

from django.conf import settings
from django.core.files.images import ImageFile
from .models import (
    AppImage, User, Merchant, MerchantProductsTab, Product, Order, OrderItem
)


def get_image_file(path: Path):
    cwd = Path(os.getcwd())
    relative_path = path.relative_to(cwd)
    return ImageFile(open(relative_path, 'rb'))


def get_default_image():
    try:
        avatar = AppImage.objects.get(desc="默认图片")
    except AppImage.DoesNotExist:
        avatar = AppImage.objects.create(
            img=get_image_file(settings.BASE_DIR / 'doc' / 'imgs' / 'heibei.png'),
            desc='默认图片'
        )
    return avatar


def gen_users():
    avatar = get_default_image()

    u1, _ = User.objects.get_or_create(username='aweffr')
    u1.avatar = avatar
    u1.set_password(os.getenv('MOCK_PASS', 'unsafe'))
    u1.phone_number = '15086886666'
    u1.is_superuser = u1.is_staff = True
    u1.save()

    u2, _ = User.objects.get_or_create(username='guying')
    u2.avatar = avatar
    u2.set_password(os.getenv('MOCK_PASS', 'unsafe'))
    u2.phone_number = '15086886667'
    u2.is_superuser = u2.is_staff = True
    u2.save()


def gen_merchants():
    avatar = get_default_image()

    m1, _ = Merchant.objects.get_or_create(name='沃尔玛')
    m1.img = avatar
    m1.express_limit = 0
    m1.express_price = 5
    m1.sales = 10000
    m1.slogan = '一刀满级'
    m1.save()

    m2, _ = Merchant.objects.get_or_create(name='山姆会员店')
    m2.img = avatar
    m2.express_limit = 0
    m2.express_price = 5
    m2.sales = 10000
    m2.slogan = '开局满装备'
    m2.save()


tabs_dict = [
    {'name': '电子', 'slug': 'electronic'},
    {'name': '新鲜水果', 'slug': 'fruit'},
]


def gen_merchant_tabs():
    m1 = Merchant.objects.get(name="沃尔玛")
    m2 = Merchant.objects.get(name="山姆会员店")

    for m in (m1, m2):
        for tab_raw in tabs_dict:
            tab, _ = MerchantProductsTab.objects.get_or_create(
                merchant=m,
                name=tab_raw['name'],
                slug=tab_raw['slug'],
            )


products_dict = [
    {
        'name': '任天堂Switch日版游戏机续航加强版',
        'unit_desc': '',
        'img': settings.BASE_DIR / "doc" / "imgs" / "product-switch.png",
        'img_desc': 'Switch 样品图',
        'tab': '电子',
        'price': decimal.Decimal("2529.0"),
        'old_price': decimal.Decimal("3088.0"),
    },
    {
        'name': '索尼ps5国行版游戏机主机',
        'unit_desc': '',
        'img': settings.BASE_DIR / "doc" / "imgs" / "product-ps5.png",
        'img_desc': 'ps5 样品图',
        'tab': '电子',
        'price': decimal.Decimal("4699.0"),
        'old_price': decimal.Decimal("5299.0"),
    },
    {
        'name': '番茄',
        'unit_desc': '250g / 份',
        'img': settings.BASE_DIR / "doc" / "imgs" / "product-tomato.png",
        'img_desc': '番茄 样品图',
        'tab': '新鲜水果',
        'price': decimal.Decimal("33.6"),
        'old_price': decimal.Decimal("45.3"),
    },
    {
        'name': '车厘子',
        'unit_desc': '500g / 份',
        'img': settings.BASE_DIR / "doc" / "imgs" / "product-cherry.png",
        'img_desc': '车厘子 样品图',
        'tab': '新鲜水果',
        'price': decimal.Decimal("99.6"),
        'old_price': decimal.Decimal("128.3"),
    },
    {
        'name': '橙子',
        'unit_desc': '250g / 份',
        'img': settings.BASE_DIR / "doc" / "imgs" / "product-orange.png",
        'img_desc': '橙子 样品图',
        'tab': '新鲜水果',
        'price': decimal.Decimal("12.6"),
        'old_price': decimal.Decimal("22.4"),
    },
]


def gen_products():
    m1 = Merchant.objects.get(name="沃尔玛")
    m2 = Merchant.objects.get(name="山姆会员店")

    for m in (m1, m2):
        for p_raw in products_dict:
            tab = MerchantProductsTab.objects.get(merchant=m, name=p_raw['tab'])
            p = Product.objects.filter(merchant=m, name=p_raw['name']).first()
            if p is None:
                p = Product.objects.create(
                    merchant=m,
                    name=p_raw['name'],
                    old_price=p_raw['old_price'],
                    price=p_raw['price'],
                )
            p.unit_desc = p_raw['unit_desc']
            try:
                p.img = AppImage.objects.get(desc=p_raw['img_desc'])
            except AppImage.DoesNotExist:
                p.img = AppImage.objects.create(
                    img=get_image_file(p_raw['img']),
                    desc=p_raw['img_desc'],
                )
            p.old_price = p_raw['old_price']
            p.price = p_raw['price']
            p.tab = tab
            p.save()


def generate_mock_data():
    """
    生成mock数据, 入口
    """

    gen_users()

    gen_merchants()

    gen_merchant_tabs()

    gen_products()
