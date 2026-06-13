from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.telegrambot.models import Telegram_bot


@admin.register(Telegram_bot)
class TelegramBotAdmin(ModelAdmin):
    list_display = ("business", "business_link", "token")
    search_fields = ("business__name", "business_link", "token")
    list_per_page = 25
    list_select_related = ("business",)
