import decimal

import django.db.transaction

from .models import Merchant, Product, MerchantProductsTab, AppImage, Order, OrderItem, UserExpressAddress
from rest_framework import serializers


class AppImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppImage
        fields = (
            'width',
            'height',
            'img',
            'desc',
        )


class MerchantSerializer(serializers.HyperlinkedModelSerializer):
    img = AppImageSerializer()

    class Meta:
        model = Merchant
        fields = (
            'id', 'name', 'img', 'express_limit', 'express_price', 'sales', 'slogan', 'create_at', 'update_at'
        )


class MerchantProductsTabSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MerchantProductsTab
        fields = (
            'id', 'merchant', 'name', 'slug', 'rank'
        )


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    img = AppImageSerializer()

    tab_slug = serializers.SerializerMethodField()

    def get_tab_slug(self, obj: Product):
        return obj.tab.slug

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'merchant',
            'tab',
            'tab_slug',
            'img',
            'unit_desc',
            'old_price',
            'price',
            'sales',
            'create_at',
            'update_at',
        )


class UserExpressAddressSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        creator = self.context['request'].user
        address = UserExpressAddress(
            creator=creator,
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            address_full_txt=validated_data['address_full_txt'],
        )
        address.save()
        return address

    class Meta:
        model = UserExpressAddress
        fields = (
            'id',
            'creator_id',
            'name',
            'phone_number',
            'address_full_txt',
            'create_at',
            'update_at',
        )


# noinspection PyAbstractClass
class OrderUpdateStatusSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.ChoiceField(Order.STATUS_CHOICES)


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    product_id = serializers.IntegerField()
    product_desc = serializers.SerializerMethodField()
    product_merchant_id = serializers.SerializerMethodField()
    product_merchant_name = serializers.SerializerMethodField()

    def get_product_desc(self, obj: OrderItem):
        return str(obj.product)

    def get_product_merchant_id(self, obj: OrderItem):
        return obj.product.merchant.id

    def get_product_merchant_name(self, obj: OrderItem):
        return obj.product.merchant.name

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_id',
            'product_merchant_id',
            'product_merchant_name',
            'product_desc',  # read only
            'price',
            'quantity',
        )
        read_only_fields = (
            'product_desc',
            'price',
        )


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    items = OrderItemSerializer(many=True)
    address = UserExpressAddressSerializer(read_only=True)
    address_id = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context['request'].user
        with django.db.transaction.atomic():
            order = Order.objects.create(
                user=user,
                address_id=validated_data['address_id'],
                status=Order.STATUS_WAITING_TO_PAY,
                price_total=decimal.Decimal('-1'),
            )
            for item in validated_data['items']:
                product = Product.objects.get(pk=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item['quantity']
                )
            order.save()

            return order

    def update(self, instance, validated_data):
        raise NotImplementedError('update not implemented')

    class Meta:
        model = Order
        fields = (
            'id',
            'user_id',
            'address',
            'address_id',
            'status',
            'price_total',
            'create_at',
            'update_at',
            'items',
        )
        read_only_fields = (
            'id',
            'address',
            'status',
            'price_total',
        )
