from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.telegrambot.models import Telegram_bot
from django.conf import settings
import requests

@receiver(post_save, sender=Telegram_bot)
def set_telegram_webhook(sender, instance, created, **kwargs):
    try:
        print(f"Checking/Setting Telegram webhook for bot: {instance.token}")

        webhook_url = settings.SERVER_DOMAIN + f"/telegram-webhook/{instance.id}/"
        token = instance.token

        # Get current webhook info
        current_webhook_info = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo").json()

        if current_webhook_info.get('ok'):
            current_url = current_webhook_info['result'].get('url')
            if current_url and current_url != webhook_url:
                print(f"Old webhook ({current_url}) found. Deleting...")
                delete = requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook")
                print(f"Delete status: {delete.status_code} - {delete.text}")

        # Set the new webhook (regardless, in case it was empty before)
        set_hook = requests.get(f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}")
        if set_hook.ok:
            print("Webhook set successfully.")
        else:
            print(f"Failed to set webhook: {set_hook.text}")
    except Exception as e:
        print(f"Webhook error: {e}")
