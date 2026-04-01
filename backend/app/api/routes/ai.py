from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.ai import AutoDebugRequest, PromptResponse, PromptToWorkflowRequest, WorkflowImprovementRequest
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/prompt-to-workflow", response_model=PromptResponse)
async def prompt_to_workflow(
    payload: PromptToWorkflowRequest,
    _: User = Depends(get_current_active_user),
) -> PromptResponse:
    return PromptResponse(result=await ai_service.prompt_to_workflow(payload.prompt))


@router.post("/improve-workflow", response_model=PromptResponse)
async def improve_workflow(
    payload: WorkflowImprovementRequest,
    _: User = Depends(get_current_active_user),
) -> PromptResponse:
    return PromptResponse(result=await ai_service.suggest_improvements(payload.definition))


@router.post("/auto-debug", response_model=PromptResponse)
async def auto_debug(
    payload: AutoDebugRequest,
    _: User = Depends(get_current_active_user),
) -> PromptResponse:
    return PromptResponse(
        result=await ai_service.auto_debug(payload.definition, payload.error_log)
    )
