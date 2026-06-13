import graphene
from graphql import GraphQLError
import json
import logging
from datetime import timedelta


from django.db import transaction
from django.utils import timezone

from apps.api.graphql.v1.types.business import BusinessType
from apps.business.models import Business, Membership, Subscription
from apps.api.helper import create_owner_role_with_permissions

from apps.business.utils import (
  generate_business_hash_id, process_business_fields, process_platforms_config, is_platform_available, get_domain_from_platforms    
)
from apps.business.service import (
    remove_vercel_domain, remove_telegram_bot
)

# Configure logging
logger = logging.getLogger(__name__)

def check_business_limit(user):
    return Membership.objects.filter(
        user=user,
        role="OWNER"
    ).count() >= 3

class CreateBusiness(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        logo = graphene.String()
        platforms = graphene.String()

    business = graphene.Field(BusinessType)

    @transaction.atomic
    def mutate(self, info, name, logo=None, platforms=None):
        try:
            if check_business_limit(info.context.user):
                raise GraphQLError("You can only have 3 businesses without a proper settings.")
            
            if platforms:
                self.validate_platforms(platforms)

            hash_id = generate_business_hash_id(platforms)

            business = Business.objects.create(
                name=name, logo=logo, hash_id=hash_id
            )

            if (timezone.now() - info.context.user.date_joined) <= timedelta(days=7) and Membership.objects.filter(
                user=info.context.user, role="OWNER"
            ).count() < 1:
                Subscription.objects.create(
                    business=business,
                    subscription_type=Subscription.SubscriptionTier.PRO,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=7),
                    total_amount=0.00,
                )
            else:
                Subscription.objects.create(
                    business=business,
                    subscription_type=Subscription.SubscriptionTier.BASIC,
                    start_date=timezone.now().date() - timedelta(days=2),
                    end_date=timezone.now().date() - timedelta(days=1),
                    total_amount=0.00,
                )
            
            owner_role = create_owner_role_with_permissions(business)

            Membership.objects.create(
                user=info.context.user,
                business=business,
                role=owner_role.name,
            )

            return CreateBusiness(business=business)
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error creating business: {str(e)}")
            raise GraphQLError(f"Failed to create business: {str(e)}")

    
    def validate_platforms(platforms_str=None):
        """Validate platforms configuration"""
        if not platforms_str:
            return True
            
        try:
            platforms = json.loads(platforms_str)
            is_platform_available(platforms)
                
        except GraphQLError:
            raise GraphQLError("Invalid platforms configuration")
        except Exception as e:
            logger.error(f"Error validating platforms: {str(e)}")
            raise GraphQLError("Invalid platforms configuration")

