import os
from redis import Redis
from celery import Celery
from app.core.config import settings

# Check if Redis is online to prevent crash loop
redis_online = False
try:
    r = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.5)
    if r.ping():
        redis_online = True
except Exception:
    pass

broker_url = settings.REDIS_URL if redis_online else "sqla+sqlite:///celery_fallback.sqlite"
backend_url = settings.REDIS_URL if redis_online else "db+sqlite:///celery_fallback.sqlite"

celery_app = Celery(
    "qshield_worker",
    broker=broker_url,
    backend=backend_url,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=False
)
