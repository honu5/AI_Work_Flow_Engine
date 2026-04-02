import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_plugin_detail_not_found(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/plugins/missing")
        assert response.status_code == 404
