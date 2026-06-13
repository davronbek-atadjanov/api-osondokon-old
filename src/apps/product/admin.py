from django.contrib import admin
from apps.product.models import Product, ProductVariant

admin.site.register(
    [Product, ProductVariant]
)
