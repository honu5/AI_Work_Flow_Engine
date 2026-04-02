from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_registry
from workflows.catalog.loader import load_catalog
from workflows.workflow_compiler import compile_workflow

router = APIRouter()
CATALOG_DIR = Path(__file__).resolve().parents[2] / "workflows" / "catalog"


@router.get("/templates")
async def list_catalog_templates():
    templates = load_catalog(CATALOG_DIR)
    return [
        {
            "name": template.name,
            "node_count": len(template.nodes),
            "plugins": [node.plugin for node in template.nodes],
        }
        for template in templates
    ]


@router.get("/templates/{template_name}")
async def get_catalog_template(template_name: str, registry=Depends(get_registry)):
    templates = load_catalog(CATALOG_DIR)
    match = next((item for item in templates if item.name == template_name), None)
    if match is None:
        raise HTTPException(status_code=404, detail="Template not found")
    compiled = compile_workflow(match, registry=registry)
    return {
        "name": match.name,
        "nodes": [node.model_dump() for node in match.nodes],
        "stages": compiled.stages,
        "critical_path": compiled.critical_path,
        "valid": compiled.valid,
        "diagnostics": [diag.__dict__ for diag in compiled.diagnostics],
    }
