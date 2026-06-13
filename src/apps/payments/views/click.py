from click_up.views import ClickWebhook
from click_up.models import ClickTransaction
from django.conf import settings
from rest_framework import exceptions
from apps.payments.utils import get_click_payment_method
from apps.order.models import Order
import hashlib

# pylint: disable=E1101
class ClickWebhookAPIView(ClickWebhook):
    """
    A view to handle Click Webhook API calls.
    This view will handle all the Click Webhook API events.
    """
    def check_auth(self, params, service_id=None, secret_key=None):
        """
        Verifies the authenticity of the transaction using the secret key.

        :return: True if the signature is valid,
            otherwise raises an AuthFailed exception.
        """
        # by default it should be get from settings
        # in the another case u can override
        if not secret_key or not service_id:
            try:
                order = Order.objects.get(id=params.merchant_trans_id)
            except Order.DoesNotExist:
                raise exceptions.AuthFailed("Order not found for transaction")
            
            if order and order.source == Order.OrderSource.BUSINESS:
                service_id = settings.CLICK_SERVICE_ID
                secret_key = settings.CLICK_SECRET_KEY
            elif order:
                payment_method = get_click_payment_method(order.business.payment_methods)
                if payment_method:
                    # Use the payment method's service_id and secret_key
                    service_id = payment_method['service_id'] or None
                    secret_key = payment_method['secret_key'] or None

        if not all([service_id, secret_key]):
            error = "Missing required CLICK_SETTINGS: service_id, secret_key, or merchant_id" # noqa
            raise exceptions.AuthFailed(error)

        text_parts = [
            params.click_trans_id,
            service_id,
            secret_key,
            params.merchant_trans_id,
            params.merchant_prepare_id or "",
            params.amount,
            params.action,
            params.sign_time,
        ]
        text = ''.join(map(str, text_parts))

        calculated_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

        if calculated_hash != params.sign_string:
            raise exceptions.AuthFailed("invalid signature")

    def successfully_payment(self, params):
        """
        successfully payment method process you can ovveride it
        """
        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )
        order = Order.objects.get(id=transaction.account_id)
        order.is_paid = True
        order.save()
        # If the order is a business top-up, update the business account
        if order.source == Order.OrderSource.BUSINESS: 
            try:
                business = order.business
                business.account += order.total_amount
                business.save()
            except Exception as e:
                print(f"Error updating business account: {e}")  
        print("Payment successfully processed for order:", order.id)

    def cancelled_payment(self, params):
        """
        cancelled payment method process you can ovveride it
        """
        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )

        if transaction.state == ClickTransaction.CANCELLED:
            order = Order.objects.get(id=transaction.account_id)
            order.is_paid = False
            order.save()
        print("Payment cancelled for order:", order.id)