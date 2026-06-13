from django.contrib import admin
from apps.telegrambot.models import Telegram_bot

class Telegram_botAdmin(admin.ModelAdmin):
    list_display = ('business', 'business_link', 'token')
    search_fields = ('business__name', 'business_link', 'token')


admin.site.register(Telegram_bot, Telegram_botAdmin)
