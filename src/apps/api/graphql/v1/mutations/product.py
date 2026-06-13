import graphene
from django.db import transaction
from apps.api.graphql.v1.types.product import ProductType
from apps.category.models import Category
from apps.business.models import Business
from apps.product.models import Product, ProductVariant
from graphql_relay.node.node import from_global_id
import json

from django.core.exceptions import ObjectDoesNotExist

class NameInput(graphene.InputObjectType):      
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()

class ShortDescriptionInput(graphene.InputObjectType):
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()

class DescriptionInput(graphene.InputObjectType):   
    uz = graphene.String()
    ru = graphene.String()
    tr = graphene.String()    

class VariantInput(graphene.InputObjectType):   
    combination = graphene.JSONString() # {"color": "red", "storage": "8/128"}
    price = graphene.Int()
    discount = graphene.Int()
    sale_price = graphene.Int()
    stock = graphene.Int()
    is_active = graphene.Boolean()


class CreateProduct(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        category_id = graphene.String(required=True)

        names = NameInput(required=True)
        short_descriptions = ShortDescriptionInput(required=True)
        descriptions = DescriptionInput(required=True)

        attributes = graphene.JSONString(required=False)
        attributes_images = graphene.JSONString(required=False)
        features = graphene.JSONString(required=False)

        images = graphene.List(graphene.String)
        variants = graphene.List(VariantInput)

    product = graphene.Field(ProductType)

    @transaction.atomic
    def mutate(self, info, business_id, category_id, **kwargs):
        try:
            business = Business.objects.get(hash_id=business_id)
            CreateProduct.check_business_product_limit(business)

            category = Category.objects.get(pk=from_global_id(category_id)[1])
            print("business", business)
            print("categoriy", category)
            print("data", kwargs)

            # Product create
            product = Product.objects.create(
                business=business,
                category=category,
                name_uz=kwargs["names"]["uz"],
                name_ru=kwargs["names"].get("ru"),
                name_tr=kwargs["names"].get("tr"),
                short_description_uz=kwargs["short_descriptions"].get("uz", ""),
                short_description_ru=kwargs["short_descriptions"].get("ru", ""),
                short_description_tr=kwargs["short_descriptions"].get("tr", ""),
                description_uz=kwargs["descriptions"].get("uz", ""),
                description_ru=kwargs["descriptions"].get("ru", ""),
                description_tr=kwargs["descriptions"].get("tr", ""),
                attributes=kwargs["attributes"],
                attributes_images=kwargs["attributes_images"],
                features=kwargs["features"] if kwargs.get("features") else None,
                images=kwargs.get("images", []) ,
            )

            variants = kwargs.get("variants", [])
            if variants:
                variants = [
                    ProductVariant(
                        product=product,
                        combination=v["combination"],
                        price=v["price"],
                        discount=v["discount"],
                        sale_price=v["sale_price"],
                        stock=v["stock"],
                        is_active=v["is_active"],
                    )
                    for v in variants
                ]
                ProductVariant.objects.bulk_create(variants)  
            return CreateProduct(product=product)

        except Business.DoesNotExist:
            raise Exception("Business not found")
        except Category.DoesNotExist:
            raise Exception("Category not found")

    @staticmethod
    def check_business_product_limit(business):
        if plan := business.plan:
            count = Product.objects.filter(business=business).count()

            if plan == "BASIC" and count >= 250:
                raise Exception("Basic plan allows up to 250 products.")

            if plan == "PRO" and count >= 5000:
                raise Exception("Professional plan allows up to 5000 products.")
        else:
            raise Exception("Business plan not found")

class UpdateVariantInput(graphene.InputObjectType): 
    id = graphene.String()  # Optional, for existing variants     
    combination = graphene.JSONString() # {"color": "red", "storage": "8/128"}
    price = graphene.Int()
    discount = graphene.Int()
    sale_price = graphene.Int()
    stock = graphene.Int()
    is_active = graphene.Boolean()


class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        category_id = graphene.String(required=False)

        names = NameInput(required=False)
        short_descriptions = ShortDescriptionInput(required=False)
        descriptions = DescriptionInput(required=False)

        attributes = graphene.JSONString(required=False)
        attributes_images = graphene.JSONString(required=False)
        features = graphene.JSONString(required=False)

        images = graphene.List(graphene.String)
        variants = graphene.List(UpdateVariantInput)

    product = graphene.Field(ProductType)

    @transaction.atomic
    def mutate(self, info, id, category_id=None, **kwargs):
        try:
            product_id = from_global_id(id)[1]
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            raise Exception("Product not found")

        # category update
        if category_id:
            try:
                product.category = Category.objects.get(pk=from_global_id(category_id)[1])
            except ObjectDoesNotExist:
                raise Exception("Category not found")

        # mapping for translations
        translations_map = {
            "names": {"uz": "name_uz", "ru": "name_ru", "tr": "name_tr"},
            "short_descriptions": {"uz": "short_description_uz", "ru": "short_description_ru", "tr": "short_description_tr"},
            "descriptions": {"uz": "description_uz", "ru": "description_ru", "tr": "description_tr"},
        }

        for field, lang_map in translations_map.items():
            data = kwargs.get(field)
            if data:
                for lang, attr in lang_map.items():
                    setattr(product, attr, data.get(lang, getattr(product, attr)))

        # JSON fields
        json_fields = ["attributes", "attributes_images", "features"]
        for field in json_fields:
            if kwargs.get(field):
                setattr(product, field, kwargs[field])

        # simple list fields
        if "images" in kwargs:
            product.images = kwargs["images"]

        # handle SKU list
        variants = kwargs.get("variants")
        if variants:
            for v in variants:
                UpdateProduct._update_or_create_variant(product, v)

        product.save()
        return UpdateProduct(product=product)

    @staticmethod
    def _update_or_create_variant(product, data):
        """Helper function to update or create SKU"""
        if data.get("id"):
            try:
                sku_instance = ProductVariant.objects.get(
                    id=data["id"], product=product
                )
            except ObjectDoesNotExist:
                raise Exception(f"SKU with id {data['id']} not found for this product")

            for key, value in data.items():
                if key == "id":
                    continue
                if key == "combination":
                    setattr(sku_instance, key, value)
                else:
                    setattr(sku_instance, key, value)
            sku_instance.save()
        else:
            ProductVariant.objects.create(
                product=product,
                combination=data["combination"],
                price=data["price"],
                discount=data["discount"],
                sale_price=data["sale_price"],
                stock=data["stock"],
                is_active=data["is_active"],
            )


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            id = from_global_id(id)[1]
            product = Product.objects.get(pk=id)
            product.delete()
            return DeleteProduct(success=True)
        except ObjectDoesNotExist:
            return DeleteProduct(success=False)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
