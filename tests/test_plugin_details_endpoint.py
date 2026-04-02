import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_plugin_detail_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/plugins/echo")
        assert response.status_code == 200
        assert response.json()["name"] == "echo"
