from django.contrib import admin
from apps.account.models import User, OTP
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "phone_number",
        "business_id",
        "user_type",
        "is_active",
        "is_staff",
        "is_phone_verified",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "user_type", "is_phone_verified")
    search_fields = ("username", "email", "phone_number", "full_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")  # faqat o‘qish uchun

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("full_name", "email", "phone_number", "business_id", "user_type")}),
        ("Verification", {"fields": ("is_phone_verified",)}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "full_name",
                "email",
                "phone_number",
                "business_id",
                "user_type",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
                "is_phone_verified",
                "groups",
                "user_permissions",
            ),
        }),
    )

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'type', 'created_at', 'last_sent')
    search_fields = ('user__username', 'user__email', 'code')
    list_filter = ('type',)

admin.site.register(OTP, OTPAdmin)

# from graphql_jwt.refresh_token.models import RefreshToken

# admin.site.register(RefreshToken)