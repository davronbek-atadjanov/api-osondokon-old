from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.order.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price",)
    fields = ("product", "variant", "quantity", "price")


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "user", "business", "status", "is_paid", "payment_method", "total_amount", "created_at")
    list_filter = ("status", "is_paid", "payment_method", "delivery", "platform", "source")
    search_fields = ("user__username", "user__phone_number", "business__name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("user", "business")
    inlines = [OrderItemInline]

    fieldsets = (
        ("Asosiy", {"fields": ("user", "business", "branch", "operator", "source", "platform")}),
        ("To'lov", {"fields": ("payment_method", "is_paid", "total_amount")}),
        ("Yetkazib berish", {"fields": ("delivery", "address")}),
        ("Holat", {"fields": ("status", "comment")}),
        ("Sanalar", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("order", "product", "variant", "quantity", "price")
    search_fields = ("order__id", "product__name_uz")
    list_per_page = 25
    list_select_related = ("order", "product", "variant")
