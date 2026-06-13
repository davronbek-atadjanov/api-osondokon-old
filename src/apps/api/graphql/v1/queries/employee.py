import graphene
from apps.api.graphql.v1.types.business import MembershipNode
from apps.business.models import Membership
from graphene_django.filter import DjangoFilterConnectionField
import django_filters


class ClientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name="user__full_name", lookup_expr="icontains")
    role = django_filters.CharFilter(
        field_name="role", lookup_expr="icontains")
    tag = django_filters.CharFilter(field_name="tag", lookup_expr="icontains")

    class Meta:
        model = Membership
        fields = ["search", "tag", "role"]


class Query(graphene.ObjectType):
    employee = graphene.Field(MembershipNode, id=graphene.String(required=True))
    employees = DjangoFilterConnectionField(MembershipNode, business_id=graphene.String(required=True), roles=graphene.List(graphene.String), filterset_class=ClientFilter)

    def resolve_employee(self, info, id, business_id):
        if id == "me":
            id = info.context.user_id
        return Membership.objects.filter(business__hash_id=business_id, user__id=id)

    def resolve_employees(self, info, business_id, roles=[]):
        queryset = Membership.objects.filter(business__hash_id=business_id).exclude(role="CLIENT")
        if roles:
            return queryset.filter(role__in=roles)
        return queryset
