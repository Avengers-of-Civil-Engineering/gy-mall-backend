from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework import authentication
from .models import Merchant, MerchantProductsTab, Product
from .serializers import AppImageSerializer, MerchantSerializer, MerchantProductsTabSerializer, ProductSerializer


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
        if request.query_params.get('tab'):
            qs = qs.filter(tab__slug__iexact=request.query_params.get('tab'))
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
