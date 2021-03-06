import decimal
from collections import defaultdict
from typing import Optional

import django.db.transaction

from .models import Merchant, Product, MerchantProductsTab, AppImage, Order, OrderItem, UserExpressAddress, OrderStatus, OrderCollection, User
from rest_framework import serializers, exceptions


class AppImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppImage
        fields = (
            'id',
            'width',
            'height',
            'img',
            'desc',
        )
        read_only_fields = (
            'id',
            'width',
            'height',
        )


class MerchantSerializer(serializers.HyperlinkedModelSerializer):
    img = AppImageSerializer()

    class Meta:
        model = Merchant
        fields = (
            'id', 'name', 'img', 'express_limit', 'express_price', 'sales', 'slogan', 'create_at', 'update_at', 'search_keywords'
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
            'search_keywords',
        )


class ProductWithMerchantSerializer(ProductSerializer):
    merchant = MerchantSerializer(read_only=True)


class UserExpressAddressSerializer(serializers.HyperlinkedModelSerializer):
    city = serializers.CharField(required=False)

    def create(self, validated_data):
        creator = self.context['request'].user
        address = UserExpressAddress(
            creator=creator,
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
            city=validated_data.get('city', None),
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
            'city',
            'address_full_txt',
            'create_at',
            'update_at',
        )


# noinspection PyAbstractClass
class OrderUpdateStatusSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.ChoiceField(OrderStatus.STATUS_CHOICES)


# noinspection PyAbstractClass
class OrderCollectionUpdateStatusSerializer(serializers.Serializer):
    order_collection_id = serializers.IntegerField()
    status = serializers.ChoiceField(OrderStatus.STATUS_CHOICES)


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    product_id = serializers.IntegerField()
    product_desc = serializers.SerializerMethodField()
    product_merchant_id = serializers.SerializerMethodField()
    product_merchant_name = serializers.SerializerMethodField()
    product_img = serializers.SerializerMethodField()

    def get_product_desc(self, obj: OrderItem):
        return str(obj.product)

    def get_product_merchant_id(self, obj: OrderItem):
        return obj.product.merchant.id

    def get_product_merchant_name(self, obj: OrderItem):
        return obj.product.merchant.name

    def get_product_img(self, obj: OrderItem):
        if obj.product.img:
            return AppImageSerializer(instance=obj.product.img, context=self.context).data
        else:
            return None

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_id',
            'product_merchant_id',
            'product_merchant_name',
            'product_img',
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
    merchant = MerchantSerializer(read_only=True)
    merchant_id = serializers.IntegerField(required=True)
    address = UserExpressAddressSerializer(read_only=True)
    address_id = serializers.IntegerField(required=True)

    @classmethod
    def create_order(cls, current_user: User, validated_data, order_collection: Optional[OrderCollection] = None):
        if current_user.is_anonymous:
            raise exceptions.PermissionDenied

        address_id = validated_data['address_id']
        merchant_id = validated_data['merchant_id']

        try:
            address = UserExpressAddress.objects.get(pk=address_id)
        except UserExpressAddress.DoesNotExist:
            raise serializers.ValidationError(f"address_id = {address_id} does not exist!")

        try:
            merchant = Merchant.objects.get(pk=merchant_id)
        except Merchant.DoesNotExist:
            raise serializers.ValidationError(f"merchant_id = {merchant_id} does not exist!")

        with django.db.transaction.atomic():
            order = Order.objects.create(
                user=current_user,
                address=address,
                merchant=merchant,
                status=OrderStatus.STATUS_WAITING_TO_PAY,
                price_total=decimal.Decimal('-1'),
                order_collection=order_collection,
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

    def create(self, validated_data):
        user = self.context['request'].user
        return self.create_order(current_user=user, validated_data=validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError('update not implemented')

    class Meta:
        model = Order
        fields = (
            'id',
            'user_id',
            'address',
            'address_id',
            'merchant',
            'merchant_id',
            'status',
            'status_txt',
            'price_total',
            'create_at',
            'update_at',
            'items',
        )
        read_only_fields = (
            'id',
            'address',
            'merchant',
            'status',
            'status_txt',
            'price_total',
        )


class OrderCollectionSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    class Meta:
        model = OrderCollection
        fields = (
            'id',
            'user_id',
            'status',
            'status_txt',
            'orders',
            'price_total',
            'create_at',
            'update_at',
        )
        read_only_fields = (
            'status',
            'status_txt',
            'price_total',
        )

    def create(self, validated_data):
        user = self.context['request'].user

        order_collection = OrderCollection.objects.create(
            user=user,
            status=OrderStatus.STATUS_WAITING_TO_PAY,
            price_total=decimal.Decimal('-1'),
        )

        for _order in validated_data['orders']:
            order = OrderSerializer.create_order(
                current_user=user,
                validated_data=_order,
                order_collection=order_collection
            )

        order_collection.save()

        return order_collection


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5, max_length=20, required=True)
    avatar_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(max_length=191, write_only=True)
    avatar = AppImageSerializer(read_only=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        user_tmp = User.objects.filter(username__iexact=username).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '?????????????????????'})

        avatar = None
        avatar_id = validated_data.get('avatar_id')
        if avatar_id:
            try:
                avatar = AppImage.objects.get(pk=avatar_id)
            except AppImage.DoesNotExist:
                raise serializers.ValidationError({'msg': f'avatar_id = {avatar_id} does not exist!'})

        phone_number = validated_data['phone_number']
        user_tmp = User.objects.filter(phone_number=phone_number).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '??????????????????!'})

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', None),
            first_name=validated_data['first_name'],
            phone_number=validated_data['phone_number'],
            avatar=avatar,
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'phone_number',
            'avatar_id',
            'avatar',
            'password',
        )
        read_only_fields = (
            'id',
            'avatar',
        )


