from graphene_django import DjangoObjectType
from apps.delivery.models import DeliveryMethod, PickupMethod

class DeliveryMethodType(DjangoObjectType):
    class Meta:
        model = DeliveryMethod
        fields = "__all__"

class PickupMethodType(DjangoObjectType):
    class Meta:
        model = PickupMethod
        fields = "__all__"