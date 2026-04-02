import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_catalog_templates_endpoint(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/catalog/templates")
        assert response.status_code == 200
        names = {item["name"] for item in response.json()}
        assert "incident_triage" in names
        assert len(names) >= 15


@pytest.mark.asyncio
async def test_catalog_template_detail(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/catalog/templates/incident_triage")
        assert response.status_code == 200
        body = response.json()
        assert body["valid"] is True
        assert body["critical_path"]
