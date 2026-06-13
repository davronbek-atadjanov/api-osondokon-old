from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Osondokon Admin",
    "SITE_HEADER": "Osondokon",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("images/favicon.png"),
    "SITE_LOGO": lambda request: static("images/logo.svg"),
    "SITE_SYMBOL": "storefront",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "THEME": "dark",
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Bosh sahifa",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Hisob",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Foydalanuvchilar",
                        "icon": "people",
                        "link": reverse_lazy("admin:account_user_changelist"),
                    },
                    {
                        "title": "OTP kodlar",
                        "icon": "lock",
                        "link": reverse_lazy("admin:account_otp_changelist"),
                    },
                ],
            },
            {
                "title": "Biznes",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Bizneslar",
                        "icon": "business",
                        "link": reverse_lazy("admin:business_business_changelist"),
                    },
                    {
                        "title": "Filiallar",
                        "icon": "store",
                        "link": reverse_lazy("admin:business_branch_changelist"),
                    },
                    {
                        "title": "A'zoliklar",
                        "icon": "card_membership",
                        "link": reverse_lazy("admin:business_membership_changelist"),
                    },
                    {
                        "title": "Obunalar",
                        "icon": "subscriptions",
                        "link": reverse_lazy("admin:business_subscription_changelist"),
                    },
                    {
                        "title": "Rollar",
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:business_role_changelist"),
                    },
                    {
                        "title": "Ruxsatlar",
                        "icon": "security",
                        "link": reverse_lazy("admin:business_permission_changelist"),
                    },
                ],
            },
            {
                "title": "Mahsulotlar",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Kategoriyalar",
                        "icon": "category",
                        "link": reverse_lazy("admin:category_category_changelist"),
                    },
                    {
                        "title": "Mahsulotlar",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:product_product_changelist"),
                    },
                    {
                        "title": "Variantlar",
                        "icon": "tune",
                        "link": reverse_lazy("admin:product_productvariant_changelist"),
                    },
                ],
            },
            {
                "title": "Buyurtmalar",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Buyurtmalar",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:order_order_changelist"),
                    },
                    {
                        "title": "Buyurtma elementlari",
                        "icon": "list_alt",
                        "link": reverse_lazy("admin:order_orderitem_changelist"),
                    },
                ],
            },
            {
                "title": "Marketing",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Bannerlar",
                        "icon": "image",
                        "link": reverse_lazy("admin:marketing_banner_changelist"),
                    },
                    {
                        "title": "Email shablonlar",
                        "icon": "email",
                        "link": reverse_lazy("admin:marketing_emailtemplate_changelist"),
                    },
                    {
                        "title": "SMS shablonlar",
                        "icon": "sms",
                        "link": reverse_lazy("admin:marketing_smstemplate_changelist"),
                    },
                ],
            },
            {
                "title": "Yetkazib berish",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Yetkazish usullari",
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:delivery_deliverymethod_changelist"),
                    },
                    {
                        "title": "Olib ketish usullari",
                        "icon": "store_mall_directory",
                        "link": reverse_lazy("admin:delivery_pickupmethod_changelist"),
                    },
                ],
            },
            {
                "title": "To'lovlar",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Click tranzaksiyalar",
                        "icon": "payments",
                        "link": reverse_lazy("admin:click_up_clicktransaction_changelist"),
                    },
                ],
            },
            {
                "title": "Telegram",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Telegram botlar",
                        "icon": "smart_toy",
                        "link": reverse_lazy("admin:telegrambot_telegram_bot_changelist"),
                    },
                ],
            },
            {
                "title": "Tizim",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Guruhlar",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
