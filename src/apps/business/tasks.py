from celery import shared_task
from django_redis import get_redis_connection
from datetime import date, timedelta
from apps.business.models import TrafficStat, Business

@shared_task
def sync_traffic_stats():
    r = get_redis_connection("default")

    # Barcha counterlarni olish
    pattern = f"traffic_count:*"
    for key in r.scan_iter(pattern):
        key_str = key.decode()  # traffic_count:{biz}:{platform}:{day}
        _, business_id, platform, day = key_str.split(":")

        count = int(r.get(key) or 0)
        day_date = date(int(day[0:4]), int(day[4:6]), int(day[6:8]))

        business = Business.objects.filter(hash_id=business_id, tg_hash_id=business_id).first()
        if business:
            obj, created = TrafficStat.objects.get_or_create(
                business=business,
                platform=platform,
                date=day_date,
                defaults={"count": count}
            )
            if not created:
                obj.count = count
                obj.save()
