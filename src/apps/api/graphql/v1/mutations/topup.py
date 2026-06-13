import graphene
from apps.business.models import Business, Subscription
from apps.order.models import Order
from django.db import transaction
from click_up import ClickUp
from django.utils import timezone
from payme import Payme
from django.conf import settings
from datetime import timedelta


class TopupBusiness(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        card_token = graphene.String()
        amount = graphene.Int(required=True)
        terms = graphene.Boolean()
        payment_method = graphene.String(required=True)

    id = graphene.ID()
    amount = graphene.Int()
    link = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    @transaction.atomic
    def mutate(self, info, business_id, amount, payment_method, card_token=None, terms=False, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise TopupBusiness(success=False, message="Authentication required")

        if amount <= 0:
            raise TopupBusiness(success=False, message="Amount must be positive")

        try:
            business = Business.objects.get(hash_id=business_id)

            order = Order.objects.create(
                user=user,
                business=business,
                total_amount=amount,
                payment_method=payment_method.upper(),
                source=Order.OrderSource.BUSINESS,
                comment="TOPUP",
                delivery="BUSINESS"
            )

            if order.payment_method == "PAYME":
                payme = Payme(payme_id=settings.PAYME_ID)
                pay_link = payme.initializer.generate_pay_link(
                    id=order.id,
                    amount=amount,
                    return_url=settings.PAYME_RETURN_URL,
                )
            elif order.payment_method == "CLICK":
                click_up = ClickUp(
                        service_id=settings.CLICK_SERVICE_ID,
                        merchant_id=settings.CLICK_MERCHANT_ID,
                    )
                pay_link = click_up.initializer.generate_pay_link(
                    id=order.id,
                    amount=order.total_amount,
                    return_url=settings.CLICK_RETURN_URL  
                )
            else:
                TopupBusiness(success=False, message="Invalid payment method")

            return TopupBusiness(id=order.id, amount=amount, link=pay_link)

        except Business.DoesNotExist:
            raise TopupBusiness(success=False, message="Business not found")
        except Exception as e:
            raise Exception(str(e))


class SubscribeBusiness(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        subscription_type = graphene.String(required=True)
        duration = graphene.Int(required=True)

    success = graphene.String()
    account = graphene.String()
    message = graphene.String()
    
    @transaction.atomic
    def mutate(self, info, business_id, subscription_type, duration):
        user = info.context.user
        if user.is_anonymous:
            return SubscribeBusiness(success="error", message="Authentication required")

        BASE_PRICES = {
            "COMBINED": {
                "BASIC": 400_000,
                "PRO": 700_000,
                "ENTERPRISE": None  # Negotiable
            }
        }

        DISCOUNTS = {
            6: 0.90,   # 10% off
            12: 0.85   # 15% off
        }

        if subscription_type not in BASE_PRICES["COMBINED"]:
            return SubscribeBusiness(success="error", message="Not enough funds in business account")

        base_price = BASE_PRICES["COMBINED"][subscription_type]

        if base_price is None:
            return SubscribeBusiness(success="error", message="Enterprise plan pricing is negotiable. Please contact support.")


        if duration <= 0:
            return SubscribeBusiness(success="error", message="Duration must be positive")

        # Calculate months and discount
        months = duration // 30  # convert days to months
        discount_multiplier = DISCOUNTS.get(months, 1.0)
        monthly_price = base_price * discount_multiplier
        total_amount = int(monthly_price * months)

        try:
            business = Business.objects.get(hash_id=business_id)

            if business.account < total_amount:
                return SubscribeBusiness(success="error", message="Not enough funds in business account")

            now = timezone.now().date()
            current_subscription = Subscription.objects.filter(
                business=business,
                end_date__gte=now
            ).order_by('-end_date').first()

            # Check if trying to subscribe to different plan type while having active subscription
            if current_subscription and current_subscription.subscription_type != subscription_type:
                remaining_days = (current_subscription.end_date - now).days
                if remaining_days > 0:
                    return  SubscribeBusiness(
                        success="error",
                        message=(
                            f"You have an active {current_subscription.subscription_type} subscription "
                            f"with {remaining_days} days remaining. Please wait until it expires or "
                            f"contact support to change your plan type."
                        )
                    )

            now = timezone.now().date()
            if current_subscription and current_subscription.subscription_type == subscription_type:
                sub = current_subscription
            else:
                sub = None

            if sub:
                sub.end_date += timedelta(days=duration)
                sub.total_amount += total_amount
                sub.save()
            else:
                Subscription.objects.create(
                    business=business,
                    subscription_type=subscription_type,
                    start_date=now,
                    end_date=now + timedelta(days=duration),
                    total_amount=total_amount,
                    is_auto_renew=False,
                )

            business.account -= total_amount
            business.save()

            Order.objects.create(
                user=user,
                business=business,
                total_amount=-total_amount,
                source=Order.OrderSource.BUSINESS,
                payment_method="BALANCE",
                comment="SUBSCRIPTION",
                delivery="BUSINESS"
            )

            return SubscribeBusiness(success="ok", account=business.account, message="Subscription successful")

        except Business.DoesNotExist:
            raise Exception("Business not found")
        except Exception as e:
            raise Exception(str(e))


class Mutation(graphene.ObjectType):
    topup = TopupBusiness.Field()
    subscribe = SubscribeBusiness.Field()
