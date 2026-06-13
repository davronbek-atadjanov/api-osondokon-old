import graphene
from django.core.exceptions import ValidationError
from apps.delivery.models import DeliveryMethod, PickupMethod, DeliveryType
from apps.business.models import Business, Branch
from apps.api.graphql.v1.types.delivery import DeliveryMethodType, PickupMethodType

class CreateDeliveryMethod(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        type = graphene.String(required=True)
        max_km = graphene.Int()
        country = graphene.String()
        cities = graphene.String()
        price = graphene.Float()
        description = graphene.String()
        initial_km = graphene.Int()
        initial_km_price = graphene.Float()
        every_km_price = graphene.Float()
        is_active = graphene.Boolean()
        branches = graphene.List(graphene.ID)
        min_price = graphene.Float()
        estimated_shipping_time = graphene.Int()

    delivery_method = graphene.Field(DeliveryMethodType)

    def mutate(self, info, business_id, type, branches=None, **kwargs):
        try:
            business = Business.objects.get(hash_id=business_id)

            delivery_method = DeliveryMethod.objects.create(
                business=business, type=type, **kwargs)
            
            if branches is not None:
                delivery_method.branches.set(Branch.objects.filter(id__in=branches))
            delivery_method.save()

            return CreateDeliveryMethod(delivery_method=delivery_method)
        except Exception as e:
            return CreateDeliveryMethod(delivery_method=None)


class UpdateDeliveryMethod(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        type = graphene.String()
        max_km = graphene.Int()
        country = graphene.String()
        cities = graphene.String()
        price = graphene.Float()
        description = graphene.String()
        initial_km = graphene.Int()
        initial_km_price = graphene.Float()
        every_km_price = graphene.Float()
        is_active = graphene.Boolean()
        branches = graphene.List(graphene.ID)
        min_price = graphene.Float()
        estimated_shipping_time = graphene.Int()

    delivery_method = graphene.Field(DeliveryMethodType)

    def mutate(self, info, id, branches=None, **kwargs):
        delivery_method = DeliveryMethod.objects.get(pk=id)

        # Avval validatsiya qilamiz
        delivery_type = kwargs.get("type", delivery_method.type)

        if delivery_type == DeliveryType.FREE:
            if kwargs.get("price") or kwargs.get("initial_km_price") or kwargs.get("every_km_price"):
                raise ValidationError("Free delivery cannot have any price fields.")

        elif delivery_type == DeliveryType.FIXED_PRICE:
            if not kwargs.get("price") and not delivery_method.price:
                raise ValidationError("Fixed price delivery requires `price` field.")
            if kwargs.get("initial_km") or kwargs.get("initial_km_price") or kwargs.get("every_km_price"):
                raise ValidationError("Fixed price delivery cannot have km-based fields.")

        elif delivery_type == DeliveryType.FLEXIBLE_PRICE:
            initial_km = kwargs.get("initial_km", delivery_method.initial_km)
            initial_km_price = kwargs.get("initial_km_price", delivery_method.initial_km_price)
            every_km_price = kwargs.get("every_km_price", delivery_method.every_km_price)

            if not all([initial_km, initial_km_price, every_km_price]):
                raise ValidationError("Flexible price delivery requires `initial_km`, `initial_km_price`, and `every_km_price`.")

        # Endi qiymatlarni set qilamiz
        for key, value in kwargs.items():
            setattr(delivery_method, key, value)

        if branches is not None:
            delivery_method.branches.set(branches)

        delivery_method.save()
        return UpdateDeliveryMethod(delivery_method=delivery_method)


class DeleteDeliveryMethod(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        DeliveryMethod.objects.filter(pk=id).delete()
        return DeleteDeliveryMethod(success=True)


class CreatePickupMethod(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        branch_ids = graphene.List(graphene.ID)

    pickup_method = graphene.Field(PickupMethodType)

    def mutate(self, info, business_id, branch_ids=[]):
        try:
            business = Business.objects.get(hash_id=business_id)
            pickup_method = PickupMethod.objects.create(business=business)
            pickup_method.branches.set(branch_ids)
            return CreatePickupMethod(pickup_method=pickup_method)
        except Business.DoesNotExist:
            raise Exception("Business not found")


class UpdatePickupMethod(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        branch_ids = graphene.List(graphene.ID)

    pickup_method = graphene.Field(PickupMethodType)

    def mutate(self, info, id, branch_ids=[]):
        pickup_method = PickupMethod.objects.get(pk=id)
        pickup_method.branches.set(branch_ids)
        pickup_method.save()
        return UpdatePickupMethod(pickup_method=pickup_method)


class DeletePickupMethod(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        PickupMethod.objects.filter(pk=id).delete()
        return DeletePickupMethod(success=True)


class Mutation(graphene.ObjectType):
    create_delivery_method = CreateDeliveryMethod.Field()
    update_delivery_method = UpdateDeliveryMethod.Field()
    delete_delivery_method = DeleteDeliveryMethod.Field()
    create_pickup_method = CreatePickupMethod.Field()
    update_pickup_method = UpdatePickupMethod.Field()
    delete_pickup_method = DeletePickupMethod.Field()
