import json
from urllib.parse import urljoin

import graphene
from graphql import GraphQLError
from graphql_relay import from_global_id

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from payme import Payme
from click_up import ClickUp

from apps.api.graphql.v1.types.order import OrderType
from apps.order.models import Order, OrderItem
from apps.order.utils import detect_platform
from apps.product.models import Product, ProductVariant
from apps.business.models import Business, Branch, Membership


User = get_user_model()

def get_payme_id(payment_methods_str):    
    try:
        payme = payment_methods_str.get("payme", {})
        if payme.get("enabled") and payme.get("merchant_id") :
            return payme["merchant_id"]
    except (json.JSONDecodeError, TypeError):
        pass
    return None

def get_click_api_key(payment_methods_str):
    try:
        click = payment_methods_str.get("click", {})
        if click.get("enabled") and click.get("service_id") and click.get("merchant_id"):
            return {
                "service_id": click["service_id"],
                "merchant_id": click["merchant_id"] 
            }
    except (json.JSONDecodeError, TypeError):
        pass
    return None

def get_return_url(platforms: dict | str) -> str | None:
    try:
        if isinstance(platforms, str):
            return_config = json.loads(platforms)
        else:
            return_config = platforms

        web_config = return_config.get("web", {})
        if not web_config.get("enabled"):
            return None

        if web_config.get("domainType") == "custom":
            domain = web_config.get("customDomain")
        elif web_config.get("domainType") == "subdomain":
            domain = f"{web_config.get('subdomain')}.osonstore.uz"
        else:
            return None

        return urljoin(f"https://{domain}", "/profile/orders")
    except Exception as e:
        print(f"Exception in get_return_url: {str(e)}")
        return None

class OrderItemInput(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    variant_id = graphene.String()  # Optional, for product variants
    quantity = graphene.Int()

class CreateOrderInput(graphene.InputObjectType):
    business_id = graphene.String(required=True)
    customer_name = graphene.String(required=True)
    customer_phone = graphene.String(required=True)
    delivery_type = graphene.String(required=True)  # "PICKUP" or "DELIVERY"
    # Required if delivery_type is "PICKUP"
    branch_id = graphene.ID()
    # Required if delivery_type is "DELIVERY"
    address = graphene.String()
    payment_method = graphene.String(required=True)  # "CASH" or "CARD"
    items = graphene.List(graphene.NonNull(OrderItemInput), required=True)

    platform = graphene.String(default_value="WEB")
    comment = graphene.String()

class MakeOrderInput(graphene.InputObjectType):
    business_id = graphene.String(required=True)
    delivery_type = graphene.String(required=True)  # "PICKUP" or "DELIVERY"
    # Required if delivery_type is "PICKUP"
    branch_id = graphene.ID()
    # Required if delivery_type is "DELIVERY"
    address = graphene.String()
    payment_method = graphene.String(required=True)  # "CASH" or "CARD"
    items = graphene.List(graphene.NonNull(OrderItemInput), required=True)

    platform = graphene.String(default_value="WEB")
    comment = graphene.String()


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    payment_link = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()
    
    @classmethod
    def mutate(cls, root, info, input):
        try:
            # 1. Validate business
            business = Business.objects.filter(
                Q(hash_id=input.business_id) | Q(tg_hash_id=input.business_id)
            ).first()
            if not business:
                raise CreateOrder(
                    success=False,
                    message="Business not found"
                    )

            # 2. Validate delivery type
            if input.delivery_type not in ["PICKUP", "DELIVERY"]:
                raise CreateOrder(
                    success=False,
                    message="Invalid delivery type. Must be PICKUP or DELIVERY"
                )       

            # 3. Validate address/branch based on delivery type
            if input.delivery_type == "DELIVERY":
                if not input.address:
                    raise CreateOrder(
                        success=False,
                        message="Address is required for delivery orders"
                    )
                try:
                    address = json.loads(input.address)
                except Exception:
                    raise CreateOrder(  
                        success=False,
                        message="Invalid address format. Must be a valid JSON string"
                    )
                
                branch = None
            else:
                if not input.branch_id:
                    raise CreateOrder(
                        success=False,
                        message="Branch ID is required for pickup orders"
                    )
                try:
                    branch = Branch.objects.get(id=input.branch_id)
                except Branch.DoesNotExist:
                    raise CreateOrder(
                        success=False,
                        message="Branch not found"
                    )
                address = None

            
            customer, _ = User.objects.get_or_create(
                phone_number=input.customer_phone,
                defaults={'full_name': input.customer_name}
            )

            # 5. Create order
            order_kwargs = {
                "user": customer,
                "business": business,
                "branch": branch,
                "delivery": input.delivery_type,
                "payment_method": input.payment_method.upper(),
                "platform": input.platform,
                "comment": input.comment,
                "status": "NEW",
            }

            if address is not None:
                order_kwargs["address"] = address

            order = Order.objects.create(**order_kwargs)
            # 6. Create order items
            total_amount = 0
            for item_input in input.items:
                quantity = item_input.quantity or 1
                if quantity <= 0:
                    raise Exception("Quantity must be greater than 0")

                try:
                    product_id = from_global_id(item_input.product_id)[1]
                    product = Product.objects.get(id=product_id, business=business)
                except Product.DoesNotExist:
                    raise Exception(
                        f"Product with ID {item_input.product_id} not found")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total_amount += product.price * quantity

            # 7. Finalize order
            order.total_amount = total_amount
            order.save()

            Membership.objects.get_or_create(
                user=info.context.user,
                business=business,
            )
            
            # 9. Generate payment link
            if order.payment_method == "PAYME":
                business_payment_methods = business.payment_methods 
                payme_id = get_payme_id(business_payment_methods)
                if not business_payment_methods and not payme_id:
                    raise Exception("Payme payment method is not configured for this business")
                 
                payme = Payme(payme_id=payme_id)
                pay_link = payme.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_amount,
                    return_url=get_return_url(business.platforms) or settings.PAYME_RETURN_URL
                )

            elif order.payment_method == "CLICK":
                if not business.payment_methods and not get_click_api_key(business.payment_methods):
                    raise Exception("Click payment method is not configured for this business")
                click_data = get_click_api_key(business.payment_methods)
                click_up = ClickUp(
                        service_id=click_data["service_id"],
                        merchant_id=click_data["merchant_id"]
                    )
                pay_link = click_up.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_amount,
                    return_url=get_return_url(business.platforms) or settings.CLICK_RETURN_URL  
                )
            else:
                pay_link = None

            return CreateOrder(order=order, payment_link=pay_link)

        except Exception as e:
            raise Exception(f"Order creation failed: {str(e)}")
        
