import graphene
from apps.api.graphql.v1.types.business import MembershipNode
from apps.business.models import Membership, Business, Role
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from graphql_relay.node.node import from_global_id

User = get_user_model()


class CreateEmployee(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        full_name = graphene.String(required=True)
        role = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)

    employees = graphene.Field(MembershipNode)

    @transaction.atomic
    def mutate(self, info, business_id, full_name, role, phone_number, password):
        try:

            business = Business.objects.filter(hash_id=business_id).first()
            if not business:
                raise Exception("Business not found.")
            
            if plan := business.plan:
                count = Membership.objects.filter(
                    business=business
                ).exclude(
                    role__in=["OWNER", "CLIENT"]
                ).count()

                if plan == "BASIC" and count >= 3:
                    raise Exception("Basic plan allows up to 2 employees.")

                if plan == "PRO" and count >= 6:
                    raise Exception(
                        "Professional plan allows up to 5 employees.")
            
            existing_user = User.objects.filter(phone_number=phone_number, business_id=0).first()

            if existing_user:
                raise Exception("User with this phone number already exists.")
    

            user_obj = User.objects.create_user(
                phone_number=phone_number,
                full_name=full_name,
                business_id=0,
                password=password,
            )
            user_obj.is_active = True
            user_obj.is_phone_verified = True
            user_obj.save()

                
             # Check membership in this specific business
            existing_membership = Membership.objects.filter(
                user=user_obj,
                business=business
            ).first()

            if existing_membership:
                # Update role if membership exists
                if existing_membership.role != role:
                    existing_membership.role = role
                    try:
                        default_role = Role.objects.get(name=role, business=business)
                        existing_membership.permissions.set(default_role.permissions.all())
                    except Role.DoesNotExist:
                        raise Exception(f"Role '{role}' does not exist in this business.")
                    existing_membership.save()
                return CreateEmployee(employees=existing_membership)

            membership = Membership.objects.create(
                user=user_obj, business=business, role=role)

            try:
                default_role = Role.objects.get(name=role, business=business)
                membership.permissions.set(default_role.permissions.all())
                membership.save()
            except Role.DoesNotExist:       
                raise Exception(f"Role '{role}' does not exist in this business.")

            return CreateEmployee(employees=membership)
        except ObjectDoesNotExist:
            raise Exception("Business not found")


class UpdateEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        full_name = graphene.String()
        role = graphene.String()
        password = graphene.String()

        tag = graphene.String()

    employee = graphene.Field(MembershipNode)

    def mutate(self, info, id, full_name=None, role=None,  tag=None, password=None):
        try:
            membership = Membership.objects.get(pk=from_global_id(id)[1])
            business = membership.business

            # Check plan limits if changing role
            if role and role != membership.role:
                if plan := business.plan:
                    count = Membership.objects.filter(
                        business=business
                    ).exclude(
                        role__in=["OWNER", "CLIENT"]
                    ).count()

                    if plan == "BASIC" and count >= 3:
                        raise Exception("Basic plan allows up to 2 employees.")
                    if plan == "PRO" and count >= 6:
                        raise Exception("Professional plan allows up to 5 employees.")

                # Update role and permissions
                membership.role = role
                try:
                    default_role = Role.objects.get(name=role, business=business)
                    membership.permissions.set(default_role.permissions)
                except Role.DoesNotExist:   
                    raise Exception(f"Role '{role}' does not exist in this business.")

            # Update other fields
            if tag is not None:
                membership.tag = tag
            
            if full_name:
                membership.user.full_name = full_name
            if password:
                membership.user.set_password(password)
            if full_name or password:
                membership.user.save()

            membership.save()
            return UpdateEmployee(employee=membership)

        except ObjectDoesNotExist:
            return UpdateEmployee(employee=None)


class DeleteEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            customer = Membership.objects.get(pk=from_global_id(id)[1])
            customer.delete()

            return DeleteEmployee(success=True)
        except ObjectDoesNotExist:
            return DeleteEmployee(success=False)


class Mutation(graphene.ObjectType):
    add_employee = CreateEmployee.Field()
    update_employee = UpdateEmployee.Field()
    delete_employee = DeleteEmployee.Field()
