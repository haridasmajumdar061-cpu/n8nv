from datetime import datetime

from pydantic import BaseModel


class ExecutionCreate(BaseModel):
    workflow_id: int
    input_payload: dict | None = None


class ExecutionOut(BaseModel):
    id: int
    workflow_id: int
    status: str
    input_payload: dict | None
    output_payload: dict | None
    error_message: str | None
    retries: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogOut(BaseModel):
    id: int
    level: str
    message: str
    log_meta: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
