import graphene
from apps.api.graphql.v1.types.business import RoleType
from graphene_django.filter import DjangoFilterConnectionField
from apps.business.models import Role
import django_filters


class Filter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    class Meta:
        model = Role
        fields = ["search"]

class Query(graphene.ObjectType):
    roles = DjangoFilterConnectionField(RoleType, business_id=graphene.String(required=True), filterset_class=Filter)

    def resolve_roles(self, info, business_id):
        return Role.objects.filter(business__hash_id=business_id)