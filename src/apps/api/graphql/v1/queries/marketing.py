import graphene

from django.db.models import Q

from apps.api.graphql.v1.types.marketing import BannerType
from apps.marketing.models import Banner

class Query(graphene.ObjectType):
    banners = graphene.List(BannerType, business_id=graphene.String(required=True))

    def resolve_banners(root, info, business_id):
        return Banner.objects.filter(Q(business__hash_id=business_id) | Q(business__tg_hash_id=business_id))
