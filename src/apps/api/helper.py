from django.core.cache import cache
from apps.business.models import Role, Permission

PLAN_LIMITS = {
    "BASIC": 700,
    "PRO": 1000,
    "ENTERPRISE": 2000,
}

SERVICE_PRICES = {
    "beeline": 95,
    "uzmobile": 95,
    "mobiuz": 95,
    "ucell": 160,
    "humans": 95,
    "oq": 95,        # OQ GSM
    "perfectum": 95,
}

OPERATOR_PREFIXES = {
    "beeline": ["90", "91"],
    "uzmobile": ["99", "77", "70", "95"],
    "mobiuz": ["97", "88", "87"],
    "ucell": ["93", "94", "50"],
    "humans": ["33"],
    "oq": ["20"],
    "perfectum": ["98"],
}


def get_sms_cache_key(business_id):
    return f"business:{business_id}:sms_sent_count"


def get_operator_by_phone(phone_number):
    """Telefon raqamdan operatorni aniqlaydi"""
    clean_number = phone_number.replace("+", "").strip()

    # faqat oxirgi 2-3 raqam prefiksini olish
    if clean_number.startswith("998"):
        prefix = clean_number[3:5]  # masalan: +998 90 -> 90
    else:
        return None

    for operator, prefixes in OPERATOR_PREFIXES.items():
        if prefix in prefixes:
            return operator
    return None


def get_sms_price(phone_number):
    """Telefon raqamdan operator bo‘yicha narxni qaytaradi"""

    operator = get_operator_by_phone(phone_number)
    if not operator:
        return 0  # noma'lum operator
    return SERVICE_PRICES.get(operator, 0)


def check_sms_available(business, phone_number):
    """SMS yuborish mumkinmi yoki yo‘q, faqat tekshiradi"""
    if not business.plan:
        return False, "no_plan"
    

    sms_limit = PLAN_LIMITS.get(business.plan, 0)

    cache_key = get_sms_cache_key(business.id)
    used_sms = cache.get(cache_key, 0)

    if used_sms < sms_limit:
        return True, "plan_limit"

    sms_price = get_sms_price(phone_number)
    if business.account >= sms_price:
        return True, "balance"

    return False, "no_balance"


def consume_sms(business_id, source, phone_number):
    """SMS yuborilgach, limit yoki balansdan yechadi"""
    cache_key = get_sms_cache_key(business_id)

    if source == "plan_limit":
        cache.add(cache_key, 0, timeout=2592000)  
        cache.incr(cache_key, 1)

    elif source == "balance":
        from apps.business.models import Business
        business = Business.objects.get(id=business_id)

        # Telefon raqamdan narxni aniqlash
        sms_price = get_sms_price(phone_number)

        business.account -= sms_price
        business.save(update_fields=["account"])

# default Owner for permissions list
DEFAULT_OWNER_PERMISSIONS = [
    "dashboard",
    "orders",
    "clients",
    "products",
    "categories",
    "banners",
    "employees",
    "roles",
    "branches",
    "payments",
    "platforms",
    "apps",
    "business-settings",
    "delivery",
    "barn",
]

def create_owner_role_with_permissions(business):
    # Role yaratamiz
    owner_role = Role.objects.create(
        business=business,
        name="OWNER",
        description="Full access to all business features",
        is_default=True
    )

    # Permissionlarni yaratib, rolga qo‘shamiz
    for menu in DEFAULT_OWNER_PERMISSIONS:
        perm = Permission.objects.create(
            menu_name=menu,
            can_view=True,
            can_edit=True,
            can_delete=True,
        )
        owner_role.permissions.add(perm)

    return owner_role
