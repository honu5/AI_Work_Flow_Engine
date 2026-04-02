import pytest
from httpx import AsyncClient

from workflows.schema import WorkflowCreate, WorkflowNode


@pytest.mark.asyncio
async def test_list_executions_filters(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = WorkflowCreate(
            name="filter-flow",
            nodes=[WorkflowNode(id="n1", plugin="echo")],
        )
        response = await client.post("/workflows/", json=payload.model_dump())
        workflow_id = response.json()["id"]

        await client.post(
            f"/workflows/{workflow_id}/execute",
            json={"input": {}, "async_mode": False},
        )

        execs = await client.get(f"/executions/?workflow_id={workflow_id}")
        assert execs.status_code == 200
        assert execs.json()