class MakeOrder(graphene.Mutation):
    class Arguments:
        input = MakeOrderInput(required=True)

    order = graphene.Field(OrderType)
    payment_link = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        try:
            # 1. Validate business
            business = Business.objects.filter(
                Q(hash_id=input.business_id) | Q(tg_hash_id=input.business_id)
            ).first()
            if not business:
                raise Exception("Business not found")

            # 2. Validate delivery type
            if input.delivery_type not in ["PICKUP", "DELIVERY"]:
                raise Exception(
                    "Invalid delivery type. Must be PICKUP or DELIVERY")

            # 3. Validate address/branch based on delivery type
            if input.delivery_type == "DELIVERY":
                if not input.address:
                    raise Exception("Address is required for delivery orders")
                try:
                    address = json.loads(input.address)
                except Exception:
                    raise Exception(
                        "Invalid address format. Must be a valid JSON string")
                branch = None
            else:
                if not input.branch_id:
                    raise Exception("Branch ID is required for pickup orders")
                try:
                    branch = Branch.objects.get(id=input.branch_id)
                except Branch.DoesNotExist:
                    raise Exception("Branch not found")
                address = None

            # 4. Detect platform    
            platform = detect_platform(info.context)
            # 5. Create order
            order_kwargs = {
                "user": info.context.user,
                "business": business,
                "branch": branch,
                "delivery": input.delivery_type,
                "payment_method": input.payment_method.upper(),
                "platform": platform,
                "comment": input.comment,
                "status": "NEW",
            }

            # address faqat DELIVERY bo‘lsa qo‘shiladi
            if address is not None:
                order_kwargs["address"] = address

            order = Order.objects.create(**order_kwargs)

            # 6. Create order items
            total_amount = 0
            for item_input in input.items:
                quantity = item_input.quantity or 1
                if quantity <= 0:
                    raise Exception("Quantity must be greater than 0")

                try:
                    product_id = from_global_id(item_input.product_id)[1]
                    product = Product.objects.get(id=product_id, business=business)                
                except Product.DoesNotExist:
                    raise Exception(
                        f"Product with ID {item_input.product_id} not found")
                variant = None
                if item_input.variant_id:
                    try:
                        variant = ProductVariant.objects.get(id=item_input.variant_id, product=product)
                    except ProductVariant.DoesNotExist:
                        raise Exception(f"Variant with ID {item_input.variant_id} not found for this product")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    price=product.price if not variant else variant.price,
                )
                total_amount += (product.price if not variant else variant.sale_price) * quantity

            Membership.objects.get_or_create(
                user=info.context.user,
                business=business,
            )

            # 7. Finalize order
            order.total_amount = total_amount
            order.save()

            #8. Generate payment link
            if order.payment_method == "PAYME":
                business_payment_methods = business.payment_methods 
                payme_id = get_payme_id(business_payment_methods)
                if not business_payment_methods and not payme_id:
                    raise Exception("Payme payment method is not configured for this business")
                 
                payme = Payme(payme_id=payme_id)
                pay_link = payme.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_amount,
                    return_url=get_return_url(business.platforms) or settings.PAYME_RETURN_URL
                )

            elif order.payment_method == "CLICK":
                if not business.payment_methods and not get_click_api_key(business.payment_methods):
                    raise Exception("Click payment method is not configured for this business")
                click_data = get_click_api_key(business.payment_methods)
                click_up = ClickUp(
                        service_id=click_data["service_id"],
                        merchant_id=click_data["merchant_id"]
                    )
                pay_link = click_up.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_amount,
                    return_url=get_return_url(business.platforms) or settings.CLICK_RETURN_URL  
                )
            else:
                pay_link = None

            return MakeOrder(order=order, payment_link=pay_link)

        except Exception as e:
            raise Exception(f"Order creation failed: {str(e)}")


