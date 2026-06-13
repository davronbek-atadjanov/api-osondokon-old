import graphene

from apps.api.graphql.v1.types.business import BranchType
from apps.business.models import Business, Branch
from django.core.exceptions import ObjectDoesNotExist

class CreateBranch(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        name = graphene.String(required=True)
        address = graphene.String(required=True)
        phone = graphene.String()
        email = graphene.String()
        latitude = graphene.String(required=True)
        longitude = graphene.String(required=True)
        is_main_branch = graphene.Boolean()
        enabled = graphene.Boolean()
        delivery_enabled = graphene.Boolean()
        pickup_enabled = graphene.Boolean()
    
    branch = graphene.Field(BranchType)
    
    def mutate(self, info, business_id, name, address, phone, latitude, longitude, 
               email=None, is_main_branch=False, enabled=True, delivery_enabled=False, pickup_enabled=True):
        try:
            business = Business.objects.get(hash_id=business_id)
            if plan := business.plan:
                count = Branch.objects.filter(business=business).count()
                
                if plan == "BASIC" and count > 2:
                    raise Exception("Basic plan allows up to 2 branches.")
                
                if plan == "PRO" and count >= 10:
                    raise Exception("Professional plan allows up to 5 branches.")
                
            branch = Branch.objects.create(
                business=business, name=name, address=address, phone=phone, email=email,
                latitude=latitude, longitude=longitude, is_main_branch=is_main_branch,
                enabled=enabled, delivery_enabled=delivery_enabled, pickup_enabled=pickup_enabled
            )
            return CreateBranch(branch=branch)
        except ObjectDoesNotExist:
            raise Exception("Business not found")

class UpdateBranch(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        address = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        latitude = graphene.String()
        longitude = graphene.String()
        is_main_branch = graphene.Boolean()
        enabled = graphene.Boolean()
        delivery_enabled = graphene.Boolean()
        pickup_enabled = graphene.Boolean()
    
    branch = graphene.Field(BranchType)
    
    def mutate(self, info, id, **kwargs):
        try:
            branch = Branch.objects.get(pk=id)
        except ObjectDoesNotExist:
            raise Exception("Branch not found")
        
        for key, value in kwargs.items():
            if value is not None:
                setattr(branch, key, value)
        
        branch.save()
        return UpdateBranch(branch=branch)

class DeleteBranch(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        try:
            branch = Branch.objects.get(pk=id)
            branch.delete()
            return DeleteBranch(success=True)
        except ObjectDoesNotExist:
            return DeleteBranch(success=False)

class Mutation(graphene.ObjectType):
    create_branch = CreateBranch.Field()
    update_branch = UpdateBranch.Field()
    delete_branch = DeleteBranch.Field()
