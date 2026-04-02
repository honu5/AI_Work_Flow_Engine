from __future__ import annotations

from typing import Any, Dict, List

from workflows.schema import WorkflowCreate, WorkflowNode


def _node(node_id: str, plugin: str, input_data: Dict[str, Any], depends_on: List[str] | None = None) -> WorkflowNode:
    return WorkflowNode(id=node_id, plugin=plugin, input=input_data, depends_on=depends_on or [])


def build_text_pipeline_workflow() -> WorkflowCreate:
    nodes = [
        _node("normalize", "text.normalize", {"text": "  Example  ", "lowercase": True, "strip": True}),
        _node("tokenize", "text.tokenize", {"text": "Example"}, depends_on=["normalize"]),
        _node("count", "text.count", {"text": "Example"}, depends_on=["normalize"]),
        _node("ngrams", "text.ngram", {"tokens": ["example", "pipeline"], "size": 2}, depends_on=["tokenize"]),
    ]
    return WorkflowCreate(name="text_pipeline", nodes=nodes)


def build_analysis_workflow() -> WorkflowCreate:
    nodes = [
        _node("density", "analysis.keyword_density", {"text": "alpha beta alpha", "keywords": ["alpha", "beta"]}),
        _node("sections", "analysis.section_index", {"text": "# Intro\n## Details"}, depends_on=["density"]),
        _node("profile", "analysis.numeric_profile", {"values": [1, 2, 3, 4, 5]}, depends_on=["sections"]),
    ]
    return WorkflowCreate(name="analysis_workflow", nodes=nodes)


def build_validation_workflow() -> WorkflowCreate:
    nodes = [
        _node("required", "validate.required_keys", {"data": {"name": "demo"}, "keys": ["name", "id"]}),
        _node("range", "validate.range", {"value": 8, "minimum": 1, "maximum": 10}, depends_on=["required"]),
        _node("length", "validate.length", {"text": "workflow", "minimum": 3, "maximum": 20}, depends_on=["range"]),
        _node("contains", "validate.contains", {"text": "workflow", "needle": "flow"}, depends_on=["length"]),
        _node("email", "validate.email", {"value": "demo@example.com"}, depends_on=["contains"]),
    ]
    return WorkflowCreate(name="validation_workflow", nodes=nodes)


def build_reporting_workflow() -> WorkflowCreate:
    nodes = [
        _node("group", "data.group", {"values": [{"team": "a", "value": 1}, {"team": "b", "value": 2}], "key": "team"}),
        _node("map", "data.map", {"values": [{"value": 1}, {"value": 2}], "key": "value"}, depends_on=["group"]),
        _node("sort", "data.sort", {"values": [3, 1, 2]}, depends_on=["map"]),
        _node("median", "data.median", {"values": [3, 1, 2]}, depends_on=["sort"]),
    ]
    return WorkflowCreate(name="reporting_workflow", nodes=nodes)


def build_routing_workflow() -> WorkflowCreate:
    nodes = [
        _node("route", "route.switch", {"key": "default", "routes": {"default": "primary", "fallback": "secondary"}}),
        _node("format", "format.join", {"values": ["route", "workflow"], "separator": "::"}, depends_on=["route"]),
        _node("reverse", "reverse", {"text": "route"}, depends_on=["format"]),
    ]
    return WorkflowCreate(name="routing_workflow", nodes=nodes)


def build_catalog() -> List[WorkflowCreate]:
    return [
        build_text_pipeline_workflow(),
        build_analysis_workflow(),
        build_validation_workflow(),
        build_reporting_workflow(),
        build_routing_workflow(),
    ]
