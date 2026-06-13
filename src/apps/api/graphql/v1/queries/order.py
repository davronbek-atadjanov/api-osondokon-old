import graphene
from django.db.models import Sum, Count, F, Q
from apps.api.graphql.v1.types.order import (
  OrderType, OrderItemConnection, 
  OrderConnection, OrderMapType,
)
from apps.api.graphql.v1.types.auth import UserType
from apps.api.graphql.v1.types.business import BusinessType
from apps.order.models import Order, OrderItem
from apps.business.models import Business, Membership
from django.core.exceptions import FieldError
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta


class OrderStatsType(graphene.ObjectType):
    date = graphene.String()
    desktop = graphene.Int()
    mobile = graphene.Int()


class TopOrderItemType(graphene.ObjectType):
    product_id = graphene.Int()
    product_name = graphene.String()
    product_images = graphene.List(graphene.String)
    total_quantity = graphene.Int()
    total_revenue = graphene.Int()
    order_count = graphene.Int()


class BusinessTransactionType(graphene.ObjectType):
    who = graphene.Field(UserType)
    where = graphene.Field(BusinessType)
    why = graphene.String()
    amount = graphene.Int()

class OrderStatsByPurposeType(graphene.ObjectType):
    web = graphene.Int()
    telegram = graphene.Int()
    purpose = graphene.String()

class OrderFilterInput(graphene.InputObjectType):
    status = graphene.String()
    status_in = graphene.List(graphene.String)
    platform = graphene.String()
    platform_in = graphene.List(graphene.String)
    delivery_type = graphene.String()
    delivery_type_in = graphene.List(graphene.String)
    payment_methods = graphene.List(graphene.String)
    created_at_min = graphene.String()
    created_at_max = graphene.String()
    search = graphene.String()
    source = graphene.String()
    source_in = graphene.List(graphene.String)


