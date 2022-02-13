from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from mall.models import Product, Merchant
        for p in Product.objects.all():
            p.init_keywords()
            p.save(init_keywords_called=True)
        for m in Merchant.objects.all():
            m.init_keywords()
            m.save(init_keywords_called=True)
