from fastapi import APIRouter

from app.api.routes import ai, auth, executions, integrations, lifeos, logs, workflows

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(lifeos.router, prefix="/life-os", tags=["life-os"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
