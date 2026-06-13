from graphene_django.types import DjangoObjectType
from apps.product.models import Product, ProductVariant
from graphene.relay import Node
from .category import CategoryType
from apps.api.graphql.v1.types.scalars import JSONScalar
import graphene

class ProductVariantType(DjangoObjectType):
    combination = JSONScalar()  # JSONFieldni string sifatida ko‘rsatamiz

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "combination",
            "price",
            "discount",
            "sale_price",
            "stock",
            "is_active",
        )
    
class NameType(graphene.ObjectType):
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()

class ShortDescriptionType(graphene.ObjectType):
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()

class DescriptionType(graphene.ObjectType):
    uz = graphene.String()  
    ru = graphene.String()
    tr = graphene.String()

class ProductType(DjangoObjectType):
    images = graphene.List(graphene.String)
    attributes = JSONScalar()
    attributes_images = JSONScalar()
    features = JSONScalar()
    category = graphene.Field(CategoryType)
    variants = graphene.List(ProductVariantType)
    names = graphene.Field(NameType)
    name_uz = graphene.String()
    name_ru = graphene.String()
    name_tr = graphene.String()
    short_descriptions = graphene.Field(ShortDescriptionType)
    descriptions = graphene.Field(DescriptionType)
    variants_count = graphene.Int()
    total_stock = graphene.Int()

    class Meta:
        model = Product
        interfaces = (Node,)
        fields = (
            "id",
            "images",
            "attributes",
            "attributes_images",
            "features",
            "is_active",
            "order_count",
            "name_uz",
            "name_ru",
            "name_tr",
        )

    def resolve_names(self, info):
        return {
            "uz": self.name_uz,
            "ru": self.name_ru,
            "tr": self.name_tr
        }       

    def resolve_short_descriptions(self, info): 
        return {
            "uz": self.short_description_uz,
            "ru": self.short_description_ru,
            "tr": self.short_description_tr
        }               

    def resolve_descriptions(self, info):
        return {
            "uz": self.description_uz,
            "ru": self.description_ru,
            "tr": self.description_tr
        }       

    def resolve_images(self, info):
        return self.images or []

    def resolve_variants(self, info):
        return self.productvariant_set.all()

    def resolve_variants_count(self, info):
        return self.productvariant_set.count()    

    def resolve_total_stock(self, info):    
        return sum(variant.stock for variant in self.productvariant_set.all())            