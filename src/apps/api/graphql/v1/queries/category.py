import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

import django_filters
from django.db.models import Q

from apps.api.graphql.v1.types.category import CategoryType
from apps.category.models import Category

class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    business_id = django_filters.CharFilter(method="filter_business")
    parent_id = django_filters.CharFilter(method='filter_parent')
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name_uz__icontains=value) | 
            Q(name_ru__icontains=value) | 
            Q(name_tr__icontains=value)
        )

    def filter_business(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(business__hash_id=value) | Q(business__tg_hash_id=value)
            )
        return queryset


    def filter_parent(self, queryset, name, value):
        if value:
            return queryset.filter(parent__id=from_global_id(value)[1])
        return queryset.filter(parent__isnull=True)

    class Meta:
        model = Category
        fields = ["search", "business_id", "parent_id"]

class Query(graphene.ObjectType):
    category = graphene.relay.Node.Field(CategoryType)
    categories = DjangoFilterConnectionField(CategoryType, filterset_class=CategoryFilter)