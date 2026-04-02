from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_registry

router = APIRouter()


@router.get("/")
async def list_plugins(registry=Depends(get_registry)):
    return registry.list_plugins()


@router.get("/{plugin_name}")
async def get_plugin(plugin_name: str, registry=Depends(get_registry)):
    try:
        return registry.get_details(plugin_name)
    except Exception:
        raise HTTPException(status_code=404, detail="Plugin not found")
