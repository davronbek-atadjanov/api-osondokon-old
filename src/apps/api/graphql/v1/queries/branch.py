import graphene
from django.db.models import Q
from apps.api.graphql.v1.types.business import BranchType
from apps.business.models import Branch

class Query(graphene.ObjectType):
    branch = graphene.Field(BranchType, id=graphene.ID(required=True), business_id=graphene.String(required=True))
    branches = graphene.List(BranchType, business_id=graphene.String(required=True))
    
    def resolve_branch(self, info, id, business_id):
        return Branch.objects.filter(
            Q(business__hash_id=business_id) | Q(business__tg_hash_id=business_id),
            id=id
        ).first()
    
    def resolve_branches(self, info, business_id):
        return Branch.objects.filter(
            Q(business__hash_id=business_id) | Q(business__tg_hash_id=business_id)
        )