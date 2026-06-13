import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id

import django_filters
from django.db.models import Q

from apps.api.graphql.v1.types.product import ProductType
from apps.product.models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    business_id = django_filters.CharFilter(method="filter_business")
    order_count_min = django_filters.NumberFilter(method='filter_order_count_min')
    order_count_max = django_filters.NumberFilter(method='filter_order_count_max')
    category = django_filters.CharFilter(method="filter_category")


    class Meta:
        model = Product
        fields = ["search", "order_count_min", "order_count_max", "business_id", "category"]
    
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name_uz__icontains=value) | Q(name_ru__icontains=value) | Q(name_tr__icontains=value)
        )
    
    def filter_category(self, queryset, name, value):
        return queryset.filter(category__id=from_global_id(value)[1])


    def filter_business(self, queryset, name, value):
        return queryset.filter(
            Q(business__hash_id=value) | Q(business__tg_hash_id=value)
        )
    
    def filter_order_count_min(self, queryset, name, value):
        return queryset.filter(order_count__gte=value)

    def filter_order_count_max(self, queryset, name, value):
        return queryset.filter(order_count__lte=value)

class Query(graphene.ObjectType):
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)

    def resolve_product(root, info, id):
        return Product.objects.filter(id=from_global_id(id)[1]).first()