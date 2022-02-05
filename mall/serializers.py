from .models import Merchant, Product, MerchantProductsTab, AppImage, Order, OrderItem
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
