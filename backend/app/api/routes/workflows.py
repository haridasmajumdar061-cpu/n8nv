from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowOut, WorkflowUpdate
from app.utils.scheduler import schedule_workflow

router = APIRouter()


@router.get("", response_model=list[WorkflowOut])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> list[Workflow]:
    result = await db.execute(select(Workflow).where(Workflow.user_id == user.id))
    return list(result.scalars().all())


@router.post("", response_model=WorkflowOut)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> Workflow:
    wf = Workflow(user_id=user.id, **payload.model_dump())
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    if wf.cron_schedule:
        schedule_workflow(wf.id, wf.cron_schedule)
    return wf


@router.patch("/{workflow_id}", response_model=WorkflowOut)
async def update_workflow(
    workflow_id: int,
    payload: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> Workflow:
    result = await db.execute(
        select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user.id)
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(wf, key, value)

    await db.commit()
    await db.refresh(wf)
    if wf.cron_schedule:
        schedule_workflow(wf.id, wf.cron_schedule)
    return wf
