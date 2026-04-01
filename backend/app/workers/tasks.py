import asyncio

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.workflow_engine import workflow_engine


@celery_app.task(bind=True, max_retries=3)
def run_workflow_task(self, execution_id: int) -> None:
    asyncio.run(_run(execution_id, self))


async def _run(execution_id: int, task_instance) -> None:
    async with SessionLocal() as session:
        try:
            await workflow_engine.run(session, execution_id)
        except Exception as exc:
            raise task_instance.retry(exc=exc, countdown=2 ** task_instance.request.retries)
