from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "ai_life_os",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)
celery_app.conf.task_routes = {
    "app.workers.tasks.run_workflow_task": {"queue": "workflows"},
}
