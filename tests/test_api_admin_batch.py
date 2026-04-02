import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_admin_stats(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/admin/stats")
        assert response.status_code == 200
        body = response.json()
        assert "plugins_registered" in body


@pytest.mark.asyncio
async def test_batch_execute(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "workflows": [
                WorkflowCreate(
                    name="batch-1",
                    nodes=[WorkflowNode(id="n1", plugin="add_numbers", input={"a": 1, "b": 2})],
                ).model_dump()
            ],
            "checkpoint": False,
        }
        response = await client.post("/batch/execute", json=payload)
        assert response.status_code == 200
        assert response.json()["results"][0]["status"] == "succeeded"
