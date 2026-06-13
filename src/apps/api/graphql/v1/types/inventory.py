import graphene
import json
from graphene_django.types import DjangoObjectType
from graphene.relay import Node

from apps.product.models import Product
from apps.api.graphql.v1.types.category import CategoryType

class InventoryItemType(DjangoObjectType):
    images = graphene.List(graphene.String)
    category = graphene.Field(CategoryType)

    class Meta:
        model = Product
        interfaces = (Node,)
        filter_fields = []

    def resolve_category(self, info):
        return self.category

    def resolve_images(self, info):
        if isinstance(self.images, str):
            try:
                return json.loads(self.images)
            except json.JSONDecodeError:
                return []
        return self.images or []
