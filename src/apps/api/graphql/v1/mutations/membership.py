import graphene
from apps.api.graphql.v1.types.business import MembershipType, RoleType
from apps.api.graphql.v1.types.auth import UserType
from apps.business.models import Permission, Membership, Role

from graphql import GraphQLError
from django.contrib.auth import get_user_model


User = get_user_model()

class PermissionInput(graphene.InputObjectType):
    menu_name = graphene.String(required=True)
    can_view = graphene.Boolean(default_value=False)
    can_edit = graphene.Boolean(default_value=False)
    can_delete = graphene.Boolean(default_value=False)

class UserInput(graphene.InputObjectType):
    email = graphene.String()
    phone_number = graphene.String()
    full_name = graphene.String(required=True)
    is_staff = graphene.Boolean(default_value=False)

class MembershipInput(graphene.InputObjectType):
    user_id = graphene.ID(required=True)
    business_id = graphene.ID(required=True)
    role_id = graphene.ID(required=True)

class RoleInput(graphene.InputObjectType):
    business_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    is_default = graphene.Boolean(default_value=False)
    permissions = graphene.List(PermissionInput)


class CreateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, input):
        user = User(
            email=input.email,
            phone_number=input.phone_number,
            full_name=input.full_name,
            is_staff=input.is_staff
        )
        user.save()
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = UserInput(required=True)

    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, id, input):
        user = User.objects.get(pk=id)
        for field, value in input.items():
            setattr(user, field, value)
        user.save()
        return UpdateUser(user=user)

class AddEmployee(graphene.Mutation):
    class Arguments:
        input = MembershipInput(required=True)

    membership = graphene.Field(MembershipType)

    @classmethod
    def mutate(cls, root, info, input):
        membership = Membership(
            user_id=input.user_id,
            business_id=input.business_id,
            role_id=input.role_id
        )
        membership.save()
        return AddEmployee(membership=membership)

class UpdateEmployeeRole(graphene.Mutation):
    class Arguments:
        membership_id = graphene.ID(required=True)
        new_role_id = graphene.ID(required=True)

    membership = graphene.Field(MembershipType)

    @classmethod
    def mutate(cls, root, info, membership_id, new_role_id):
        membership = Membership.objects.get(pk=membership_id)
        membership.role_id = new_role_id
        membership.save()
        return UpdateEmployeeRole(membership=membership)

class CreateRole(graphene.Mutation):
    class Arguments:
        input = RoleInput(required=True)

    role = graphene.Field(RoleType)

    @classmethod
    def mutate(cls, root, info, input):
        role = Role(
            business_id=input.business_id,
            name=input.name,
            description=input.description,
            is_default=input.is_default
        )
        role.save()
        
        # Add permissions
        for perm_input in input.permissions:
            perm, _ = Permission.objects.get_or_create(
                menu_name=perm_input.menu_name,
                defaults={
                    'can_view': perm_input.can_view,
                    'can_edit': perm_input.can_edit,
                    'can_delete': perm_input.can_delete
                }
            )
            role.permissions.add(perm)
            
        return CreateRole(role=role)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    # create_role = CreateRole.Field()