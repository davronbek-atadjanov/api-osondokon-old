import graphene
from apps.api.graphql.v1.types.business import MembershipNode
from apps.business.models import Membership, Business

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from graphql_relay.node.node import from_global_id


User = get_user_model()


class CreateClient(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        full_name = graphene.String(required=True)
        password = graphene.String(required=True)

        phone_number = graphene.String()
        email = graphene.String()
        tag = graphene.String()

    client = graphene.Field(MembershipNode)

    def mutate(self, info, business_id, full_name, password, phone_number=None, tag=None, email=None):
        business = Business.objects.get(hash_id=business_id)

        if not (phone_number or email):
            raise Exception("Phone number or email is required")
        
        username = phone_number if phone_number else email
        user, created = User.objects.get_or_create(
            full_name=full_name,
            email=email if email else None,
            username=username,
            phone_number=phone_number,
            is_active=True,
        )

        user.set_password(password)
        user.save()

        membership, created = Membership.objects.get_or_create(
            user=user,
            business=business,
            role="CLIENT",
            tag=tag,
        )
        return CreateClient(client=membership)


class UpdateClient(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        full_name = graphene.String()

        phone_number = graphene.String()
        email = graphene.String()
        password = graphene.String()
        tag = graphene.String()

    client = graphene.Field(MembershipNode)

    def mutate(self, info, id, full_name=None, phone_number=None, email=None, password=None, tag=None):
        try:
            membership = Membership.objects.get(pk=from_global_id(id)[1])

            membership.tag = tag
            membership.save()

            if full_name:
                membership.user.full_name = full_name

            if phone_number:
                membership.user.phone_number = phone_number

            if email:
                membership.user.email = email
            
            if password:
                membership.user.set_password(password)

            membership.user.save()
            return UpdateClient(client=membership)
        except ObjectDoesNotExist:
            return UpdateClient(client=None)


class DeleteClient(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            client = Membership.objects.get(pk=from_global_id(id)[1])
            client.delete()

            return DeleteClient(success=True)
        except ObjectDoesNotExist:
            return DeleteClient(success=False)


class Mutation(graphene.ObjectType):
    add_client = CreateClient.Field()
    update_client = UpdateClient.Field()
    delete_client = DeleteClient.Field()
