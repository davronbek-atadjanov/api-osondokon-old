import graphene
from graphql_relay.node.node import from_global_id
from django.db.models import Q
from apps.product.models import Product
from apps.api.graphql.v1.types.inventory import InventoryItemType

class InventoryFilterInput(graphene.InputObjectType):
    search = graphene.String()
    category_id = graphene.ID()
    order_count_min = graphene.Int()
    order_count_max = graphene.Int()
    min_stock = graphene.Int()
    max_stock = graphene.Int()
    is_active = graphene.Boolean()

class Query(graphene.ObjectType):
    inventory_items = graphene.List(
        InventoryItemType,
        business_id=graphene.String(required=True),
        filters=InventoryFilterInput()
    )

    def resolve_inventory_items(self, info, business_id, filters=None):
        qs = Product.objects.filter(business__hash_id=business_id)

        if filters:
            if filters.search:
                qs = qs.filter(Q(name_uz__icontains=filters.search) | Q(name_ru__icontains=filters.search))

            if filters.category_id:
                category_id = from_global_id(filters.category_id)[1]
                qs = qs.filter(category_id=category_id)

            if filters.min_stock is not None:
                qs = qs.filter(stock__gte=filters.min_stock)

            if filters.max_stock is not None:
                qs = qs.filter(stock__lte=filters.max_stock)

            if filters.is_active is not None:
                qs = qs.filter(is_active=filters.is_active)

            if filters.order_min is not None:
                qs = qs.filter(order_count__gte=filters.order_count_min)

            if filters.order_max is not None:
                qs = qs.filter(order_count__lte=filters.order_count_max)

        return qs.order_by('-order_count')
