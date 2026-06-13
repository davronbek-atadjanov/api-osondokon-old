from celery import shared_task
from apps.account.sms_providers import EskizUz
from apps.api.helper import consume_sms
import logging
from django.utils.timezone import now

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_sms_task(self, phone_number, business_name, message_type, code, business_id, source=None, otp_id=None):
    try:
        success = EskizUz.send_sms(
            phone_number=phone_number,
            business_name=business_name,
            message_type=message_type,
            code=code
        )

        if not success:
            logger.error(
                "SMS yuborilmadi",
                extra={
                    "phone_number": phone_number,
                    "business_id": business_id,
                    "message_type": message_type,
                    "otp_id": otp_id,
                })       
            return False
        if business_id and business_id > 0:
            consume_sms(business_id, source, phone_number)

        if otp_id:
            from apps.account.models import OTP
            otp = OTP.objects.get(id=otp_id)
            otp.attempts += 1
            otp.last_sent = now()
            otp.save(update_fields=["attempts", "last_sent"])

        return True
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)



@shared_task
def reset_all_otp_attempts():
    """
    Reset all OTP objects' attempts to 0 unconditionally.
    """
    from apps.account.models import OTP

    updated = OTP.objects.exclude(attempts=0).update(attempts=0)
    return f"{updated} OTP attempt(s) reset to 0"
