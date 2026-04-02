from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowNode(BaseModel):
    id: str
    plugin: str
    input: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)
    retry: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[float] = None
    cache: Optional[Dict[str, Any]] = None
    requires: List[str] = Field(default_factory=list)


class WorkflowCreate(BaseModel):
    name: str
    nodes: List[WorkflowNode]


class WorkflowResponse(BaseModel):
    id: str
    name: str
    nodes: List[WorkflowNode]


class ExecutionRequest(BaseModel):
    workflow_id: Optional[str] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    async_mode: bool = False
