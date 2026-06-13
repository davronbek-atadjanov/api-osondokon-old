import requests
from django.conf import settings
from django.core.cache import cache


class EskizUz:
    TOKEN_KEY = "eskiz_uz_token"

    GET_TOKEN_URL = "https://notify.eskiz.uz/api/auth/login"
    SEND_SMS_URL = "https://notify.eskiz.uz/api/message/sms/send"

    ACTIVATION_MESSAGE = "KODNI HECH KIMGA BERMANG!. {business_name} platformasidan ro'yxatdan o'tish uchun tasdiqlash kodi: {code}"
    PASSWORD_RESET_MESSAGE= "KODNI HECH KIMGA BERMANG!. {business_name} platformasidan parolingizni tiklash uchun tasdiqlash kodi: {code}"

    EMAIL = settings.ESKIZ_UZ_EMAIL
    PASSWORD = settings.ESKIZ_UZ_PASSWORD

    @classmethod
    def get_token(cls):
        """Token olish"""
        token = cache.get(cls.TOKEN_KEY)
        if not token:
            response = requests.post(
                url=cls.GET_TOKEN_URL,
                json={
                    'email': cls.EMAIL,
                    'password': cls.PASSWORD
                }
            )
            response.raise_for_status()
            token = response.json()['data']['token']

            cache.set(cls.TOKEN_KEY, token, timeout=60 * 60 * 24 * 30)
        return token

    @classmethod
    def send_sms(cls, phone_number: str, business_name: str, message_type: str, code: str, nickname: str = "4546") -> bool:
        """SMS yuborish (OTP code modeldan olinadi)"""

        # Message type bo‘yicha xabar tayyorlash
        if message_type == "FORGOT_PASSWORD":
            message = cls.PASSWORD_RESET_MESSAGE.format(business_name=business_name, code=code)
        elif message_type == "ACTIVATION":
            message = cls.ACTIVATION_MESSAGE.format(business_name=business_name, code=code)
        else:
            raise ValueError("Invalid message type. Must be FORGOT_PASSWORD or AUTH_CODE")

        # Token olish
        token = cls.get_token()
        if not token:
            return False

        headers = {
            'Authorization': f'Bearer {token}',
        }

        data = {
            'mobile_phone': phone_number,
            'message': message,
            'from': nickname
        }

        response = requests.post(cls.SEND_SMS_URL, headers=headers, json=data)

        # Agar token muddati tugagan bo‘lsa, yangisini olish
        if response.status_code == 401:
            cache.delete(cls.TOKEN_KEY)  # eski tokenni o‘chirish
            token = cls.get_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
                response = requests.post(cls.SEND_SMS_URL, headers=headers, json=data)

        return response.status_code == 200