import graphene
from apps.api.graphql.v1.types.business import BusinessType, MembershipType, TrafficCountType, MyBusinessType, PaymentMethodsType 
from apps.business.models import Business, Membership, TrafficStat
from apps.order.models import Order
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta, date

# First, let's define the StatsType that will structure our statistics


class StatsType(graphene.ObjectType):
    total_clients = graphene.Int()
    total_revenue = graphene.Int()
    orders_count = graphene.Int()
    orders_on_the_way = graphene.Int()


class Query(graphene.ObjectType):
    business = graphene.Field(
        BusinessType, id=graphene.String(required=True)
    )

    my_businesses = graphene.List(MyBusinessType, id=graphene.String(required=False))
    users = graphene.List(
        MembershipType,
        business_id=graphene.String(required=True),
        role=graphene.String()
    )

    stats = graphene.Field(
        StatsType,
        business_id=graphene.String(required=True),
        start_date=graphene.String(),
        end_date=graphene.String(),
    )

    traffic_stats = graphene.Field(
        TrafficCountType,
        business_id=graphene.String(required=True),
        purpose=graphene.String(required=True)  # daily, weekly, monthly
    )

    def resolve_business(root, info, id):
        return Business.objects.filter(Q(hash_id=id) | Q(tg_hash_id=id)).first()

    def resolve_my_businesses(root, info, id=None):
        user = info.context.user

        if not user or not user.is_authenticated:
            return Business.objects.none()

        businesses = Business.objects.filter(
            id__in=Membership.objects.filter(
                user__id=user.id).values_list("business_id", flat=True)
        )

        if id:
            businesses = businesses.filter(hash_id=id)

        return businesses

    def resolve_users(self, info, business_id, role=None):
        user = info.context.user
        if not user or not user.is_authenticated:
            return Membership.objects.none()
        
        query = Membership.objects.filter(business__hash_id=business_id, user=user)

        if role:  # Ensure role is a list before filtering
            listed_roles = list(role.split(",")) or []
            # Convert to list if needed
            query = query.filter(role__name__in=listed_roles)

        return query

    def resolve_stats(root, info, business_id, start_date=None, end_date=None):
        user = info.context.user
        if not user or not user.is_authenticated:
            return None
        
        business = Business.objects.filter(hash_id=business_id).first()
        if not business:
            return None
        
        # Parse dates if provided
        start_datetime = None
        end_datetime = None

        if start_date:
            try:
                start_datetime = timezone.make_aware(
                    datetime.strptime(start_date, '%Y-%m-%d'))
            except ValueError:
                pass

        if end_date:
            try:
                end_datetime = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d'))
                # Include the entire end day by setting to end of day
                end_datetime = end_datetime.replace(
                    hour=23, minute=59, second=59)
            except ValueError:
                pass

        # Filtering orders properly
        order_filters = {"business": business}
        if start_datetime and end_datetime:
            order_filters["created_at__range"] = (start_datetime, end_datetime)

        orders = Order.objects.filter(~Q(delivery="BUSINESS"), **order_filters)

        done_orders = orders.filter(status="COMPLETED").aggregate(
            total_amount=Sum("total_amount"), total_count=Count("id")
            # Ensure it never returns None
        ) or {"total_amount": 0, "total_count": 0}

        clients = Membership.objects.filter(
            business=business, role="CLIENT").count()

        return StatsType(
            total_clients=clients,
            total_revenue=done_orders["total_amount"] or 0,
            orders_count=done_orders["total_count"] or 0,
            orders_on_the_way=(orders.count() or 0) -
            (done_orders["total_count"] or 0),
        )

    def resolve_traffic_stats(self, info, business_id, purpose):
        
        today = date.today()

        if purpose == "daily":
            start_date = end_date = today

        elif purpose == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        elif purpose == "monthly":
            start_date = today.replace(day=1)
            end_date = start_date.replace(
                day=(start_date + timedelta(days=31)).day
            )
        else:
            raise ValueError("Purpose must be daily, weekly, or monthly")

        stats = TrafficStat.objects.filter(
            business__hash_id=business_id,
            date__range=(start_date, end_date)
        ).aggregate(
            web_count=Sum("count", filter=Q(platform__iexact="WEB")),
            telegram_count=Sum("count", filter=Q(platform__iexact="TELEGRAM"))
        )

        return TrafficCountType(
            web=stats["web_count"] or 0,
            telegram=stats["telegram_count"] or 0,
            purpose=purpose
        )