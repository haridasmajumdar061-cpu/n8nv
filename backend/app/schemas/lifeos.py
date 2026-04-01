from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    memory_type: str
    content: dict
    relevance_score: float = 0.5


class DailyPlannerRequest(BaseModel):
    date: str
    goals: list[str] = Field(default_factory=list)
    available_hours: int = 8


class IncomeSuggestionRequest(BaseModel):
    skills: list[str]
    available_hours_per_week: int = 10


class FocusModeRequest(BaseModel):
    duration_minutes: int = 45
    blocked_apps: list[str] = Field(default_factory=list)


class VoiceAssistantRequest(BaseModel):
    command: str
    context: dict | None = None
