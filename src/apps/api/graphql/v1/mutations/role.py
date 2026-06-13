import graphene

from apps.api.graphql.v1.types.business import RoleType
from apps.business.models import Business, Permission, Business, Role
from graphql_relay.node.node import from_global_id


class MenuPermissionInput(graphene.InputObjectType):
    menuName = graphene.String(required=True)
    can_view = graphene.Boolean()
    can_edit = graphene.Boolean()
    can_delete = graphene.Boolean()


class CreateRole(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        is_default = graphene.Boolean()
        menu_permissions = graphene.List(MenuPermissionInput)

    role = graphene.Field(RoleType)

    def mutate(self, info, business_id, name, description="", is_default=False, menu_permissions=[]):
        business = Business.objects.get(hash_id=business_id)
        role = Role.objects.create(
            business=business,
            name=name,
            description=description,
            is_default=is_default
        )
        if menu_permissions is not None:
            input_menu_names = set()

            # Track new permissions to add
            new_permissions = []

            for menu_perm in menu_permissions:
                input_menu_names.add(menu_perm.menuName)

                # Check if permission exists for THIS role specifically
                try:
                    # Get permission tied to this role with matching menu_name
                    permission = role.permissions.get(menu_name=menu_perm.menuName)
                    # Update existing permission
                    permission.can_view = menu_perm.can_view
                    permission.can_edit = menu_perm.can_edit
                    permission.can_delete = menu_perm.can_delete
                    permission.save()
                except Permission.DoesNotExist:
                    # Create new permission unique to this role
                    new_permission = Permission.objects.create(
                        menu_name=menu_perm.menuName,
                        can_view=menu_perm.can_view,
                        can_edit=menu_perm.can_edit,
                        can_delete=menu_perm.can_delete
                    )
                    new_permissions.append(new_permission)

            # Add new permissions to role
            role.permissions.add(*new_permissions)

            # Remove permissions not in the input
            role.permissions.exclude(menu_name__in=input_menu_names).delete()
        return CreateRole(role=role)


class UpdateRole(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
        is_default = graphene.Boolean()
        menu_permissions = graphene.List(MenuPermissionInput)

    role = graphene.Field(RoleType)

    def mutate(self, info, id, name=None, description=None, is_default=None, menu_permissions=None):
        role = Role.objects.get(id=from_global_id(id)[1])

        if name is not None:
            role.name = name
        if description is not None:
            role.description = description
        if is_default is not None:
            role.is_default = is_default

        if menu_permissions is not None:
            input_menu_names = set()

            # Track new permissions to add
            new_permissions = []

            for menu_perm in menu_permissions:
                input_menu_names.add(menu_perm.menuName)

                # Check if permission exists for THIS role specifically
                try:
                    # Get permission tied to this role with matching menu_name
                    permission = role.permissions.get(menu_name=menu_perm.menuName)
                    # Update existing permission
                    permission.can_view = menu_perm.can_view
                    permission.can_edit = menu_perm.can_edit
                    permission.can_delete = menu_perm.can_delete
                    permission.save()
                except Permission.DoesNotExist:
                    # Create new permission unique to this role
                    new_permission = Permission.objects.create(
                        menu_name=menu_perm.menuName,
                        can_view=menu_perm.can_view,
                        can_edit=menu_perm.can_edit,
                        can_delete=menu_perm.can_delete
                    )
                    new_permissions.append(new_permission)

            # Add new permissions to role
            role.permissions.add(*new_permissions)

            # Remove permissions not in the input
            role.permissions.exclude(menu_name__in=input_menu_names).delete()

        role.save()
        return UpdateRole(role=role)


class DeleteRole(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            role = Role.objects.get(id=from_global_id(id)[1])
            role.delete()
            return DeleteRole(success=True)
        except Role.DoesNotExist:
            return DeleteRole(success=False)


class Mutation(graphene.ObjectType):
    create_role = CreateRole.Field()
    update_role = UpdateRole.Field()
    delete_role = DeleteRole.Field()
