from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List

from execution.engine import WorkflowEngine
from plugins.registry import PluginRegistry
from storage.repository import Repository
from workflows.catalog.loader import load_catalog
from workflows.service import WorkflowService


async def run_catalog_subset(
    engine: WorkflowEngine,
    repository: Repository,
    catalog_dir: Path,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    service = WorkflowService(repository)
    templates = load_catalog(catalog_dir)[:limit]
    results: List[Dict[str, Any]] = []
    for template in templates:
        workflow = service.create_workflow(template)
        execution = await engine.run_workflow(workflow.id, {}, async_mode=False)
        results.append(
            {
                "workflow": template.name,
                "execution_id": execution.execution_id,
                "status": execution.status.value,
            }
        )
    return results


def run_catalog_subset_sync(
    engine: WorkflowEngine,
    repository: Repository,
    catalog_dir: Path,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    return asyncio.run(run_catalog_subset(engine, repository, catalog_dir, limit=limit))
