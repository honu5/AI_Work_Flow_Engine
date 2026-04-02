from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_registry, get_repository

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-workflow-engine"}


@router.get("/ready")
async def readiness_check(repository=Depends(get_repository), registry=Depends(get_registry)):
    workflows = repository.list_workflows(limit=1)
    plugins = registry.list_plugins()
    return {
        "status": "ready",
        "workflows_indexed": len(workflows) >= 0,
        "plugins_registered": len(plugins),
    }
