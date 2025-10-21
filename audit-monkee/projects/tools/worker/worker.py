from celery import Celery
from ..api.settings import settings
from .tasks import init_celery

celery_app = Celery('audit_monkee', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_track_started=True, task_serializer='json', result_serializer='json', accept_content=['json'])

init_celery(celery_app)
