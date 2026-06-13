from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.category.models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name_uz", "name_ru", "name_tr", "business", "parent", "created_at")
    list_filter = ("business", "parent", "created_at")
    search_fields = ("name_uz", "name_ru", "name_tr")
    autocomplete_fields = ("parent",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("business", "parent")

    fieldsets = (
        ("Ko'p tilli nomlar", {"fields": ("name_uz", "name_ru", "name_tr")}),
        ("Rasmlar", {"fields": ("logo", "picture")}),
        ("Bog'liqliklar", {"fields": ("business", "parent")}),
        ("Sanalar", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
