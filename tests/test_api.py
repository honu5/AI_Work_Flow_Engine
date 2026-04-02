import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_api_workflow_execution(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = WorkflowCreate(
            name="api-flow",
            nodes=[WorkflowNode(id="n1", plugin="add_numbers", input={"a": 3, "b": 4})],
        )
        response = await client.post("/workflows/", json=payload.model_dump())
        assert response.status_code == 200
        workflow_id = response.json()["id"]

        exec_response = await client.post(
            f"/workflows/{workflow_id}/execute",
            json={"input": {}, "async_mode": False},
        )
        assert exec_response.status_code == 200
        assert exec_response.json()["status"] == "succeeded"
