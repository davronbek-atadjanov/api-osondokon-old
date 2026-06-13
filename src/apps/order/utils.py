def detect_platform(request):
    """
    Agar X-Telegram-Bot header yoki User-Agent ichida TelegramBot bo‘lsa → TELEGRAM,
    aks holda → WEB
    """
    if "X-Telegram-Bot" in request.headers:
        return "TELEGRAM"
    
    if "TelegramBot" in request.META.get("HTTP_USER_AGENT", ""):
        return "TELEGRAM"
    
    return "WEB"