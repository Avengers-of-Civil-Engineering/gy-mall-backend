from pprint import pprint

from django.urls import include, path
from rest_framework.authtoken import views as authtoken_views

from rest_framework import routers
from . import views
from .views import SearchAPI, MyObtainAuthTokenAPI, SearchMerchantAPI

router = routers.DefaultRouter()
router.register(r'merchants', views.MerchantViewSet)
router.register(r'merchant-products-tabs', views.MerchantProductsTabViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-collections', views.OrderCollectionViewSet)
router.register(r'addresses', views.UserExpressAddressViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'images', views.AppImageViewSet)

pprint(router.get_urls())

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SearchAPI.as_view(), name="search"),
    path('search-merchant/', SearchMerchantAPI.as_view(), name="search-merchant"),
    path('api-token-auth/', MyObtainAuthTokenAPI.as_view(), name="token_login"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
