from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.delivery.models import DeliveryMethod, PickupMethod


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(ModelAdmin):
    list_display = ("business", "type", "is_active", "price", "max_km")
    list_filter = ("type", "is_active")
    search_fields = ("business__name",)
    list_per_page = 25
    list_select_related = ("business",)

    fieldsets = (
        ("Asosiy", {"fields": ("business", "type", "is_active")}),
        ("Narx", {"fields": ("price", "initial_km", "initial_km_price", "every_km_price", "min_price")}),
        ("Geografiya", {"fields": ("max_km", "country", "cities")}),
        ("Qo'shimcha", {"fields": ("description", "estimated_shipping_time", "branches")}),
    )


@admin.register(PickupMethod)
class PickupMethodAdmin(ModelAdmin):
    list_display = ("business",)
    search_fields = ("business__name",)
    list_per_page = 25
    list_select_related = ("business",)
