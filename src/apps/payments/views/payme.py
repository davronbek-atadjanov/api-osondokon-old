from payme.views import PaymeWebHookAPIView
from payme.models import PaymeTransactions  
from apps.order.models import Order
from payme import exceptions
import base64
import binascii
from django.conf import settings
from apps.payments.utils import check_payme_api_key


class PaymeCallBackAPIView(PaymeWebHookAPIView):

    @staticmethod
    def check_authorize(request):
        """
        Verify the integrity of the request using the merchant key.
        """
        password = request.META.get('HTTP_AUTHORIZATION')
        if not password:
            raise exceptions.PermissionDenied("Missing authentication credentials")
        password = password.split()[-1]

        try:
            password = base64.b64decode(password).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise exceptions.PermissionDenied("Decoding error in authentication credentials") from exc

        try:
            payme_key = password.split(':')[-1]
        except IndexError as exc:
            message = "Invalid merchant key format in authentication credentials"
            raise exceptions.PermissionDenied(message) from exc
    

        # Extract and validate transaction_id and order_id
        params = request.data.get('params', {})
        transaction_id = params.get('id')
        account = params.get('account', {})
        order_id = account.get('id')

        if not transaction_id and not order_id:
            raise exceptions.PermissionDenied("Invalid merchant key specified")


        order = None

        if transaction_id:
            try:
                transaction = PaymeTransactions.objects.get(transaction_id=transaction_id)
                order = Order.objects.get(id=transaction.account_id)
            except PaymeTransactions.DoesNotExist:
                transaction = None
            except Order.DoesNotExist:
                order = None

        # Agar yuqorida order topilmagan bo‘lsa, order_id orqali topamiz
        if not order and order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                order = None
        

        # Auth keyni tekshirish logikasi
        if order and order.source == Order.OrderSource.BUSINESS:
            if payme_key != settings.PAYME_KEY:
                raise exceptions.PermissionDenied("Invalid merchant key specified")
        elif order and order.source == Order.OrderSource.CUSTOMER:
            if not check_payme_api_key(payme_key, order.business.payment_methods):
                raise exceptions.PermissionDenied("Invalid merchant key specified")
        else:
            if payme_key != settings.PAYME_KEY:
                raise exceptions.PermissionDenied("Invalid merchant key specified")

    def handle_created_payment(self, params, result, *args, **kwargs):
        """
        Handle the successful payment. You can override this method
        """
        print(f"Transaction created for this params: {params} and cr_result: {result}")

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        """
        Handle the successful payment. You can override this method
        """
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )

        order = Order.objects.get(id=transaction.account_id)
        if transaction.is_performed():
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

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        """
        Handle the cancelled payment. You can override this method
        """
        print(f"Transaction cancelled for this params: {params} and cancelled_result: {result}")


# Ikkinchi yechim

# @staticmethod
# def check_authorize(request):
#     """
#     Verify the integrity of the request using the merchant key.
#     """
#     password = request.META.get('HTTP_AUTHORIZATION')
#     if not password:
#         raise exceptions.PermissionDenied("Missing authentication credentials")
#     print("Bu ishladi prod", request.data['params'])
#     password = password.split()[-1]

#     try:
#         password = base64.b64decode(password).decode('utf-8')
#     except (binascii.Error, UnicodeDecodeError) as exc:
#         raise exceptions.PermissionDenied("Decoding error in authentication credentials") from exc

#     try:
#         payme_key = password.split(':')[-1]
#     except IndexError as exc:
#         message = "Invalid merchant key format in authentication credentials"
#         raise exceptions.PermissionDenied(message) from exc

#     if not check_payme_api_key(payme_key):
#         raise exceptions.PermissionDenied("Invalid merchant key specified")
