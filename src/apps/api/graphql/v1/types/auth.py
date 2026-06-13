from graphene_django import DjangoObjectType
from apps.account.models import User, OTP, Card


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "phone_number", "email", "full_name", "is_phone_verified")

class CardType(DjangoObjectType):
    class Meta:
        model = Card
        fields = ('id', 'user', 'card_token', 'is_default', 'is_verified')

class OTPType(DjangoObjectType):
    class Meta:
        model = OTP
        fields = ('id', 'user', 'code', 'type', 'attempts', 'last_sent', 'created_at')