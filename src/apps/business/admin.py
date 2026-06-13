from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.business.models import Business, Branch, Membership, Role, Permission, Subscription


@admin.register(Business)
class BusinessAdmin(ModelAdmin):
    list_display = ("name", "currency", "is_finished", "multi_operator_mode", "created_at")
    list_filter = ("is_finished", "multi_operator_mode", "otp_enabled")
    search_fields = ("name", "hash_id")
    readonly_fields = ("created_at", "updated_at", "hash_id", "tg_hash_id")
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("name", "description", "currency")}),
        ("Identifikatorlar", {"fields": ("hash_id", "tg_hash_id"), "classes": ("collapse",)}),
        ("Media", {"fields": ("logo", "favicon")}),
        ("Sozlamalar", {"fields": ("step", "is_finished", "multi_operator_mode", "otp_enabled", "account")}),
        ("JSON ma'lumotlar", {
            "fields": ("languages", "social_info", "working_days", "payment_methods", "platforms"),
            "classes": ("collapse",),
        }),
        ("Sanalar", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ("name", "business", "address", "phone", "enabled", "is_main_branch", "created_at")
    list_filter = ("enabled", "is_main_branch", "delivery_enabled", "pickup_enabled")
    search_fields = ("name", "business__name", "address", "phone")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("business",)


@admin.register(Membership)
class MembershipAdmin(ModelAdmin):
    list_display = ("user", "business", "role", "tag", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__phone_number", "business__name", "tag")
    list_per_page = 25
    list_select_related = ("user", "business")


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "business", "is_default")
    list_filter = ("is_default",)
    search_fields = ("name", "business__name")
    list_per_page = 25
    list_select_related = ("business",)


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ("menu_name", "can_view", "can_edit", "can_delete")
    list_filter = ("can_view", "can_edit", "can_delete")
    search_fields = ("menu_name",)
    list_per_page = 25


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("business", "subscription_type", "platform_type", "start_date", "end_date", "is_auto_renew", "total_amount")
    list_filter = ("subscription_type", "platform_type", "is_auto_renew")
    search_fields = ("business__name",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    list_select_related = ("business",)
