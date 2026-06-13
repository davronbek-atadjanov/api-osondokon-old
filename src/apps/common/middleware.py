import json
from datetime import date
from django_redis import get_redis_connection
from apps.order.utils import detect_platform

class TrafficMiddleware:
    def resolve(self, next, root, info, **args):
        request = info.context
        platform = detect_platform(request)

        business_id = None
        try:
            if "business_id" in args:
                business_id = args["business_id"]
            elif request.method == "POST" and request.body:
                body_data = json.loads(request.body)
                variables = body_data.get("variables", {})
                business_id = variables.get("business_id")
        except Exception:
            pass

        if business_id:
            today = date.today().strftime("%Y%m%d")
            r = get_redis_connection("default")
            # IP olish
            ip = request.META.get(
                "HTTP_X_FORWARDED_FOR",
                request.META.get("REMOTE_ADDR", "unknown")
            ).split(",")[0]
            # IP bo‘yicha noyob key
            ip_key = f"traffic_ip:{business_id}:{platform}:{today}:{ip}"

            # Faqat yangi IP bo‘lsa yozadi
            if r.set(ip_key, 1, ex=86400, nx=True):
                counter_key = f"traffic_count:{business_id}:{platform}:{today}"
                count = r.incr(counter_key)
                if count == 1:
                    r.expire(counter_key, 172800)  # faqat birinchi marta TTL qo‘yiladi

        return next(root, info, **args)