class UpdateOrderStatus(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        business_id = graphene.String(required=True)
        status = graphene.String(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, id, business_id, status):
        try:
            # Verify the order exists and belongs to the business
            business = Business.objects.get(hash_id=business_id)
            order_id = from_global_id(id)[1]
            order = Order.objects.get(id=order_id, business=business)

            if business.multi_operator_mode:
                if is_user_op := Membership.objects.filter(user=info.context.user, business=business, role="OPERATOR"):
                    operator = is_user_op.first()
                    order.operator = operator

            # Validate the status transition
            valid_statuses = ["NEW", "PROCESSING", "DELIVERING", "COMPLETED", "CANCELLED"]
            if status not in valid_statuses:
                raise GraphQLError(
                    f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

            # Update the status
            order.status = status
            order.save()

            return UpdateOrderStatus(order=order)
        except ObjectDoesNotExist:
            raise GraphQLError(
                "Order not found or doesn't belong to this business")


class UpdateOrderInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    business_id = graphene.String(required=True)
    status = graphene.String()
    payment_method = graphene.String()
    address = graphene.String()
    delivery_type = graphene.String()
    branch_id = graphene.ID()
    comment = graphene.String()


class UpdateOrder(graphene.Mutation):
    class Arguments:
        input = UpdateOrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, input):
        # Verify the order exists and belongs to the business
        order_id = from_global_id(input.id)[1]
        order = Order.objects.filter(
            Q(business__hash_id=input.business_id) | Q(business__tg_hash_id=input.business_id),
            id=order_id
        ).first()

        if not order:
            raise GraphQLError("Order not found or doesn't belong to this business")
        # Update fields if they're provided
        if input.status:
            order.status = input.status
        if input.payment_method:
            order.payment_method = input.payment_method
        if input.address:
            order.address = json.loads(input.address)
        if input.delivery_type:
            if input.delivery_type not in ["PICKUP", "DELIVERY"]:
                raise GraphQLError(
                    "Delivery type must be PICKUP or DELIVERY")
            order.delivery = input.delivery_type
        if input.branch_id:
            branch_id = from_global_id(input.branch_id)[1]
            order.branch_id = branch_id
        if input.comment is not None:  # Empty string is allowed
            order.comment = input.comment

        order.save()

        return UpdateOrder(order=order)


class DeleteOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        try:
            order_id = from_global_id(id)[1]
            order = Order.objects.get(id=order_id)

            # Soft delete the order (assuming your model has is_deleted field)
            # Alternatively, use order.delete() for hard delete
            order.is_deleted = True
            order.save()

            return DeleteOrder(success=True)
        except ObjectDoesNotExist:
            raise GraphQLError("Order not found")


class Mutation(graphene.ObjectType):
    create_order = CreateOrder.Field()
    make_order = MakeOrder.Field()
    update_order_status = UpdateOrderStatus.Field()
    update_order = UpdateOrder.Field()
    delete_order = DeleteOrder.Field()
