import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_execution_logs_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = WorkflowCreate(name="logs", nodes=[WorkflowNode(id="n1", plugin="echo")])
        response = await client.post("/workflows/", json=payload.model_dump())
        workflow_id = response.json()["id"]
        exec_response = await client.post(
            f"/workflows/{workflow_id}/execute",
            json={"input": {"x": 1}, "async_mode": False},
        )
        exec_id = exec_response.json()["execution_id"]

        logs = await client.get(f"/executions/{exec_id}/logs")
        assert logs.status_code == 200
        assert logs.json()
