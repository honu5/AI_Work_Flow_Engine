from execution.trace import ExecutionTrace, build_trace_from_execution


def test_execution_trace_aggregates_events():
    trace = ExecutionTrace(execution_id="exec_1", workflow_id="wf_1")
    trace.record("n1", "echo", "succeeded", duration_ms=12.5)
    trace.record("n2", "add_numbers", "failed", duration_ms=4.0, error="boom")
    assert trace.total_duration_ms() == 16.5
    assert trace.plugins_used() == ["add_numbers", "echo"]
    assert len(trace.failed_nodes()) == 1


def test_build_trace_from_execution_payload():
    execution = {
        "id": "exec_1",
        "workflow_id": "wf_1",
        "logs": [
            {"node_id": "n1", "status": "succeeded", "error": None},
            {"node_id": "n2", "status": "succeeded", "error": None},
        ],
    }
    workflow = {
        "definition": {
            "nodes": [
                {"id": "n1", "plugin": "echo"},
                {"id": "n2", "plugin": "add_numbers"},
            ]
        }
    }
    trace = build_trace_from_execution(execution, workflow)
    assert trace.plugins_used() == ["add_numbers", "echo"]
