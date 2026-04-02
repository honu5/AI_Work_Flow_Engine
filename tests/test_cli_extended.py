import json
from pathlib import Path

from cli.inspect import catalog_summary, describe_plugin, format_json
from workflows.dsl import compile_dsl


def test_catalog_summary_lists_templates():
    directory = Path(__file__).resolve().parents[1] / "workflows" / "catalog"
    summary = catalog_summary(directory)
    assert any(item["name"] == "incident_triage" for item in summary)


def test_describe_plugin(registry):
    details = describe_plugin(registry, "echo")
    payload = json.loads(format_json(details))
    assert payload["name"] == "echo"


def test_compile_dsl_from_example_file():
    path = Path(__file__).resolve().parents[1] / "examples" / "onboarding.wf.dsl"
    workflow = compile_dsl(path.read_text(encoding="utf-8"))
    assert workflow.name == "onboarding_from_dsl"
