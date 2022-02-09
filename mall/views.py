from rest_framework import authentication
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins

from .models import Merchant, MerchantProductsTab, Product, Order, UserExpressAddress, OrderCollection
from .serializers import MerchantSerializer, MerchantProductsTabSerializer, ProductSerializer, OrderSerializer, OrderUpdateStatusSerializer, \
    UserExpressAddressSerializer, OrderCollectionSerializer, OrderCollectionUpdateStatusSerializer


class MerchantViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

    def get_serializer_class(self):
        if self.action == 'products':
            return ProductSerializer
        elif self.action == 'tabs':
            return MerchantProductsTabSerializer
        return super(MerchantViewSet, self).get_serializer_class()

    @action(detail=True, methods=['get', ])
    def tabs(self, request: Request, pk=None):
        merchant = self.get_object()
        qs = MerchantProductsTab.objects.filter(merchant=merchant).all()
        return Response(
            MerchantProductsTabSerializer(
                instance=qs.all(),
                many=True,
                context={'request': request}
            ).data
        )

    @action(detail=True, methods=['get', ])
    def products(self, request: Request, pk=None):
        merchant = self.get_object()
        qs = Product.objects.select_related('merchant', 'tab').filter(merchant=merchant)
        tab_param = request.query_params.get('tab')
        if tab_param and tab_param != 'all':
            qs = qs.filter(tab__slug__iexact=tab_param)
        return Response(ProductSerializer(instance=qs.all(), many=True, context={'request': request}).data)


class MerchantProductsTabViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    queryset = MerchantProductsTab.objects.all()
    serializer_class = MerchantProductsTabSerializer


class ProductViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    filterset_fields = ['merchant', 'tab']

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = Order.objects.prefetch_related(
        'items',
        'items__product',
        'items__product__merchant',
        'items__product__img'
    ).all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

    @action(methods=['POST', ], detail=True)
    def update_status(self, request: Request, pk=None):
        order: Order = self.get_object()
        serializer = OrderUpdateStatusSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            order.status = serializer.validated_data['status']
            order.save()
        return Response(OrderSerializer(instance=order, context={'request': request}).data)


class UserExpressAddressViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = UserExpressAddress.objects.all()
    serializer_class = UserExpressAddressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(creator=self.request.user)
        return qs


class OrderCollectionViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = OrderCollection.objects.all()
    serializer_class = OrderCollectionSerializer

    @action(methods=['POST', ], detail=True)
    def update_status(self, request: Request, pk=None):
        order_collection: OrderCollection = self.get_object()
        serializer = OrderCollectionUpdateStatusSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            order_collection.status = serializer.validated_data['status']
            order_collection.save()
        return Response(OrderCollectionSerializer(instance=order_collection, context={'request': request}).data)
