import graphene

from django.db.models import Q

from apps.api.graphql.v1.types.delivery import DeliveryMethodType, PickupMethodType
from apps.delivery.models import DeliveryMethod, PickupMethod

class Query(graphene.ObjectType):
    delivery_methods = graphene.List(DeliveryMethodType, business_id=graphene.String(required=True))
    pickup_methods = graphene.List(PickupMethodType, business_id=graphene.String(required=True))

    def resolve_delivery_methods(self, info, business_id):
        return DeliveryMethod.objects.filter(Q(business__hash_id=business_id) | Q(business__tg_hash_id=business_id)).first()

    def resolve_pickup_methods(self, info, business_id):
        return PickupMethod.objects.filter(business__hash_id=business_id)
