import graphene
from apps.api.graphql.v1.types.auth import UserType, CardType
from apps.api.graphql.v1.types.business import MembershipNode, PermissionType
from apps.business.models import Membership, Role
from graphql_jwt.decorators import login_required
from apps.account.models import Card


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    my_card = graphene.Field(CardType)

    my_roles = graphene.List(MembershipNode, business_id=graphene.String(required=True))
    
    my_permissions = graphene.List(
        PermissionType,
        business_id=graphene.String(required=True)
    )

    def resolve_my_roles(self, info, business_id):
        return Membership.objects.filter(business__hash_id=business_id, user__id=info.context.user.id)

    @login_required
    def resolve_me(self, info):
        user = info.context.user
        if not user or user.is_anonymous:
            raise Exception("Not authenticated")
        return user

    @login_required
    def resolve_my_card(self, info):
        user = info.context.user
        if not user or user.is_anonymous:
            raise Exception("Not authenticated")

        cards = Card.objects.filter(
            user=user, is_default=True, is_verified=True
        )

        if cards.exists():
            return cards.first()
        return None
    
    @login_required
    def resolve_my_permissions(self, info, business_id):
        user = info.context.user

        membership = Membership.objects.filter(
            user=user, business__hash_id=business_id
        ).first()
        if not membership:
            return []

        role_name = membership.role
        if not role_name:
            return []
        
        role = Role.objects.filter(
            business=membership.business,
            name=role_name
        ).first()
        if not role:
            return []
        
        return role.permissions.all()