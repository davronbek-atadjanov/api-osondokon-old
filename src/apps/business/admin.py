from django.contrib import admin
from apps.business.models import (
    Business, Membership, Role,
    Permission, Subscription, Branch
)

admin.site.register([
    Business, Permission, Membership,
    Role, Subscription, Branch
])
