import graphene
from graphene_django.filter import DjangoFilterConnectionField

import django_filters
from django.db.models import Count, Sum, Max

from apps.api.graphql.v1.types.business import MembershipNode
from apps.business.models import Membership
from apps.order.models import Order

class ClientFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="user__full_name", lookup_expr="icontains")
    tag = django_filters.CharFilter(field_name="tag", lookup_expr="icontains")

    class Meta:
        model = Membership
        fields = ["search", "tag"]

class TopClientType(graphene.ObjectType):
    full_name = graphene.String()
    phone_number = graphene.String()
    order_count = graphene.Int()
    total_spent = graphene.Int()
    last_order_date = graphene.String()

class Query(graphene.ObjectType):
    client = graphene.Field(MembershipNode, id=graphene.ID(required=True))
    clients = DjangoFilterConnectionField(MembershipNode, business_id=graphene.String(required=True), filterset_class=ClientFilter)

    top_clients = graphene.List(
        TopClientType,
        business_id=graphene.String(required=True),
        limit=graphene.Int(default_value=10)
    )
    def resolve_customer(self, info, id, **kwargs):
        return Membership.objects.filter(user__id=id)

    def resolve_clients(self, info, business_id, **kwargs):
        return Membership.objects.filter(business__hash_id=business_id, role="CLIENT")

    def resolve_top_clients(self, info, business_id, limit):
        top_customers = (
            Order.objects.filter(business__hash_id=business_id, is_paid=True, source=Order.OrderSource.CUSTOMER)
            .values("user__id", "user__full_name", "user__phone_number")
            .annotate(
                order_count=Count("id"),
                total_spent=Sum("total_amount"),
                last_order_date=Max("created_at")
            )
            .order_by("-order_count")[:limit]
        )

        return [
            TopClientType(
                full_name=c['user__full_name'],
                phone_number=c['user__phone_number'],
                order_count=c['order_count'],
                total_spent=c['total_spent'],
                last_order_date=c['last_order_date'].strftime("%Y-%m-%d")
            )
            for c in top_customers
        ]