import graphene

from apps.api.graphql.v1.types.category import CategoryType
from apps.category.models import Category
from apps.business.models import Business
from graphql_relay.node.node import from_global_id

from django.core.exceptions import ObjectDoesNotExist


class CategoryNameInput(graphene.InputObjectType):
    uz = graphene.String(required=True)
    ru = graphene.String()
    tr = graphene.String()


class CreateCategory(graphene.Mutation):
    class Arguments:
        names = CategoryNameInput(required=True)
        logo = graphene.String()
        picture = graphene.String()
        business_id = graphene.String(required=True)
        parent_id = graphene.String()

    category = graphene.Field(CategoryType)

    def mutate(self, info, names, business_id, logo=None, picture=None, parent_id=None):
        try:
            business = Business.objects.get(hash_id=business_id)
            
            parent = None
            if parent_id:
                parent_db_id = from_global_id(parent_id)[1]
                parent = Category.objects.get(pk=parent_db_id, business=business)
            
            category = Category.objects.create(
                name_uz=names.get('uz'),
                name_ru=names.get('ru'),
                name_tr=names.get('tr'),
                logo=logo,
                picture=picture,
                business=business,
                parent=parent
            )
            return CreateCategory(category=category)
        except ObjectDoesNotExist:
            raise Exception("Business or parent category not found")


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        names = CategoryNameInput()
        logo = graphene.String()
        picture = graphene.String()
        parent_id = graphene.String()

    category = graphene.Field(CategoryType)

    def mutate(self, info, id, names=None, logo=None, picture=None, parent_id=None):
        try:
            id = from_global_id(id)[1]
            category = Category.objects.get(pk=id)
            
            if parent_id:
                parent_db_id = from_global_id(parent_id)[1]
                parent = Category.objects.get(
                    pk=parent_db_id, 
                    business=category.business
                )
                category.parent = parent
            elif parent_id == '':
                category.parent = None

            if names:
                if names.get('uz'):
                    category.name_uz = names.get('uz')
                if names.get('ru') is not None:
                    category.name_ru = names.get('ru')
                if names.get('tr') is not None:
                    category.name_tr = names.get('tr')
                    
            if logo is not None:
                category.logo = logo
            if picture is not None:
                category.picture = picture

            category.save()
            return UpdateCategory(category=category)
            
        except ObjectDoesNotExist:
            raise Exception("Category not found")


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            id = from_global_id(id)[1]
            category = Category.objects.get(pk=id)
            category.delete()
            return DeleteCategory(success=True)
        except ObjectDoesNotExist:
            return DeleteCategory(success=False)


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
