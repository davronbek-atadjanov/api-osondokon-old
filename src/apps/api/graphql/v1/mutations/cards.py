import graphene
from apps.account.models import User, Card
from apps.api.graphql.v1.types.auth import CardType
from payme import Payme
from django.conf import settings

class AddCardMutation(graphene.Mutation):
    class Arguments:
        card_number = graphene.String(required=True)
        expire_date = graphene.String(required=True)  # Format: "03/99"
        is_default = graphene.Boolean(default_value=False)

    card = graphene.Field(CardType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, card_number, expire_date, is_default):
        try:
            user = info.context.user
            
            # Initialize Payme client
            payme = Payme(
                payme_id=settings.PAYME_ID,
                payme_key=settings.PAYME_KEY,
                is_test_mode=False  # False in production
            )
            
            # Step 1: Create card in Payme (this will trigger SMS)
            response = payme.cards.create(
                number=card_number,
                expire=expire_date,
                save=True
            )
            
            # If this card is being set as default, unset any existing default cards
            if is_default:
                Card.objects.filter(user=user, is_default=True).update(is_default=False)
            
            # Create card record in our DB (unverified)
            card = Card.objects.create(
                user=user,
                card_token=response.result.card.token,
                is_default=is_default,
                is_verified=False
            )
            
            return AddCardMutation(
                card=card,
                success=True,
                message="SMS verification code sent to your phone"
            )
            
        except User.DoesNotExist:
            return AddCardMutation(success=False, message="User not found")
        except Exception as e:
            return AddCardMutation(success=False, message=str(e))

class VerifyCardMutation(graphene.Mutation):
    class Arguments:
        card_id = graphene.ID(required=True)
        sms_code = graphene.String(required=True)

    card = graphene.Field(CardType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, card_id, sms_code):
        try:
            card = Card.objects.get(id=card_id)
            
            if card.is_verified:
                return VerifyCardMutation(
                    success=False,
                    message="Card is already verified"
                )
            
            # Initialize Payme client
            payme = Payme(
                payme_id=settings.PAYME_ID,
                payme_key=settings.PAYME_KEY,
                is_test_mode=False
            )
            
            # Step 2: Verify SMS code with Payme
            verify_response = payme.cards.verify(
                token=card.card_token,
                code=sms_code
            )
            
            if not verify_response.result.card.verify:
                return VerifyCardMutation(
                    success=False,
                    message="Invalid verification code"
                )
            
            # Step 3: Update our card record
            card.is_verified = True
            card.save()
            
            return VerifyCardMutation(
                card=card,
                success=True,
                message="Card successfully verified"
            )
            
        except Card.DoesNotExist:
            return VerifyCardMutation(success=False, message="Card not found")
        except Exception as e:
            return VerifyCardMutation(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    add_card = AddCardMutation.Field()
    verify_card = VerifyCardMutation.Field()