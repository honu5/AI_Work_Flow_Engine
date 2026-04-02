from __future__ import annotations

from workflows.recipes import (
    build_analysis_workflow,
    build_catalog,
    build_reporting_workflow,
    build_routing_workflow,
    build_text_pipeline_workflow,
    build_validation_workflow,
)


def test_text_pipeline_recipe_shape():
    workflow = build_text_pipeline_workflow()
    assert workflow.name == "text_pipeline"
    assert [node.plugin for node in workflow.nodes][:2] == ["text.normalize", "text.tokenize"]


def test_analysis_recipe_shape():
    workflow = build_analysis_workflow()
    assert workflow.name == "analysis_workflow"
    assert workflow.nodes[0].plugin == "analysis.keyword_density"


def test_validation_recipe_shape():
    workflow = build_validation_workflow()
    assert len(workflow.nodes) == 5
    assert workflow.nodes[-1].plugin == "validate.email"


def test_reporting_recipe_shape():
    workflow = build_reporting_workflow()
    assert workflow.nodes[0].plugin == "data.group"
    assert workflow.nodes[-1].plugin == "data.median"


def test_routing_recipe_shape():
    workflow = build_routing_workflow()
    assert workflow.nodes[0].plugin == "route.switch"
    assert workflow.nodes[1].plugin == "format.join"


def test_build_catalog_contains_all_recipes():
    catalog = build_catalog()
    names = {workflow.name for workflow in catalog}
    assert names == {
        "text_pipeline",
        "analysis_workflow",
        "validation_workflow",
        "reporting_workflow",
        "routing_workflow",
    }
