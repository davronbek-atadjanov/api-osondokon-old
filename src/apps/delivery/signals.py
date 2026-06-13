from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.business.models import Business
from apps.delivery.models import DeliveryMethod, DeliveryType

@receiver(post_save, sender=Business)
def create_delivery_method_for_business(sender, instance, created, **kwargs):
    if created:
        # Agar Business yangi yaratilgan bo‘lsa
        delivery = DeliveryMethod.objects.create(
            business=instance,
            type=DeliveryType.FREE,
            estimated_shipping_time=48,
            is_active=True,
            description="Shahar ichida bepul yetkazib berish"
        )
        return delivery
