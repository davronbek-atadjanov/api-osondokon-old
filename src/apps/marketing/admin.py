from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.marketing.models import Banner, EmailTemplate, SmsTemplate


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ("business", "link")
    search_fields = ("business__name", "link")
    list_per_page = 25
    list_select_related = ("business",)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(ModelAdmin):
    list_display = ("name", "subject", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "subject")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25


@admin.register(SmsTemplate)
class SmsTemplateAdmin(ModelAdmin):
    list_display = ("name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
