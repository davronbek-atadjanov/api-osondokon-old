import os

PAYME_ID = os.getenv("PAYME_ID", "")
PAYME_KEY = os.getenv("PAYME_KEY", "")
PAYME_ACCOUNT_FIELD = os.getenv("PAYME_ACCOUNT_FIELD", "order_id")
PAYME_AMOUNT_FIELD = os.getenv("PAYME_AMOUNT_FIELD", "amount")
PAYME_ACCOUNT_MODEL = os.getenv("PAYME_ACCOUNT_MODEL", "order.models.Order")
PAYME_ONE_TIME_PAYMENT = os.getenv("PAYME_ONE_TIME_PAYMENT", "True") == "True"
PAYME_RETURN_URL = os.getenv("PAYME_RETURN_URL", "")

CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")
CLICK_ACCOUNT_MODEL = os.getenv("CLICK_ACCOUNT_MODEL", "order.models.Order")
CLICK_AMOUNT_FIELD = os.getenv("CLICK_AMOUNT_FIELD", "amount")
CLICK_RETURN_URL = os.getenv("CLICK_RETURN_URL", "")
