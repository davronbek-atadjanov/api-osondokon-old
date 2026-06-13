# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from payme.models import PaymeTransactions
# from apps.order.models import Order
# from apps.business.models import Business

# @receiver(post_save, sender=PaymeTransactions)
# def handle_transaction_payment_link(sender, instance, created, **kwargs):
#     try:
#         if instance.is_performed() and created:
#             order_id = instance.account_id
#             order = Order.objects.get(id=order_id)

#             if order.delivery == "BUSINESS" and order.comment == "TOPUP":
#                 business = Business.objects.get(id=order.business__id)
#                 business.account += order.total_amount
#                 business.save()
                    
#     except Exception as e:
#         print(f"Error in payment link generation: {e}")