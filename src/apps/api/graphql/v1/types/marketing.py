from graphene_django.types import DjangoObjectType
from apps.marketing.models import Banner, EmailTemplate, SmsTemplate
from graphene.relay import Node

class BannerType(DjangoObjectType):
    class Meta:
        model = Banner
        fields = "__all__"

class BannerNode(DjangoObjectType):
    class Meta:
        model = Banner
        fields = "__all__"
        interfaces = (Node,)

class EmailTemplateType(DjangoObjectType):
    class Meta:
        model = EmailTemplate
        fields = "__all__"

class SmsTemplateType(DjangoObjectType):
    class Meta:
        model = SmsTemplate
        fields = "__all__"
