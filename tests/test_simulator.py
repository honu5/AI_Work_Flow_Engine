from execution.simulator import WorkflowSimulator
from workflows.recipes import build_text_pipeline_workflow


def test_simulator_returns_stages(registry):
    simulator = WorkflowSimulator(registry)
    result = simulator.simulate(build_text_pipeline_workflow())
    assert result.valid
    assert result.stages
    assert result.estimated_total_ms > 0
