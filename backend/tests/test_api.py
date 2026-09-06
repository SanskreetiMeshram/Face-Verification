import pytest
import cv2
import numpy as np
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.test_face_service import create_synthetic_face_image, create_blank_image

@pytest.mark.asyncio
async def test_api_health():
    """Test /api/health endpoint returns ok status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data

@pytest.mark.asyncio
async def test_api_system_status():
    """Test /api/config/status endpoint returns configuration safely without secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/config/status")
        assert response.status_code == 200
        data = response.json()
        assert "face_ai_status" in data
        assert "blockchain_network" in data
        assert "is_demo_mode_active" in data
        assert "private_key" not in data

@pytest.mark.asyncio
async def test_api_face_analyze_success():
    """Test /api/face/analyze with valid synthetic face image."""
    img_bytes = create_synthetic_face_image()
    files = {"file": ("face_test.jpg", img_bytes, "image/jpeg")}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/face/analyze", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["face_detected"] is True
        assert data["face_count"] >= 1
        assert len(data["source_image_sha256"]) == 64
        assert data["embedding_dimension"] == 128

@pytest.mark.asyncio
async def test_api_face_detect_blank_image():
    """Test /api/face/detect with blank image (0 faces)."""
    img_bytes = create_blank_image()
    files = {"file": ("blank.jpg", img_bytes, "image/jpeg")}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/face/detect", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["face_detected"] is False
        assert data["face_count"] == 0
        assert len(data["faces"]) == 0
        assert "No face detected" in data["message"]

@pytest.mark.asyncio
async def test_api_face_detect_corrupt_file():
    """Test /api/face/detect with invalid corrupted bytes returns 400."""
    files = {"file": ("corrupt.jpg", b"corrupted_binary_data_not_an_image", "image/jpeg")}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/face/detect", files=files)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_api_fingerprint_create():
    """Test /api/fingerprint/create deterministic canonical JSON and SHA-256."""
    payload = {
        "title": "Public Profile Showcase",
        "url": "https://instagram.com/p/sample_123",
        "domain": "instagram.com",
        "platform": "Instagram",
        "discovered_at": "2026-09-06T12:00:00Z",
        "source_image_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "search_provider": "SerpApi (google_lens)"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/fingerprint/create", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["sha256_hash"]) == 64
        assert data["bytes32_hash"].startswith("0x")
        assert len(data["bytes32_hash"]) == 66
        assert "canonical_json" in data

@pytest.mark.asyncio
async def test_api_reverse_search():
    """Test /api/search/reverse endpoint."""
    img_bytes = create_synthetic_face_image()
    files = {"file": ("query.jpg", img_bytes, "image/jpeg")}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/search/reverse", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "match_status" in data
        assert "provider" in data

@pytest.mark.asyncio
async def test_api_blockchain_register_and_verify():
    """Test /api/blockchain/register and /api/blockchain/verify endpoint flow."""
    evidence = {
        "source_image_sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "reverse_search_provider": "SerpApi (google_lens)",
        "matched_url": "https://instagram.com/p/record_abc",
        "platform": "Instagram",
        "search_timestamp": "2026-09-06T12:00:00Z",
        "match_metadata": {"title": "Profile Showcase", "domain": "instagram.com"}
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register
        reg_res = await ac.post("/api/blockchain/register", json={"evidence": evidence})
        assert reg_res.status_code == 200
        reg_data = reg_res.json()
        record_id = reg_data["record_id"]
        assert record_id > 0
        assert reg_data["evidence_hash"].startswith("0x")
        
        # Verify Match
        ver_res = await ac.post("/api/blockchain/verify", json={"record_id": record_id, "evidence": evidence})
        assert ver_res.status_code == 200
        ver_data = ver_res.json()
        assert ver_data["is_verified"] is True
        assert ver_data["status"] == "VERIFIED"
        assert ver_data["hashes_match"] is True

        # Verify Tampered Mismatch
        tampered_evidence = dict(evidence)
        tampered_evidence["matched_url"] = "https://instagram.com/p/tampered_fake_url"
        ver_fail = await ac.post("/api/blockchain/verify", json={"record_id": record_id, "evidence": tampered_evidence})
        assert ver_fail.status_code == 200
        ver_fail_data = ver_fail.json()
        assert ver_fail_data["is_verified"] is False
        assert ver_fail_data["status"] == "RECORD_MISMATCH"
        assert ver_fail_data["tamper_detected"] is True

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
        assert data["blockchain_record"] is not None
        assert data["verification"] is not None
        assert data["verification"]["is_verified"] is True
