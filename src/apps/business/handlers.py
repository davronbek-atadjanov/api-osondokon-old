import base64
from urllib.parse import urlparse
from corsheaders.signals import check_request_enabled
from apps.business.models import Business

def encode_domain(domain):
    base64_encoded_domain = base64.b64encode(domain.encode("utf-8")).decode("utf-8")
    www_domain = "www." + domain
    base64_encoded_www_domain = base64.b64encode(www_domain.encode("utf-8")).decode("utf-8")
    return base64_encoded_domain, base64_encoded_www_domain

def cors_allow_mysites(sender, request, **kwargs):
    origin = request.headers.get("origin")
    if not origin:
        return False

    parsed_origin = urlparse(origin)
    domain = parsed_origin.netloc

    if domain.startswith("www."):
        domain = domain[4:]

    encoded_domain, encoded_www_domain = encode_domain(domain)
    businesses = Business.objects.filter(hash_id__in=[encoded_domain, encoded_www_domain])

    for business in businesses:
        if business.plan:
            return True

    return False

check_request_enabled.connect(cors_allow_mysites)
