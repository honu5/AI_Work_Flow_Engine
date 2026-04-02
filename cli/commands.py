from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from execution.engine import WorkflowEngine
from plugins.registry import PluginRegistry
from storage.repository import Repository
from workflows.schema import WorkflowCreate
from workflows.validation import WorkflowValidator


def load_workflow(path: Path) -> WorkflowCreate:
    data = json.loads(path.read_text(encoding="utf-8"))
    return WorkflowCreate(**data)


def export_workflow(repository: Repository, workflow_id: str, output_path: Path) -> None:
    workflow = repository.get_workflow(workflow_id)
    if workflow is None:
        raise ValueError("Workflow not found")
    output_path.write_text(json.dumps(workflow["definition"], indent=2), encoding="utf-8")


def import_workflow(repository: Repository, payload: WorkflowCreate) -> str:
    workflow_id = repository.create_workflow_id(payload.name)
    repository.create_workflow(workflow_id, payload.name, payload.model_dump())
    repository.create_workflow_version(workflow_id, 1, payload.model_dump())
    return workflow_id


def validate_workflow(payload: WorkflowCreate, registry: PluginRegistry | None = None) -> List[str]:
    validator = WorkflowValidator(registry)
    result = validator.validate(payload.nodes)
    return result.errors


async def replay_execution(
    engine: WorkflowEngine, repository: Repository, execution_id: str
) -> Dict[str, object]:
    execution = repository.get_execution(execution_id)
    if execution is None:
        raise ValueError("Execution not found")
    workflow_id = execution["workflow_id"]
    return await engine.run_workflow(workflow_id, {}, async_mode=False)


def export_metrics(repository: Repository, execution_id: str) -> List[Dict[str, object]]:
    return repository.list_metrics(execution_id)


def export_logs(repository: Repository, execution_id: str) -> List[Dict[str, object]]:
    return repository.list_execution_logs(execution_id)


def cli_register_extra_plugins(registry: PluginRegistry) -> None:
    """Register bundled extra plugins from plugins.extra_plugins."""
    from plugins.extra_plugins import register_extra_plugins as _reg

    _reg(registry)

