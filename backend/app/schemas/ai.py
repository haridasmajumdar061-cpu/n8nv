from pydantic import BaseModel, Field


class PromptToWorkflowRequest(BaseModel):
    prompt: str


class WorkflowImprovementRequest(BaseModel):
    definition: dict


class AutoDebugRequest(BaseModel):
    definition: dict
    error_log: str = Field(default="")


class PromptResponse(BaseModel):
    result: dict
