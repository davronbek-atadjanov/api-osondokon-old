import graphene
from graphene_django import DjangoObjectType
from apps.category.models import Category


class CategoryNameType(graphene.ObjectType):
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()


class CategoryType(DjangoObjectType):
    names = graphene.Field(CategoryNameType)
    
    class Meta:
        model = Category
        fields = "__all__"
        interfaces = (graphene.relay.Node,)
    
    def resolve_names(self, info):
        return {
            "uz": self.name_uz,
            "ru": self.name_ru,
            "tr": self.name_tr
        }
