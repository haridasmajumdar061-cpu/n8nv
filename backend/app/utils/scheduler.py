from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.tasks import run_workflow_task


scheduler = AsyncIOScheduler()


def schedule_workflow(workflow_id: int, cron_expression: str) -> None:
    parts = cron_expression.split()
    if len(parts) != 5:
        return

    minute, hour, day, month, day_of_week = parts
    scheduler.add_job(
        run_workflow_task.delay,
        trigger="cron",
        args=[workflow_id],
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        id=f"wf_{workflow_id}",
        replace_existing=True,
    )


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
