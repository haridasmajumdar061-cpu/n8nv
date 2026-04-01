from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True
    cron_schedule: str | None = None


class WorkflowCreate(WorkflowBase):
    definition: dict = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    definition: dict | None = None
    is_active: bool | None = None
    cron_schedule: str | None = None


class WorkflowOut(WorkflowBase):
    id: int
    user_id: int
    definition: dict
    created_at: datetime

    class Config:
        from_attributes = True
