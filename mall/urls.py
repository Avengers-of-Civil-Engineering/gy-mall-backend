from pprint import pprint

from django.urls import include, path
from rest_framework.authtoken import views as authtoken_views

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'merchants', views.MerchantViewSet)
router.register(r'merchant-products-tabs', views.MerchantProductsTabViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-collections', views.OrderCollectionViewSet)
router.register(r'addresses', views.UserExpressAddressViewSet)

pprint(router.get_urls())

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', authtoken_views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
