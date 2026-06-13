from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from apps.account.models import User, OTP


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = (
        "username",
        "full_name",
        "phone_number",
        "user_type",
        "is_active",
        "is_staff",
        "is_phone_verified",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "user_type", "is_phone_verified")
    search_fields = ("username", "email", "phone_number", "full_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Shaxsiy ma'lumot", {"fields": ("full_name", "email", "phone_number", "business_id", "user_type")}),
        ("Tasdiqlash", {"fields": ("is_phone_verified",)}),
        ("Ruxsatlar", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
            "classes": ("collapse",),
        }),
        ("Muhim sanalar", {"fields": ("last_login", "date_joined")}),
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
                "is_phone_verified",
            ),
        }),
    )


@admin.register(OTP)
class OTPAdmin(ModelAdmin):
    list_display = ("user", "code", "type", "created_at", "last_sent")
    search_fields = ("user__username", "user__email", "code")
    list_filter = ("type",)
    list_per_page = 25
    readonly_fields = ("created_at", "last_sent")
