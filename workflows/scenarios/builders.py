from __future__ import annotations

from typing import Callable, Dict, List

from workflows.schema import WorkflowCreate, WorkflowNode


def _node(
    node_id: str,
    plugin: str,
    input_data: Dict[str, object],
    depends_on: List[str] | None = None,
) -> WorkflowNode:
    return WorkflowNode(
        id=node_id,
        plugin=plugin,
        input=input_data,
        depends_on=depends_on or [],
    )


def build_document_ingest() -> WorkflowCreate:
    return WorkflowCreate(
        name="document_ingest",
        nodes=[
            _node("capture", "echo", {"message": "upload://batch-17"}),
            _node(
                "normalize",
                "text.normalize",
                {"text": "  Quarterly Report Q1  ", "lowercase": True, "strip": True},
                ["capture"],
            ),
            _node("tokenize", "text.tokenize", {"text": "quarterly report q1"}, ["normalize"]),
            _node("sections", "analysis.section_index", {"text": "# Summary\n## Revenue"}, ["tokenize"]),
            _node("slug", "transform.slugify", {"text": "quarterly-report-q1"}, ["sections"]),
        ],
    )


def build_data_quality_gate() -> WorkflowCreate:
    records = [
        {"sku": "A1", "qty": 4},
        {"sku": "B2", "qty": 1},
        {"sku": "A1", "qty": 2},
    ]
    return WorkflowCreate(
        name="data_quality_gate",
        nodes=[
            _node("required", "validate.required_keys", {"data": {"source": "warehouse"}, "keys": ["source"]}),
            _node("group", "aggregate.group_sum", {"records": records, "group_field": "sku", "value_field": "qty"}, ["required"]),
            _node("profile", "analysis.numeric_profile", {"values": [4, 1, 2]}, ["group"]),
            _node("gate", "route.gate", {"condition": True, "value": "pass"}, ["profile"]),
        ],
    )


def build_order_fulfillment() -> WorkflowCreate:
    return WorkflowCreate(
        name="order_fulfillment",
        nodes=[
            _node("price", "transform.coerce_float", {"value": "89.99"}),
            _node("qty", "transform.coerce_int", {"value": "3"}),
            _node("subtotal", "math.multiply", {"values": [89.99, 3]}, ["price", "qty"]),
            _node("clamp", "math.clamp", {"value": 270.0, "minimum": 0, "maximum": 500}, ["subtotal"]),
            _node("label", "format.join", {"values": ["order", "ready"], "separator": "-"}, ["clamp"]),
        ],
    )


def build_customer_feedback() -> WorkflowCreate:
    return WorkflowCreate(
        name="customer_feedback",
        nodes=[
            _node("normalize", "text.normalize", {"text": "  Great service, quick response!  ", "strip": True}),
            _node("density", "analysis.keyword_density", {"text": "great service quick response", "keywords": ["great", "service"]}, ["normalize"]),
            _node("count", "text.count", {"text": "great service quick response"}, ["density"]),
            _node("wrap", "transform.wrap_columns", {"text": "great service quick response", "width": 16}, ["count"]),
        ],
    )


def build_security_scan() -> WorkflowCreate:
    return WorkflowCreate(
        name="security_scan",
        nodes=[
            _node("contains", "validate.contains", {"text": "auth token leaked in logs", "needle": "token"}),
            _node("replace", "transform.replace_chars", {"text": "auth-token-leaked", "mapping": {"-": "_"}}, ["contains"]),
            _node("route", "route.switch", {"key": "high", "routes": {"high": "block", "low": "allow"}}, ["replace"]),
            _node("report", "format.join", {"values": ["security", "scan"], "separator": "::"}, ["route"]),
        ],
    )


def build_release_gate() -> WorkflowCreate:
    return WorkflowCreate(
        name="release_gate",
        nodes=[
            _node("tests", "logic.all", {"values": [True, True, False]}),
            _node("gate", "route.gate", {"condition": False, "value": "hold"}, ["tests"]),
            _node("echo", "echo", {"message": "release-gate"}, ["gate"]),
        ],
    )


