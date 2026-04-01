import json

from openai import AsyncOpenAI

from app.core.config import settings


class AIService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def _ask_json(self, system_prompt: str, user_prompt: str, fallback: dict) -> dict:
        if not self.client:
            return fallback

        response = await self.client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def prompt_to_workflow(self, prompt: str) -> dict:
        fallback = {
            "name": "AI Generated Workflow",
            "nodes": [
                {"id": "1", "type": "trigger", "config": {"trigger": "manual"}},
                {"id": "2", "type": "ai", "config": {"task": prompt}},
            ],
            "edges": [{"source": "1", "target": "2"}],
        }
        return await self._ask_json(
            "Convert natural language to executable workflow JSON with nodes and edges.",
            prompt,
            fallback,
        )

    async def suggest_improvements(self, definition: dict) -> dict:
        fallback = {
            "suggestions": [
                "Add retry policy to external API nodes",
                "Add guard condition before send actions",
                "Store AI outputs in memory for future adaptation",
            ]
        }
        return await self._ask_json(
            "Suggest concrete improvements for a workflow JSON.",
            json.dumps(definition),
            fallback,
        )

    async def auto_debug(self, definition: dict, error_log: str) -> dict:
        fallback = {
            "root_cause": "Integration timeout",
            "fixes": ["Increase timeout", "Add fallback route", "Enable exponential backoff"],
            "patched_workflow": definition,
        }
        return await self._ask_json(
            "Debug workflow failures and provide root cause + fixed workflow JSON.",
            json.dumps({"workflow": definition, "error_log": error_log}),
            fallback,
        )

    async def generate_daily_plan(self, payload: dict) -> dict:
        fallback = {
            "date": payload.get("date"),
            "routine": [
                {"time": "06:30", "task": "Morning planning"},
                {"time": "09:00", "task": "Deep work block"},
                {"time": "14:00", "task": "Skill monetization sprint"},
            ],
        }
        return await self._ask_json("Generate a practical daily planner.", json.dumps(payload), fallback)

    async def generate_income_suggestions(self, payload: dict) -> dict:
        fallback = {
            "strategies": [
                {
                    "title": "Micro-consulting",
                    "steps": ["Package one skill", "Launch on social profile", "Book 30-min calls"],
                }
            ]
        }
        return await self._ask_json("Create income ideas based on skills and time.", json.dumps(payload), fallback)

    async def voice_assistant_response(self, payload: dict) -> dict:
        fallback = {
            "response": f"Received command: {payload.get('command', '')}",
            "actions": ["log_memory", "suggest_next_task"],
        }
        return await self._ask_json("Act as AI Life OS voice assistant.", json.dumps(payload), fallback)


ai_service = AIService()
