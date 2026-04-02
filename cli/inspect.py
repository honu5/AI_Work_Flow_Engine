from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from plugins.registry import PluginRegistry
from storage.repository import Repository
from workflows.catalog.loader import load_catalog
from workflows.workflow_compiler import compile_workflow
from workflows.schema import WorkflowCreate


def describe_plugin(registry: PluginRegistry, name: str) -> Dict[str, Any]:
    return registry.get_details(name)


def list_registered_plugins(registry: PluginRegistry) -> List[Dict[str, Any]]:
    return registry.list_plugins()


def describe_workflow(workflow: WorkflowCreate, registry: PluginRegistry) -> Dict[str, Any]:
    compiled = compile_workflow(workflow, registry=registry)
    return {
        "name": workflow.name,
        "node_count": len(workflow.nodes),
        "stages": compiled.stages,
        "critical_path": compiled.critical_path,
        "valid": compiled.valid,
        "diagnostics": [diag.__dict__ for diag in compiled.diagnostics],
    }


def catalog_summary(catalog_dir: Path) -> List[Dict[str, Any]]:
    templates = load_catalog(catalog_dir)
    return [
        {
            "name": template.name,
            "nodes": len(template.nodes),
            "plugins": sorted({node.plugin for node in template.nodes}),
        }
        for template in templates
    ]


def format_json(data: Any) -> str:
    return json.dumps(data, indent=2)
