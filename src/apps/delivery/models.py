from django.db import models

class DeliveryType(models.TextChoices):
    FREE = 'FREE', 'Free'
    FIXED_PRICE = 'FIXED', 'Fixed Price'
    FLEXIBLE_PRICE = 'FLEXIBLE', 'Flexible Price'
class DeliveryMethod(models.Model):
    business = models.OneToOneField("business.Business", on_delete=models.CASCADE, related_name='delivery_methods')

    type = models.CharField(max_length=15, choices=DeliveryType.choices)
    max_km = models.PositiveIntegerField(null=True, blank=True)
    country = models.JSONField(null=True, blank=True)  # Stores country data as a JSON object
    cities = models.JSONField(null=True, blank=True)  # Stores a list of cities
    price = models.PositiveIntegerField(null=True, blank=True)  # so‘mda saqlanadi
    description = models.TextField(null=True, blank=True)  # Renamed 'text' to be clearer
    initial_km = models.PositiveIntegerField(null=True, blank=True)
    initial_km_price = models.PositiveIntegerField(null=True, blank=True)
    every_km_price = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    branches = models.ManyToManyField("business.Branch", blank=True)
    min_price = models.PositiveIntegerField(null=True, blank=True)
    estimated_shipping_time = models.PositiveIntegerField(null=True, blank=True, help_text="Yetkazib berish vaqti (soatda)")


    class Meta:
        verbose_name = 'Delivery Method'
        verbose_name_plural = 'Delivery Methods'

    def __str__(self):
        return f'{self.business.name} - {self.type}'

class PickupMethod(models.Model):
    business = models.OneToOneField("business.Business", on_delete=models.CASCADE, related_name='pickup_methods')
    branches = models.ManyToManyField("business.Branch", blank=True)

    def __str__(self):
        return f'{self.business.name}'

