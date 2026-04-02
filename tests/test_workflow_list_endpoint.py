import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_workflow_list_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = WorkflowCreate(name="list", nodes=[WorkflowNode(id="n1", plugin="echo")])
        await client.post("/workflows/", json=payload.model_dump())

        response = await client.get("/workflows/?name=list")
        assert response.status_code == 200
        assert response.json()
