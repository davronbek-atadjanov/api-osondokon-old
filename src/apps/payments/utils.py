import json

def check_payme_api_key(payme_key, payment_methods):
    """
    Check if the given payme_key matches any business' payme.api_key in their payment_method.
"""
    try:
        payme = payment_methods.get("payme", {})
        if payme.get("enabled") and payme.get("api_key") == payme_key:
            return True
    except (json.JSONDecodeError, TypeError):
        pass

    return False

# def check_payme_api_key(payme_key):
#     """
#     Check if the given payme_key matches any business' payme.api_key in their payment_method.
#     """
#     print(payme_key)
#     if payme_key == settings.PAYME_KEY:
#         return True    

#     businesses = Business.objects.all()

#     for business in businesses:
#         try:
#             methods = json.loads(business.payment_methods)
#             payme = methods.get("payme", {})
#             if payme.get("enabled") and payme.get("api_key") == payme_key:
#                 return True
#         except (json.JSONDecodeError, TypeError):
#             continue

#     return False

def get_click_payment_method(payment_methods):
    """
    Extracts the Click payment method from the provided payment methods.
    """

    try:
        methods = json.loads(payment_methods)
        click = methods.get("click", {})

        if click.get("enabled") and click.get("service_id") and click.get("api_key"):
            return {
                "service_id": click["service_id"],
                "secret_key": click["api_key"] 
            }
    except (json.JSONDecodeError, TypeError):
        pass
    return None