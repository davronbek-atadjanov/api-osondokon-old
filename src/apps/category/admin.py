from django.contrib import admin
from apps.category.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_tr', 'business', 'parent', 'created_at')
    list_filter = ('business', 'parent', 'created_at')
    search_fields = ('name_uz', 'name_ru', 'name_tr')
    autocomplete_fields = ('parent',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Multi-Language Names', {
            'fields': ('name_uz', 'name_ru', 'name_tr')
        }),
        ('Images', {
            'fields': ('logo', 'picture')
        }),
        ('Relations', {
            'fields': ('business', 'parent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
