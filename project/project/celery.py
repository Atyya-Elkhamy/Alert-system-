
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-stock-prices-every-5-minutes': {
        'task': 'alerts.tasks.fetch_stock_prices',
        'schedule': crontab(minute='*/5'),
    },
}
