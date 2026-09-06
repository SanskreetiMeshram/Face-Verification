import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.test_face_service import create_synthetic_face_image

@pytest.mark.asyncio
async def test_api_health():
    """Test /api/health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_system_status():
    """Test /api/config/status endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/config/status")
        assert response.status_code == 200
        data = response.json()
        assert "face_ai_status" in data
        assert "blockchain_network" in data
        assert "is_demo_mode_active" in data

@pytest.mark.asyncio
async def test_api_pipeline_run():
    """Test full /api/pipeline/run endpoint with synthetic image."""
    img_bytes = create_synthetic_face_image()
    files = {"file": ("face_test.jpg", img_bytes, "image/jpeg")}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/pipeline/run", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "pipeline_id" in data
        assert len(data["steps"]) >= 5
        assert data["evidence_hash"] is not None
