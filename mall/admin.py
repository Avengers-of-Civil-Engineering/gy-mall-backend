from django.contrib import admin

from .models import OrderItem
from .models import Merchant, Product, MerchantProductsTab, AppImage, Order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class ReportAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(MerchantProductsTab)
class MerchantProductsTabAdmin(admin.ModelAdmin):
    pass


@admin.register(AppImage)
class AppImageAdmin(admin.ModelAdmin):
    pass
