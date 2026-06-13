import graphene
from graphene_django.types import DjangoObjectType
from graphene import relay
from apps.business.models import (
    Business, BusinessField, Permission,
    Membership, Role, Subscription, Branch
)
from .scalars import JSONScalar

class PaymentMethodsType(graphene.ObjectType):
    card = graphene.Boolean()
    cash = graphene.Boolean()
    click = graphene.Boolean()
    payme = graphene.Boolean()

class BusinessSmsLimitType(graphene.ObjectType):
    used = graphene.Int()
    max = graphene.Int()
    
class BusinessType(DjangoObjectType):
    payment_methods = JSONScalar()
    platforms = JSONScalar()
    languages = JSONScalar()
    social_info = JSONScalar()
    working_days = JSONScalar()
    
    plan = graphene.String()
    plan_expiry = graphene.String()

    sms_limit = graphene.Field(BusinessSmsLimitType)    
    payment_methods_status = graphene.Field(PaymentMethodsType)

    def resolve_plan(self, info):
        return self.plan
    
    def resolve_sms_limit(self, info):
        from django.core.cache import cache
        from apps.api.helper import PLAN_LIMITS, get_sms_cache_key

        if not self.plan:
            return BusinessSmsLimitType(
                used=0,
                max=0,
            )

        cache_key = get_sms_cache_key(self.id)
        used_sms = cache.get(cache_key, 0)
        max_sms = PLAN_LIMITS.get(self.plan, 0)

        return BusinessSmsLimitType(
            used=used_sms,
            max=max_sms,
        )
    
    def resolve_payment_methods_status(self, info):
        data = self.payment_methods or {}

        def get_enabled(method):
            return data.get(method, {}).get("enabled", False)

        return PaymentMethodsType(
            card=get_enabled("card"),
            cash=get_enabled("cash"),
            click=get_enabled("click"),
            payme=get_enabled("payme"),
        )
    
    class Meta:
        model = Business
        fields = "__all__"  # Exclude payment_methods from this type
    
class MyBusinessType(DjangoObjectType):
    payment_methods = JSONScalar()
    platforms = JSONScalar()
    languages = JSONScalar()
    social_info = JSONScalar()
    working_days = JSONScalar()
    
    plan = graphene.String()
    sms_limit = graphene.Field(BusinessSmsLimitType)    
    plan_expiry = graphene.String()
    
    def resolve_plan(self, info):
        return self.plan
    
    def resolve_sms_limit(self, info):
        from django.core.cache import cache
        from apps.api.helper import PLAN_LIMITS, get_sms_cache_key

        if not self.plan:
            return BusinessSmsLimitType(
                used=0,
                max=0,
            )

        cache_key = get_sms_cache_key(self.id)
        used_sms = cache.get(cache_key, 0)
        max_sms = PLAN_LIMITS.get(self.plan, 0)

        return BusinessSmsLimitType(
            used=used_sms,
            max=max_sms,
        )

    
    class Meta:
        model = Business
        fields = "__all__"


class BusinessFieldType(DjangoObjectType):
    class Meta:
        model = BusinessField
        fields = "__all__"


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = "__all__"

class MembershipType(DjangoObjectType):
    class Meta:
        model = Membership
        fields = "__all__"

class MembershipNode(DjangoObjectType):
    class Meta:
        model = Membership
        fields = "__all__"
        interfaces = (relay.Node,)

class RoleType(DjangoObjectType):
    class Meta:
        model = Role
        fields = "__all__"
        interfaces = (relay.Node,)

class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription
        fields = "__all__"

class BranchType(DjangoObjectType):
    class Meta:
        model = Branch

class TrafficCountType(graphene.ObjectType):
    web = graphene.Int()
    telegram = graphene.Int()
    purpose = graphene.String()
