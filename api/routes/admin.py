from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_registry, get_repository
from execution.simulator import WorkflowSimulator
from storage.analytics import RepositoryAnalytics
from workflows.catalog.loader import load_catalog
from pathlib import Path

router = APIRouter()
CATALOG_DIR = Path(__file__).resolve().parents[2] / "workflows" / "catalog"


@router.get("/stats")
async def admin_stats(repository=Depends(get_repository), registry=Depends(get_registry)):
    analytics = RepositoryAnalytics(repository)
    templates = load_catalog(CATALOG_DIR)
    return {
        "workflows": analytics.workflow_summary(),
        "executions": analytics.execution_summary(),
        "plugins_registered": len(registry.list_plugins()),
        "catalog_templates": len(templates),
    }


@router.post("/simulate")
async def admin_simulate(payload: dict, registry=Depends(get_registry)):
    from workflows.schema import WorkflowCreate

    workflow = WorkflowCreate(**payload)
    simulator = WorkflowSimulator(registry)
    return simulator.simulate(workflow).to_dict()
