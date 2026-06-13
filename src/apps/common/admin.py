from django.contrib import admin
from unfold.admin import ModelAdmin  # noqa


class BaseAdmin(ModelAdmin):
    """
    Unfold admin formalarini barcha admin panellarga avtomatik tatbiq qilish
    """
    list_per_page = 25  # Sahifadagi obyektlar soni
    search_help_text = "Qidirish uchun kalit so‘z kiriting"

    # Barcha formalarga umumiy CSS sinflari qo‘shish
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'description')
        }),
    )

