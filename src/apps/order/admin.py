from django.contrib import admin
from apps.order.models import Order, OrderItem

admin.site.register(
    [Order, OrderItem]
)
