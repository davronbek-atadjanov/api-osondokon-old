from django.contrib import admin
from apps.marketing.models import Banner, EmailTemplate, SmsTemplate

admin.site.register([
    Banner, EmailTemplate, SmsTemplate
])
