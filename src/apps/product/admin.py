from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.product.models import Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("combination", "price", "discount", "sale_price", "stock", "is_active")


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name_uz", "business", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "business", "category")
    search_fields = ("name_uz", "name_ru", "business__name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("business", "category")
    inlines = [ProductVariantInline]

    fieldsets = (
        ("Ko'p tilli nomlar", {"fields": ("name_uz", "name_ru", "name_tr")}),
        ("Tavsif", {
            "fields": (
                "short_description_uz", "short_description_ru",
                "description_uz", "description_ru",
            ),
            "classes": ("collapse",),
        }),
        ("Bog'liqliklar", {"fields": ("business", "category")}),
        ("Narx va inventar", {"fields": ("price", "stock", "order_count", "is_active")}),
        ("Media", {"fields": ("images",)}),
        ("Atributlar", {"fields": ("attributes", "attributes_images", "features"), "classes": ("collapse",)}),
        ("Sanalar", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    list_display = ("product", "combination", "price", "sale_price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__name_uz",)
    list_per_page = 25
    list_select_related = ("product",)
