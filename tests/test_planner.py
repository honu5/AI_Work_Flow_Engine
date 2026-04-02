import pytest

from execution.planner import ExecutionPlanner


def test_planner_builds_stages():
    planner = ExecutionPlanner()
    plan = planner.build(
        [
            {"id": "a", "depends_on": []},
            {"id": "b", "depends_on": ["a"]},
            {"id": "c", "depends_on": ["a"]},
        ]
    )
    assert plan.stages[0] == ["a"]
    assert set(plan.stages[1]) == {"b", "c"}


def test_planner_detects_cycle():
    planner = ExecutionPlanner()
    with pytest.raises(ValueError):
        planner.build(
            [
                {"id": "a", "depends_on": ["b"]},
                {"id": "b", "depends_on": ["a"]},
            ]
        )
