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


def get_order_id():
    # TODO: 主键冲突检测
    dt_now = timezone.localtime(timezone.now())
    rand_int = randint(1000, 9999)
    dt_str = dt_now.strftime('%Y%m%d%H%M%S%f')[:-3]
    return '%s%04d' % (dt_str, rand_int)


class Order(models.Model):
    """
    订单
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

    id = models.CharField(primary_key=True, max_length=64, default=get_order_id, editable=False)
    user = models.ForeignKey(User, verbose_name="用户", related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=191, choices=STATUS_CHOICES)
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

    def __str__(self):
        return f"订单号: {self.id}"

    class Meta:
        verbose_name = verbose_name_plural = "订单"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='订单', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='商品', related_name='+', on_delete=models.SET_NULL, null=True, blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="实际单价", null=False, blank=True)
    quantity = models.IntegerField(verbose_name='数量')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.price is None:
            self.price = self.product.price

        super().save(force_insert, force_update, using, update_fields)

        # 触发order重新计算总价
        self.order.save()

    class Meta:
        verbose_name = verbose_name_plural = "订单项"
