from rest_framework import authentication
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework import exceptions

from .models import Merchant, MerchantProductsTab, Product, Order, UserExpressAddress, OrderCollection, User, AppImage
from .serializers import MerchantSerializer, MerchantProductsTabSerializer, ProductSerializer, OrderSerializer, OrderUpdateStatusSerializer, \
    UserExpressAddressSerializer, OrderCollectionSerializer, OrderCollectionUpdateStatusSerializer, UserSerializer, SearchSerializer, \
    AppImageSerializer, MerchantSearchSerializer


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


class AllowPostByAnyOne(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        else:
            return bool(request.user and request.user.is_authenticated)


class UserViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        AllowPostByAnyOne,
    )

    lookup_field = 'username'

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request: Request, *args, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied

        user_obj: User = self.get_object()
        if user_obj.id != request.user.id:
            raise exceptions.PermissionDenied

        return super().retrieve(request, *args, **kwargs)

    @action(methods=['GET', ], detail=False)
    def about_me(self, request: Request, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied
        return Response(UserSerializer(instance=request.user, context={'request': request}).data)


class AppImageViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = AppImage.objects.all()
    serializer_class = AppImageSerializer


class SearchAPI(APIView):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get(self, request: Request):
        search_serializer = SearchSerializer(data=request.query_params, context={'request': request})
        if search_serializer.is_valid(raise_exception=True):
            search_result = search_serializer.do_search(search_serializer.validated_data)
            return Response(search_result)


class SearchMerchantAPI(APIView):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    def get(self, request: Request):
        serializer = MerchantSearchSerializer(data=request.query_params, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            search_result = serializer.do_search(serializer.validated_data)
            return Response(search_result)


class MyObtainAuthTokenAPI(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(instance=user, context={'request': request}).data,
        })
