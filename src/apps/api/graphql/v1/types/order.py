import graphene
from graphene_django.types import DjangoObjectType
from apps.order.models import Order, OrderItem
from graphene.relay import Node
from .scalars import JSONScalar
from .product import ProductType, ProductVariantType

class OrderItemType(DjangoObjectType):
    product = graphene.Field(ProductType)
    variant = graphene.Field(ProductVariantType)
    
    class Meta:
        model = OrderItem
        fields = "__all__"
    
    def resolve_product(self, info):
        return self.product
    
    def resolve_variant(self, info):
        return self.variant

class OrderType(DjangoObjectType):
    items = graphene.List(OrderItemType)
    address = JSONScalar()
    payment_link = graphene.String()
    
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (Node,)

    def resolve_items(self, info):
        return OrderItem.objects.filter(order=self)
    
class OrderItemConnection(graphene.relay.Connection):
    class Meta:
        node = OrderItemType

    total_count = graphene.Int()
    
    def resolve_total_count(root, info, **kwargs):
        return root.iterable.count()

class OrderConnection(graphene.relay.Connection):
    class Meta:
        node = OrderType

    total_count = graphene.Int()
    address = JSONScalar()
    
    def resolve_total_count(root, info, **kwargs):
        return root.iterable.count()

class OrderMapType(graphene.ObjectType):
    id = graphene.Int()
    latitude = graphene.String()
    longitude = graphene.String()

    def resolve_latitude(self, info):
        if self.branch:
            return self.branch.latitude
        return self.address.get("latitude", None)

    def resolve_longitude(self, info):
        if self.branch:
            return self.branch.longitude
        return self.address.get("longitude", None)