import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_execution_trace_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = WorkflowCreate(
            name="trace-flow",
            nodes=[WorkflowNode(id="n1", plugin="add_numbers", input={"a": 1, "b": 2})],
        )
        create = await client.post("/workflows/", json=payload.model_dump())
        workflow_id = create.json()["id"]
        run = await client.post(
            f"/workflows/{workflow_id}/execute",
            json={"input": {}, "async_mode": False},
        )
        execution_id = run.json()["execution_id"]
        trace = await client.get(f"/executions/{execution_id}/trace")
        assert trace.status_code == 200
        body = trace.json()
        assert body["execution_id"] == execution_id
        assert "add_numbers" in body["plugins"]
