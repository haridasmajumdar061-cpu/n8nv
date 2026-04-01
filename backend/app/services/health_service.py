from __future__ import annotations

from datetime import UTC, datetime

import redis.asyncio as redis
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine


class HealthService:
    async def liveness(self) -> dict:
        return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}

    async def readiness(self) -> dict:
        db_state = await self._check_database()
        redis_state = await self._check_redis()

        overall = "ok"
        if db_state["status"] != "ok" or redis_state["status"] != "ok":
            overall = "degraded"

        return {
            "status": overall,
            "timestamp": datetime.now(UTC).isoformat(),
            "dependencies": {"database": db_state, "redis": redis_state},
        }

    async def _check_database(self) -> dict:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "ok"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def _check_redis(self) -> dict:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        try:
            await client.ping()
            return {"status": "ok"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
        finally:
            await client.aclose()


health_service = HealthService()
