import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from apps.telegrambot.models import Telegram_bot
import logging  
logger = logging.getLogger(__name__)

translations = {
    "en": {
        "welcome": "Welcome!",
        "open_shop": "🛒 Open Shop",
        "language": "🌐 Language",
        "orders": "📦 My Orders",
        "choose_lang": "Choose your language",
        "placeholder": "osondokon.uz - developed by",
        "langs": {
            "en": "🇬🇧 English",
            "uz": "🇺🇿 Uzbek",
            "ru": "🇷🇺 Russian",
            "tr": "🇹🇷 Türkçe",
        },
    },
    "uz": {
        "welcome": "Xush kelibsiz!",
        "open_shop": "🛒 Do'konni ochish",
        "language": "🌐 Til",
        "orders": "📦 Buyurtmalarim",
        "choose_lang": "Tilni tanlang",
        "placeholder": "osondokon.uz tomonidan ishlab chiqarilgan",
        "langs": {
            "en": "🇬🇧 Inglizcha",
            "uz": "🇺🇿 O'zbekcha",
            "ru": "🇷🇺 Ruscha",
            "tr": "🇹🇷 Turkcha",
        },
    },
    "ru": {
        "welcome": "Добро пожаловать!",
        "open_shop": "🛒 Открыть магазин",
        "language": "🌐 Язык",
        "orders": "📦 Мои заказы",
        "choose_lang": "Выберите язык",
        "placeholder": "osondokon.uz - разработано",
        "langs": {
            "en": "🇬🇧 Английский",
            "uz": "🇺🇿 Узбекский",
            "ru": "🇷🇺 Русский",
            "tr": "🇹🇷 Турецкий",
        },
    },
    "tr": {
        "welcome": "Hoş geldiniz!",
        "open_shop": "🛒 Mağazayı Aç",
        "language": "🌐 Dil",
        "orders": "📦 Siparişlerim",
        "choose_lang": "Dil seçin",
        "placeholder": "osondokon.uz tarafından geliştirilmiştir",
        "langs": {
            "en": "🇬🇧 İngilizce",
            "uz": "🇺🇿 Özbekçe",
            "ru": "🇷🇺 Rusça",
            "tr": "🇹🇷 Türkçe",
        },
    },
}


def get_lang(chat_id):
    return cache.get(f"lang_{chat_id}", "en")


def set_lang(chat_id, lang):
    cache.set(f"lang_{chat_id}", lang, timeout=3600 * 24 * 7)  # 7 days


@csrf_exempt
def telegram_webhook(request, bot_id):
    bot = get_object_or_404(Telegram_bot, id=bot_id)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received: {request.body}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    # Determine update type
    message = data.get("message")
    callback = data.get("callback_query")
    chat_id = None

    if message:
        chat_id = message["chat"]["id"]
    elif callback and "message" in callback:
        chat_id = callback["message"]["chat"]["id"]
    elif "my_chat_member" in data:
        chat_id = data["my_chat_member"]["chat"]["id"]
    else:
        logger.warning(f"Unknown update type: {data}")
        return JsonResponse({"ok": False, "error": "Unknown update type"}, status=400)

    # Language
    lang = get_lang(chat_id)
    t = translations[lang]

    if message:
        text = message.get("text", "")
        if text == t["language"]:
            send_inline_languages(bot.token, chat_id, lang)
        elif text == "/start" or text:
            send_main_menu(bot.token, chat_id, lang, link=bot.business_link)

    # Handle callback_query updates
    elif callback:
        cb_data = callback.get("data")
        callback_id = callback.get("id")
        # Answer the callback query to stop the loading animation
        answer_callback_query(bot.token, callback_id)
        if cb_data in translations:
            set_lang(chat_id, cb_data)
            update_language_message(
                bot.token, callback["message"]["message_id"], chat_id, cb_data
            )
            send_main_menu(bot.token, chat_id, cb_data, link=bot.business_link)

    return JsonResponse({"ok": True})


def answer_callback_query(token, callback_query_id):
    """Send a response to the callback query to stop the loading animation."""
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id
    }
    requests.post(url, json=payload)


def update_language_message(token, message_id, chat_id, selected_lang):
    """Update the language selection message to show which language was selected."""
    t = translations[selected_lang]
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": f"{t['choose_lang']}\n\n✅ {t['langs'][selected_lang]}"
    }
    requests.post(url, json=payload)

def send_main_menu(token, chat_id, lang, link=None):
    if not link:
        link = "https://www.osondokon.uz/"
    t = translations[lang]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": t["welcome"],
        "reply_markup": {
            "keyboard": [
                [
                    {
                        "text": t["open_shop"],
                        "web_app": {"url": link},
                    }
                ],
                [
                    {"text": t["language"]},
                    {
                        "text": t["orders"],
                        "web_app": {"url": f"{link}/profile/orders"},
                    },
                ],
            ],
            "input_field_placeholder": t["placeholder"],
            "resize_keyboard": True,  # foydalanuvchiga qulay
        },
    }
    try:
        requests.post(url, json=payload).raise_for_status()
    except Exception as e:
        logger.error(f"Telegram API error: {e}")



def send_inline_languages(token, chat_id, lang):
    t = translations[lang]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": t["choose_lang"],
        "reply_markup": {
            "inline_keyboard": [
                [{"text": translations[lang]["langs"][code], "callback_data": code}]
                for code in ["en", "uz", "ru", "tr"]
            ]
        },
    }
    requests.post(url, json=payload)