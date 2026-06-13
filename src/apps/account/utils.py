import logging
import random

logger = logging.getLogger(__name__)

def generate_unique_username():
    from .models import User
    while True:
        random_username = f"osondokon_{random.randint(100_000_000, 999_999_999)}"
        if not User.objects.filter(username=random_username).exists():
            return random_username

def generate_unique_email():
    from .models import User
    while True:
        random_email = f"osondokon-{random.randint(100_000_000, 999_999_999)}@gmail.com"
        if not User.objects.filter(email=random_email).exists():
            return random_email

def get_cooldown_time(attempts: int) -> int:
    """Return cooldown time in seconds based on the number of attempts."""
    if attempts <= 0:
        return 180  # 3 minutes
    elif attempts == 1:
        return 360  # 6 minutes
    elif 2 <= attempts <= 3:
        return 900  # 15 minutes
    elif attempts == 4:
        return 1800  # 30 minutes
    else:  # attempts >= 5
        return 3600  # 1 hour

# def send_sms_async(phone_number: str, message: str):
#     logger.info(f"Sending SMS to {phone_number}")
#     try:
#         print("Sending SMS asynchronously...")
#         return send_sms(phone_number, message)
#     except Exception as e:
#         logger.error(f"SMS sending failed: {str(e)}")
#         raise


# def send_sms(phone_number: str, message: str):
#     url = settings.SMS_API_URL
#     params = {
#         "unique_id": settings.SMS_API_UNIQUE_ID,
#         "phone_number": phone_number,
#         "message": message
#     }
#     response = requests.post(url, params=params)
#     response.raise_for_status()
#     print(f"SMS sent successfully to {phone_number} and {response.status_code}")
#     logger.info(f"SMS sent successfully to {phone_number}")
#     return True