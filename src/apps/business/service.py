import requests
import logging
from django.conf import settings
from apps.telegrambot.models import Telegram_bot

logger = logging.getLogger(__name__)


def add_vercel_domain(custom_domain):
    """Add a domain to Vercel via API and update CORS settings"""
    url = f"https://api.vercel.com/v10/projects/{settings.VERCEL_PROJECT_ID}/domains"
    headers = {
        "Authorization": f"Bearer {settings.VERCEL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "name": custom_domain,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info(f"Domain {custom_domain} added to Vercel project")

            return True
        else:
            logger.error(f"Failed to add domain to Vercel: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Vercel API error: {str(e)}")
        return False


def remove_vercel_domain(custom_domain):
    """Remove a domain from Vercel via API and update CORS settings"""
    url = f"https://api.vercel.com/v10/projects/{settings.VERCEL_PROJECT_ID}/domains/{custom_domain}"
    headers = {
        "Authorization": f"Bearer {settings.VERCEL_API_KEY}"
    }

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code in [200, 204]:
            logger.info(f"Domain {custom_domain} removed from Vercel project")

            return True
        else:
            logger.error(
                f"Failed to remove domain from Vercel: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Vercel API error: {str(e)}")
        return False


def check_telegram_token(bot_token):
    """
    Verify Telegram bot token by making API call
    Returns (is_valid, result_data)
    """
    if not bot_token:
        return False, "Bot token is empty"

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)  # Add timeout

        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return True, data["result"]
            else:
                return False, data.get("description", "Unknown error")
        else:
            return False, f"HTTP Error: {response.status_code}"
    except requests.RequestException as e:
        logger.error(f"Telegram API request failed: {str(e)}")
        return False, f"Request error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error checking Telegram token: {str(e)}")
        return False, f"Unexpected error: {str(e)}"


def create_telegram_bot_async(business, bot_token, business_link):
    """Asynchronously create a Telegram bot with validation"""
    try:
        is_valid, result = check_telegram_token(bot_token)

        if is_valid:
            logger.info(
                f"Telegram bot validated for business {business.id}: {result}")
            if not business_link.startswith("https://"):
                business_link = "https://" + business_link
            Telegram_bot.objects.create(
                business=business,
                token=bot_token,
                business_link=business_link
            )
            add_vercel_domain(business_link)
            add_vercel_domain(f"www.{business_link}")
            logger.info(f"Telegram bot created for business {business.id}")
        else:
            logger.warning(
                f"Invalid Telegram bot token for business {business.id}: {result}")
    except Exception as e:
        logger.error(
            f"Error creating Telegram bot for business {business.id}: {str(e)}")

def remove_telegram_bot(business):
    """Remove Telegram bot for business if exists"""
    try:
        telegram_bot = Telegram_bot.objects.filter(business=business).first()
        if telegram_bot:
            telegram_bot.delete()
            remove_vercel_domain(telegram_bot.business_link)
            remove_vercel_domain(f"www.{telegram_bot.business_link}")
            logger.info(f"Telegram bot removed for business {business.id}")
            return True
    except Exception as e:
        logger.error(f"Error removing Telegram bot: {str(e)}")
    return False