class SearchSerializer(serializers.Serializer):
    s = serializers.CharField(min_length=1, max_length=191)
    merchant_id = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50, required=False)
    type = serializers.ChoiceField(choices=(
        ('all', '??????'),
        ('merchant', '??????'),
        ('product', '??????'),
    ))

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def do_search(self, validated_data):
        _type = validated_data['type']
        s = validated_data['s']
        merchant_id = validated_data.get('merchant_id')
        limit = validated_data['limit']

        products = []
        merchants = []

        if _type == 'merchant' or _type == 'all':
            for m in Merchant.objects.select_related('img').filter(search_keywords__icontains=s)[:limit]:
                merchants.append(m)
        if _type == 'product' or _type == 'all':
            qs = Product.objects.select_related('merchant', 'img').filter(search_keywords__icontains=s)
            if isinstance(merchant_id, int):
                qs = qs.filter(merchant_id=merchant_id)
            for p in qs[:limit]:
                products.append(p)

        return {
            's': s,
            'type': _type,
            'limit': limit,
            'products': ProductWithMerchantSerializer(instance=products, many=True, context=self.context).data,
            'merchants': MerchantSerializer(instance=merchants, many=True, context=self.context).data,
        }


class MerchantSearchSerializer(serializers.Serializer):
    s = serializers.CharField(min_length=1, max_length=191)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def do_search(self, validated_data):
        s = validated_data['s']
        limit = validated_data['limit']

        qs = Product.objects.filter(search_keywords__icontains=s).values_list('id', 'merchant_id')

        ret = defaultdict(list)

        product_id_set = set()
        for product_id, merchant_id in qs:
            if merchant_id in ret:
                product_id_set.add(product_id)
                ret[merchant_id].append(product_id)
            else:
                if len(ret) == limit:
                    break
                else:
                    product_id_set.add(product_id)
                    ret[merchant_id].append(product_id)

        merchant_dict = {
            m.id: m for m in Merchant.objects.filter(id__in=ret.keys())
        }

        product_dict = {
            p.id: p for p in Product.objects.filter(id__in=product_id_set)
        }

        search_result = [
            {
                "merchant": merchant_dict[merchant_id],
                "products": [product_dict[_p_id] for _p_id in product_id_list]
            } for merchant_id, product_id_list in ret.items()
        ]

        # serialize
        for item in search_result:
            item['merchant'] = MerchantSerializer(instance=item['merchant'], context=self.context).data
            for idx in range(len(item['products'])):
                item['products'][idx] = ProductSerializer(instance=item['products'][idx], context=self.context).data

        # search for merchant that names contains keywords and not hit by products
        qs = Merchant.objects.filter(search_keywords__icontains=s).exclude(id__in=merchant_dict.keys()).all()
        search_result_merchants = []
        for m in qs:
            search_result_merchants.append({
                "merchant": MerchantSerializer(instance=m, context=self.context).data,
                "products": [],
            })
        if len(search_result_merchants) > 0:
            search_result = [
                *search_result_merchants,
                *search_result,
            ]

        return {
            's': s,
            'limit': limit,
            'search_result': search_result
        }
