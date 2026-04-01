from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.execution import Execution, ExecutionLog
from app.models.user import User
from app.models.workflow import Workflow
from app.schemas.execution import ExecutionCreate, ExecutionOut, LogOut
from app.workers.tasks import run_workflow_task

router = APIRouter()


@router.post("/run", response_model=ExecutionOut)
async def run_workflow(
    payload: ExecutionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> Execution:
    result = await db.execute(
        select(Workflow).where(Workflow.id == payload.workflow_id, Workflow.user_id == user.id)
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    execution = Execution(workflow_id=wf.id, input_payload=payload.input_payload)
    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    run_workflow_task.delay(execution.id)
    return execution


@router.get("/{execution_id}", response_model=ExecutionOut)
async def get_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> Execution:
    result = await db.execute(
        select(Execution)
        .join(Workflow, Workflow.id == Execution.workflow_id)
        .where(Execution.id == execution_id, Workflow.user_id == user.id)
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/{execution_id}/logs", response_model=list[LogOut])
async def get_execution_logs(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> list[ExecutionLog]:
    result = await db.execute(
        select(ExecutionLog)
        .join(Execution, Execution.id == ExecutionLog.execution_id)
        .join(Workflow, Workflow.id == Execution.workflow_id)
        .where(ExecutionLog.execution_id == execution_id, Workflow.user_id == user.id)
        .order_by(ExecutionLog.created_at.asc())
    )
    return list(result.scalars().all())
