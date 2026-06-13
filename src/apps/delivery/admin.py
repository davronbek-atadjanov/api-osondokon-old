from django.contrib import admin
from apps.delivery.models import DeliveryMethod, PickupMethod

admin.site.register(
    [DeliveryMethod, PickupMethod]
)
