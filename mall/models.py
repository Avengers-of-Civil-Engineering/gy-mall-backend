import decimal

from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from random import randint


class AppImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    img = models.ImageField(width_field='width', height_field='height')
    desc = models.CharField(max_length=191, blank=True, null=False, verbose_name="图片备注")

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.img.name

    class Meta:
        verbose_name = verbose_name_plural = '图片'


class User(AbstractUser):
    phone_number = models.CharField(max_length=191, blank=True, null=True, verbose_name="手机号码", unique=True)
    avatar = models.ForeignKey(AppImage, on_delete=models.SET_NULL, db_constraint=False, null=True, blank=True)


class UserExpressAddress(models.Model):
    """
    收货地址
    """
    creator = models.ForeignKey('mall.User', on_delete=models.SET_NULL, null=True, blank=False, verbose_name='创建者')
    name = models.CharField(max_length=191, blank=False, null=False, verbose_name='收货人姓名')
    phone_number = models.CharField(max_length=191, blank=False, null=False, verbose_name='收货人手机号')
    address_full_txt = models.TextField(verbose_name='收货人地址')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} {self.phone_number} {self.address_full_txt}'

    class Meta:
        verbose_name = verbose_name_plural = '收货地址'


class Merchant(models.Model):
    """
    商户
    """

    name = models.CharField(max_length=191, verbose_name="商户名")
    img = models.ForeignKey(AppImage, related_name='+', db_constraint=False, on_delete=models.SET_NULL, null=True, blank=True)

    express_limit = models.IntegerField(verbose_name='起送运费', default=0)
    express_price = models.IntegerField(verbose_name='基础运费', default=0)

    sales = models.IntegerField(verbose_name='销量', default=0)

    slogan = models.CharField(max_length=191, blank=True, verbose_name='促销文字说明')

    rank = models.IntegerField(verbose_name='排序(大->小)', default=999, db_index=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        tab_all = self.tabs.filter(slug='all').first()
        if tab_all is None:
            tab = MerchantProductsTab(
                merchant=self,
                name='全部',
                slug='all',
                rank=9999
            )
            tab.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-rank',)
        verbose_name = verbose_name_plural = "商户"


class MerchantProductsTab(models.Model):
    """
    商户的商品类目
    """
    merchant = models.ForeignKey(Merchant, related_name='tabs', on_delete=models.CASCADE, verbose_name='商户')
    name = models.CharField(max_length=191, verbose_name="类目名")
    slug = models.CharField(max_length=191, verbose_name='slug')
    rank = models.IntegerField(verbose_name='排序(大->小)', default=999, db_index=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.merchant.name}: {self.name}"

    class Meta:
        verbose_name = verbose_name_plural = "类目"
        ordering = ('-rank',)
        constraints = (
            models.UniqueConstraint(fields=['merchant', 'slug'], name='unique-merchant-slug'),
        )


class Product(models.Model):
    merchant = models.ForeignKey(Merchant, related_name='products', on_delete=models.CASCADE, verbose_name='商户')
    tab = models.ForeignKey(MerchantProductsTab, related_name='products', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属类目')
    img = models.ForeignKey(AppImage, related_name='+', db_constraint=False, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=191, verbose_name="商品名")
    unit_desc = models.CharField(max_length=191, verbose_name="单位文字", blank=True, null=False)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="初始单价")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="当前单价")
    sales = models.IntegerField(verbose_name='销量', default=0)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.unit_desc:
            return f'{self.name} {self.unit_desc}'
        else:
            return self.name

    class Meta:
        verbose_name = verbose_name_plural = "商品"


ID_GENERATE_RETRY_CNT = 10
local_order_id_set = set()


def get_order_id():
    # TODO: 跨进程主键冲突检测

    if len(local_order_id_set) >= 10000:  # 防一手内存泄漏
        local_order_id_set.clear()

    for i in range(ID_GENERATE_RETRY_CNT):
        dt_now = timezone.localtime(timezone.now())
        rand_int = randint(1000, 9999)
        dt_str = dt_now.strftime('%Y%m%d%H%M%S%f')[:-3]
        candidate = '%s%04d' % (dt_str, rand_int)
        if candidate in local_order_id_set:
            continue
        else:
            local_order_id_set.add(candidate)
            return candidate
    raise RuntimeError(f"get_order_id fail, retry more than {ID_GENERATE_RETRY_CNT} times")


class OrderStatus:
    """
    订单状态
    """
    STATUS_CREATING = 'creating'
    STATUS_WAITING_TO_PAY = 'waiting_to_pay'
    STATUS_PAID_SUCCEED = 'paid_succeed'
    STATUS_UNPAID_CLOSED = 'unpaid_closed'
    STATUS_SENDING = 'sending'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = (
        (STATUS_CREATING, '创建中'),
        (STATUS_WAITING_TO_PAY, '待支付'),
        (STATUS_PAID_SUCCEED, '支付成功'),
        (STATUS_UNPAID_CLOSED, '未支付关闭'),
        (STATUS_SENDING, '快递发送中'),
        (STATUS_FINISHED, '已完成'),
    )


class OrderCollection(models.Model):
    """
    订单集合, 用于购物车一次性下单好几家店铺的情况
    """
    id = models.CharField(primary_key=True, max_length=64, default=get_order_id, editable=False)
    user = models.ForeignKey(User, verbose_name="用户", related_name='order_collections', on_delete=models.CASCADE)
    status = models.CharField(max_length=191, choices=OrderStatus.STATUS_CHOICES)
    price_total = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="订单总价", blank=True, null=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        acc = decimal.Decimal(0.0)
        for order in self.orders.all():
            acc = acc + order.price_total
        self.price_total = acc

        super().save(force_insert, force_update, using, update_fields)
        self.orders.update(status=self.status)


class Order(models.Model):
    """
    订单
    """
    id = models.CharField(primary_key=True, max_length=64, default=get_order_id, editable=False)
    user = models.ForeignKey(User, verbose_name="用户", related_name='orders', on_delete=models.CASCADE)
    order_collection = models.ForeignKey('mall.OrderCollection', verbose_name='订单集合',
                                         null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    merchant = models.ForeignKey('mall.Merchant', verbose_name='商户', blank=True, null=True, on_delete=models.SET_NULL, related_name='+')
    address = models.ForeignKey('mall.UserExpressAddress', verbose_name='收货地址', related_name='+', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=191, choices=OrderStatus.STATUS_CHOICES)
    price_total = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="订单总价", blank=True, null=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # 重新计算总价
        acc = decimal.Decimal(0.0)
        for item in self.items.all():
            acc = acc + (item.price * item.quantity)
        self.price_total = acc

        super().save(force_insert, force_update, using, update_fields)

        if self.order_collection is not None:
            self.order_collection.save()

    def __str__(self):
        return f"订单号: {self.id}"

    class Meta:
        verbose_name = verbose_name_plural = "订单"
        ordering = ("-create_at",)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='订单', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='商品', related_name='+', on_delete=models.SET_NULL, null=True, blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="实际单价", null=False, blank=True)
    quantity = models.IntegerField(verbose_name='数量')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        注意: 为了避免order_item创建时反复触发order的save, order创建时order_item应该采用 object.create 的方式
        """
        if self.price is None:
            self.price = self.product.price

        super().save(force_insert, force_update, using, update_fields)

        # 触发order重新计算总价
        self.order.save()

    class Meta:
        verbose_name = verbose_name_plural = "订单项"