class Query(graphene.ObjectType):
    order = graphene.Field(
        OrderType,
        id=graphene.Int(required=True),
        business_id=graphene.String(required=True),
    )

    orders = graphene.relay.ConnectionField(
        OrderConnection,
        business_id=graphene.String(required=True),
        filters=OrderFilterInput(),
    )

    my_orders = graphene.relay.ConnectionField(
        OrderConnection,
        business_id=graphene.String(required=True),
        filters=OrderFilterInput(),
    )

    business_transactions = graphene.List(
        BusinessTransactionType,
        business_id=graphene.String(required=True),
    )

    order_items = graphene.relay.ConnectionField(
        OrderItemConnection,
        order_id=graphene.Int(required=True),
        business_id=graphene.String(required=True),
    )

    orders_by_date = graphene.List(
        OrderStatsType,
        business_id=graphene.String(required=True),
        start_date=graphene.String(),
        end_date=graphene.String()
    )

    top_order_items = graphene.List(
        TopOrderItemType,
        business_id=graphene.String(required=True),
        limit=graphene.Int(default_value=10),
        start_date=graphene.String(),
        end_date=graphene.String()
    )

    orders_map = graphene.List(
        OrderMapType,
        business_id=graphene.String(required=True)
    )

    orders_stats = graphene.Field(
        OrderStatsByPurposeType ,
        business_id=graphene.String(required=True),
        purpose=graphene.String(required=True)  # daily, weekly, monthly    
    )

    def resolve_order(self, info, id, business_id):
        return Order.objects.filter(Q(business__hash_id=business_id) | Q(business__tg_hash_id=business_id), id=id).first()

    def resolve_orders(self, info, business_id, filters=None, **kwargs):
        business = Business.objects.filter(Q(hash_id=business_id) | Q(tg_hash_id=business_id)).first()

        qs = Order.objects.filter(business=business)

        if filters:
            if filters.source:
                qs = qs.filter(source=filters.source)
            if filters.source_in:
                qs = qs.filter(source__in=filters.source_in)
            if filters.status:
                qs = qs.filter(status=filters.status)
            if filters.status_in:
                qs = qs.filter(status__in=filters.status_in)
            if filters.platform:
                qs = qs.filter(platform=filters.platform)
            if filters.platform_in:
                qs = qs.filter(platform__in=filters.platform_in)
            if filters.delivery_type:
                qs = qs.filter(delivery=filters.delivery_type)
            if filters.delivery_type_in:
                qs = qs.filter(delivery__in=filters.delivery_type_in)
            if filters.payment_methods:
                qs = qs.filter(payment_method__in=filters.payment_methods)
            if filters.created_at_min:
                qs = qs.filter(created_at__date__gte=datetime.strptime(
                    filters.created_at_min, "%Y-%m-%d").date())
            if filters.created_at_max:
                qs = qs.filter(created_at__date__lte=datetime.strptime(
                    filters.created_at_max, "%Y-%m-%d").date())
            if filters.search:
                qs = qs.filter(
                    Q(id__icontains=filters.search) |
                    Q(user__email__icontains=filters.search) |
                    Q(address__icontains=filters.search)
                )

        if business.multi_operator_mode:
            user_roles = Membership.objects.filter(user=info.context.user)
            user_roles_list = user_roles.values_list("role", flat=True)

            if "COURIER" in user_roles_list:
                courier_role = user_roles.filter(role="COURIER").first()
                qs = qs.filter(Q(operator=courier_role)
                               | Q(status="PROCESSING"))
            elif "OPERATOR" in user_roles_list:
                operator_role = user_roles.filter(role="OPERATOR").first()
                qs = qs.filter(Q(operator=operator_role) | Q(status="NEW"))

        return qs.exclude(delivery="BUSINESS")

    def resolve_my_orders(self, info, business_id, filters=None, **kwargs):
        business = Business.objects.filter(Q(hash_id=business_id) | Q(tg_hash_id=business_id)).first()
        qs = Order.objects.filter(business=business, user=info.context.user)

        if filters:
            if filters.source:
                qs = qs.filter(source=filters.source)
            if filters.source_in:
                qs = qs.filter(source__in=filters.source_in)
            if filters.status:
                qs = qs.filter(status=filters.status)
            if filters.status_in:
                qs = qs.filter(status__in=filters.status_in)    
            if filters.platform:
                qs = qs.filter(platform=filters.platform)
            if filters.platform_in:
                qs = qs.filter(platform__in=filters.platform_in)
            if filters.delivery_type:
                qs = qs.filter(delivery=filters.delivery_type)
            if filters.delivery_type_in:
                qs = qs.filter(delivery__in=filters.delivery_type_in)
            if filters.payment_methods:
                qs = qs.filter(payment_method__in=filters.payment_methods)
            if filters.created_at_min:
                qs = qs.filter(created_at__date__gte=datetime.strptime(
                    filters.created_at_min, "%Y-%m-%d").date())
            if filters.created_at_max:
                qs = qs.filter(created_at__date__lte=datetime.strptime(
                    filters.created_at_max, "%Y-%m-%d").date())
            if filters.search:
                qs = qs.filter(
                    Q(id__icontains=filters.search) |
                    Q(user__email__icontains=filters.search) |
                    Q(address__icontains=filters.search)
                )

        return qs.exclude(delivery="BUSINESS")

    def resolve_business_transactions(self, info, business_id):
        try:
            if not business_id:
                raise GraphQLError("business_id is required.")

            transactions = Order.objects.filter(
                business__hash_id=business_id,
                source=Order.OrderSource.BUSINESS,
                delivery="BUSINESS"
            )

            if not transactions.exists():
                raise GraphQLError("No transactions found for this business.")

            return [
                BusinessTransactionType(
                    who=t.user if t.user else None,
                    where=t.business if t.business else None,
                    why=t.comment or "NOREASON",
                    amount=t.total_amount or 0
                )
                for t in transactions if (t.payment_method in ["PAYME", "CLICK"] and t.is_paid) or (t.payment_method in ["BALANCE"] and t.comment == "SUBSCRIPTION")
            ]

        except Exception as e:
            raise GraphQLError(
                "Something went wrong while resolving transactions.")

    def resolve_order_items(self, info, order_id, business_id, **kwargs):
        return OrderItem.objects.filter(
            Q(order__business__hash_id=business_id) | Q(order__business__tg_hash_id=business_id),
            order__id=order_id   
        ).order_by('id').exclude(delivery="BUSINESS")

    def resolve_orders_by_date(self, info, business_id, start_date=None, end_date=None):
        filters = {}

        if start_date:
            parsed_start = parse_date(start_date)
            if not parsed_start:
                raise GraphQLError("Invalid start_date format")
            filters["created_at__date__gte"] = parsed_start

        if end_date:
            parsed_end = parse_date(end_date)
            if not parsed_end:
                raise GraphQLError("Invalid end_date format")
            filters["created_at__date__lte"] = parsed_end

        try:
            data = list(
                Order.objects
                .filter(business__hash_id=business_id, **filters)
                .exclude(delivery="BUSINESS")
                .annotate(order_date=TruncDate("created_at"))
                .values("order_date", "platform")
                .annotate(count=Count("id"))
            )

            if not data:
                return []

            result = {}

            # Platform mapping to categorize platforms as either desktop or mobile
            platform_mapping = {
                "WEB": "desktop",  # Assuming WEB is accessed from desktop
                "TELEGRAM": "mobile"     # Assuming TG (Telegram) is primarily mobile
                # Add other mappings as needed
            }

            for item in data:
                date = str(item["order_date"])
                original_platform = item["platform"]
                count = item["count"]

                # Map the platform or use the original if no mapping exists
                platform = platform_mapping.get(
                    original_platform, original_platform.lower())

                if date not in result:
                    result[date] = {"date": date, "desktop": 0, "mobile": 0}

                # Check if the mapped platform matches desktop or mobile
                if platform == "desktop":
                    result[date]["desktop"] += count
                elif platform == "mobile":
                    result[date]["mobile"] += count
                # If neither, you could either ignore or add to a separate category

            return list(result.values())

        except FieldError as e:
            raise GraphQLError(f"Query field error: {e}")
        except Exception as e:
            raise GraphQLError(f"Unexpected error: {e}")

    def resolve_top_order_items(self, info, business_id, limit=10, start_date=None, end_date=None):
        filters = {
            "order__business__hash_id": business_id
        }

        if start_date:
            filters["order__created_at__date__gte"] = datetime.strptime(
                start_date, "%Y-%m-%d").date()
        if end_date:
            filters["order__created_at__date__lte"] = datetime.strptime(
                end_date, "%Y-%m-%d").date()

        top_items = (
            OrderItem.objects.filter(**filters)
            .values('product__id', 'product__name_uz', 'product__images')
            .annotate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('price')),
                order_count=Count('order', distinct=True)
            )
            .order_by('-total_quantity')[:limit]
        )

        return [
            TopOrderItemType(
                product_id=item['product__id'],
                product_name=item['product__name_uz'],
                product_images=item['product__images'],
                total_quantity=item['total_quantity'],
                total_revenue=item['total_revenue'],
                order_count=item['order_count']
            )
            for item in top_items
        ]
    
    def resolve_orders_map(self, info, business_id):
        return Order.objects.filter(business__hash_id=business_id, source=Order.OrderSource.CUSTOMER) or []

    def resolve_orders_stats(self, info, business_id, purpose):
        if purpose not in ["daily", "weekly", "monthly", "yearly"]:
            raise GraphQLError("Purpose must be daily, weekly, monthly, or yearly.")

        if purpose == "daily":
            start_date = end_date = datetime.now().date()       
        elif purpose == "weekly":
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif purpose == "monthly":          
            today = datetime.now().date()
            start_date = today.replace(day=1)   # oyning boshi
            end_date = today          
        elif purpose == "yearly":
            today = datetime.now().date()
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)

        stats = Order.objects.filter(
            business__hash_id=business_id,
            created_at__date__range=(start_date, end_date),
            source=Order.OrderSource.CUSTOMER
        ).aggregate(
            web_count=Count("id", filter=Q(platform__iexact="WEB")),
            telegram_count=Count("id", filter=Q(platform__iexact="TELEGRAM"))
        )

        return OrderStatsByPurposeType(
            web=stats["web_count"] or 0,
            telegram=stats["telegram_count"] or 0,
            purpose=purpose
        )