class CreateDetailedBusiness(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        favicon = graphene.String()
        logo = graphene.String()
        description = graphene.String()
        languages = graphene.String()
        details = graphene.String()
        working_days = graphene.String()
        social_info = graphene.String()
        payment_methods = graphene.String()
        platforms = graphene.String()
        step = graphene.String()
        is_finished = graphene.Boolean()
        otp_enabled = graphene.Boolean()
        multi_operator_mode = graphene.Boolean()
        currency = graphene.String()

    business = graphene.Field(BusinessType)

    @transaction.atomic
    def mutate(self, info, name, **kwargs):
        try:
            if check_business_limit(info.context.user):
                raise GraphQLError("You can only have 3 businesses without a proper settings.")
            
            platforms_str = kwargs.get("platforms")
            if platforms_str:
                self.validate_platforms(platforms_str)

            # Agar platforms berilgan bo'lsa
            hash_id = generate_business_hash_id(platforms_str)

            business = Business.objects.create(name=name, hash_id=hash_id)
            business = process_business_fields(business, kwargs)
            business.save()

            if (timezone.now() - info.context.user.date_joined) <= timedelta(days=7) and Membership.objects.filter(business=business,
                user=info.context.user, role="OWNER"
            ).count() < 1:
                Subscription.objects.create(
                    business=business,
                    subscription_type=Subscription.SubscriptionTier.PRO ,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timedelta(days=7),
                    total_amount=0.00,
                )
            else:
                Subscription.objects.create(
                    business=business,
                    subscription_type=Subscription.SubscriptionTier.BASIC   ,
                    start_date=timezone.now().date() - timedelta(days=2),
                    end_date= timezone.now().date() - timedelta(days=1),
                    total_amount=0.00,
                )
            owner_role = create_owner_role_with_permissions(business)

            Membership.objects.create(
                user=info.context.user,
                business=business,
                role=owner_role.name,
            )

            return CreateDetailedBusiness(business=business)
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error creating detailed business: {str(e)}")
            raise GraphQLError(f"Failed to create detailed business: {str(e)}")

    def validate_platforms(platforms_str=None):
        """Validate platforms configuration"""
        if not platforms_str:
            return True
            
        try:
            platforms = json.loads(platforms_str)
            is_platform_available(platforms)
                
        except GraphQLError:
            raise GraphQLError("Invalid platforms configuration")
        except Exception as e:
            logger.error(f"Error validating platforms: {str(e)}")
            raise GraphQLError("Invalid platforms configuration")
        
class UpdateBusiness(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        favicon = graphene.String()
        logo = graphene.String()
        description = graphene.String()
        languages = graphene.String()
        details = graphene.String()
        working_days = graphene.String()
        social_info = graphene.String()
        payment_methods = graphene.String()
        platforms = graphene.String()
        step = graphene.String()
        is_finished = graphene.Boolean()
        otp_enabled = graphene.Boolean()
        multi_operator_mode = graphene.Boolean()
        currency = graphene.String()

    business = graphene.Field(BusinessType)

    def mutate(self, info, id, **kwargs):
        try:
            business = Business.objects.filter(hash_id=id).first()
            if not business:
                raise GraphQLError("Business not found")

            platforms_str = kwargs.get("platforms")
            if platforms_str:
                # Validate new platform configuration
                platforms = json.loads(platforms_str)
                is_platform_available(platforms, exclude_business_id=business.id)
            # Process platforms configuration
            if platforms_str:
                business = process_platforms_config(business, platforms_str, business.platforms)
            business = process_business_fields(business, kwargs)
            business.save()
            return UpdateBusiness(business=business)

        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error updating business: {str(e)}")
            raise GraphQLError(f"Failed to update business: {str(e)}")


class DeleteBusiness(graphene.Mutation):
    class Arguments:
        hash_id = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @transaction.atomic
    def mutate(self, info, hash_id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                return DeleteBusiness(success=False, message="Authentication required")                 
            
            owner_membership = Membership.objects.filter(
                user=user,
                business__hash_id=hash_id,
                role="OWNER"
            ).first()
            if not owner_membership:
                return DeleteBusiness(success=False, message="You do not have permission to delete this business")  
            
            # Check if business exists
            business = Business.objects.filter(hash_id=hash_id).first()
            if not business:
                return DeleteBusiness(success=False, message="Business not found")

            # Remove Telegram bot if exists
            remove_telegram_bot(business)

            # Remove domain from Vercel and CORS
            try:
                platforms_str = business.platforms
                if platforms_str:
                    platforms = json.loads(platforms_str)
                    domain = get_domain_from_platforms(platforms)
                    if domain:
                        remove_vercel_domain(domain)
            except Exception as e:
                logger.error(
                    f"Error removing domain on business delete: {str(e)}")                

            business.delete()
            return DeleteBusiness(success=True, message="Business deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting business: {str(e)}")
            return DeleteBusiness(success=False, message=f"Failed to delete business: {str(e)}")


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    create_detailed_business = CreateDetailedBusiness.Field()
    update_business = UpdateBusiness.Field()
    delete_business = DeleteBusiness.Field()