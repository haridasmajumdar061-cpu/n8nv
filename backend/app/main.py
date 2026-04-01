from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.database import Base, engine
from app.core.logging import configure_logging
from app.services.health_service import health_service
from app.utils.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield


app = FastAPI(title="AI Life OS API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return await health_service.readiness()


@app.get("/health/live")
async def health_live() -> dict:
    return await health_service.liveness()


@app.get("/health/ready")
async def health_ready() -> dict:
    return await health_service.readiness()