def build_marketing_attribution() -> WorkflowCreate:
    events = [
        {"channel": "email", "clicks": 12},
        {"channel": "social", "clicks": 45},
        {"channel": "email", "clicks": 8},
    ]
    return WorkflowCreate(
        name="marketing_attribution",
        nodes=[
            _node("count", "aggregate.count_by", {"records": events, "field": "channel"}),
            _node("top", "aggregate.top_n", {"records": events, "field": "clicks", "n": 2}, ["count"]),
            _node("sum", "aggregate.sum_field", {"records": events, "field": "clicks"}, ["top"]),
        ],
    )


def build_incident_postmortem() -> WorkflowCreate:
    return WorkflowCreate(
        name="incident_postmortem",
        nodes=[
            _node("timeline", "text.tokenize", {"text": "14:02 alert 14:05 rollback 14:20 resolved"}),
            _node("profile", "analysis.numeric_profile", {"values": [2, 3, 18, 20]}, ["timeline"]),
            _node("truncate", "transform.truncate", {"text": "postmortem draft content goes here", "max_length": 24}, ["profile"]),
            _node("publish", "format.join", {"values": ["postmortem", "ready"], "separator": "/"}, ["truncate"]),
        ],
    )


def build_feature_rollout() -> WorkflowCreate:
    return WorkflowCreate(
        name="feature_rollout",
        nodes=[
            _node("flag", "logic.not", {"value": False}),
            _node("route", "route.switch", {"key": "beta", "routes": {"beta": "enabled", "stable": "disabled"}}, ["flag"]),
            _node("notify", "echo", {"message": "rollout-stage"}, ["route"]),
        ],
    )


def build_compliance_review() -> WorkflowCreate:
    return WorkflowCreate(
        name="compliance_review",
        nodes=[
            _node("email", "validate.email", {"value": "auditor@example.com"}),
            _node("range", "validate.range", {"value": 12, "minimum": 1, "maximum": 31}, ["email"]),
            _node("length", "validate.length", {"text": "policy document", "minimum": 5, "maximum": 80}, ["range"]),
            _node("pad", "transform.pad", {"text": "approved", "width": 12, "align": "right"}, ["length"]),
        ],
    )


def build_support_macro() -> WorkflowCreate:
    return WorkflowCreate(
        name="support_macro",
        nodes=[
            _node("greet", "text.normalize", {"text": "  Hello, how can we help?  ", "strip": True}),
            _node("ngram", "text.ngram", {"tokens": ["hello", "how", "can", "we", "help"], "size": 2}, ["greet"]),
            _node("join", "format.join", {"values": ["macro", "ready"], "separator": ":"}, ["ngram"]),
        ],
    )


def build_etl_preview() -> WorkflowCreate:
    rows = [{"id": 1, "value": 10}, {"id": 2, "value": 20}, {"id": 3, "value": 30}]
    return WorkflowCreate(
        name="etl_preview",
        nodes=[
            _node("map", "data.map", {"values": rows, "key": "value"}),
            _node("sort", "data.sort", {"values": [30, 10, 20]}, ["map"]),
            _node("median", "data.median", {"values": [30, 10, 20]}, ["sort"]),
            _node("unique", "data.unique", {"values": ["a", "b", "a", "c"]}, ["median"]),
        ],
    )


_BUILDERS: Dict[str, Callable[[], WorkflowCreate]] = {
    "document_ingest": build_document_ingest,
    "data_quality_gate": build_data_quality_gate,
    "order_fulfillment": build_order_fulfillment,
    "customer_feedback": build_customer_feedback,
    "security_scan": build_security_scan,
    "release_gate": build_release_gate,
    "marketing_attribution": build_marketing_attribution,
    "incident_postmortem": build_incident_postmortem,
    "feature_rollout": build_feature_rollout,
    "compliance_review": build_compliance_review,
    "support_macro": build_support_macro,
    "etl_preview": build_etl_preview,
}


def list_scenario_builders() -> List[str]:
    return sorted(_BUILDERS.keys())


def build_scenario(name: str) -> WorkflowCreate:
    factory = _BUILDERS.get(name)
    if factory is None:
        raise KeyError(f"Unknown scenario: {name}")
    return factory()
