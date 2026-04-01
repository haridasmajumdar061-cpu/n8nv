from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.lifeos import DailyPlan, MemoryRecord
from app.models.user import User
from app.schemas.lifeos import (
    DailyPlannerRequest,
    FocusModeRequest,
    IncomeSuggestionRequest,
    MemoryCreate,
    VoiceAssistantRequest,
)
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/memory")
async def add_memory(
    payload: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    record = MemoryRecord(user_id=user.id, **payload.model_dump())
    db.add(record)
    await db.commit()
    return {"status": "ok"}


@router.get("/memory")
async def list_memories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> list[dict]:
    result = await db.execute(
        select(MemoryRecord).where(MemoryRecord.user_id == user.id).order_by(MemoryRecord.created_at.desc())
    )
    return [
        {
            "id": m.id,
            "type": m.memory_type,
            "content": m.content,
            "score": m.relevance_score,
        }
        for m in result.scalars().all()
    ]


@router.post("/planner")
async def create_plan(
    payload: DailyPlannerRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    plan_data = await ai_service.generate_daily_plan(payload.model_dump())
    plan = DailyPlan(user_id=user.id, plan_date=payload.date or str(date.today()), plan=plan_data)
    db.add(plan)
    await db.commit()
    return plan_data


@router.post("/income-suggestions")
async def income_suggestions(
    payload: IncomeSuggestionRequest,
    _: User = Depends(get_current_active_user),
) -> dict:
    return await ai_service.generate_income_suggestions(payload.model_dump())


@router.post("/focus-mode")
async def focus_mode(
    payload: FocusModeRequest,
    _: User = Depends(get_current_active_user),
) -> dict:
    return {
        "mode": "focus",
        "duration_minutes": payload.duration_minutes,
        "blocked_apps": payload.blocked_apps,
        "rules": ["Mute notifications", "Pause social feeds", "Allow emergency contacts"],
    }


@router.post("/voice-assistant")
async def voice_assistant(
    payload: VoiceAssistantRequest,
    _: User = Depends(get_current_active_user),
) -> dict:
    return await ai_service.voice_assistant_response(payload.model_dump())
