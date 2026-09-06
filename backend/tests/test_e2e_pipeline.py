import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.face_service import face_service
from app.services.reverse_search import reverse_search_service
from app.services.fingerprint_service import fingerprint_service
from app.services.blockchain_service import blockchain_service
from app.models.schemas import CanonicalEvidence
from tests.test_face_service import create_synthetic_face_image

@pytest.mark.asyncio
async def test_full_pipeline_step_by_step():
    """
    Execute step-by-step verified demonstration of complete FaceChain Verify pipeline:
    1. Input authorized image bytes & SHA-256
    2. Face Detection & 128-D Temporary Encoding
    3. Genuine Reverse Image Search discovery
    4. Matching Public Result extraction
    5. Canonical Metadata & SHA-256 Content Fingerprinting
    6. Blockchain smart contract registration
    7. Independent cryptographic re-verification
    """
    # 1. Input Image
    img_bytes = create_synthetic_face_image()
    assert len(img_bytes) > 0

    # 2. Face Detection
    face_res = face_service.detect_and_encode(img_bytes, "test_face.jpg")
    assert face_res.face_detected is True
    assert face_res.face_count >= 1
    assert len(face_res.source_image_sha256) == 64
    assert face_res.embedding_dimension == 128
    assert len(face_res.faces[0].embedding_fingerprint) == 64

    # 3. Reverse Image Search
    search_res = await reverse_search_service.execute_search(img_bytes, "test_face.jpg")
    assert search_res.success is True
    assert search_res.results_count > 0
    assert search_res.primary_match is not None

    # 4. Result Extraction
    match = search_res.primary_match
    assert match.url != ""
    assert match.domain != ""

    # 5. Canonical Content Fingerprint
    evidence = CanonicalEvidence(
        source_image_sha256=face_res.source_image_sha256,
        reverse_search_provider=search_res.provider,
        matched_url=match.url,
        platform=match.platform or "Web Match",
        search_timestamp="2026-09-06T12:00:00Z",
        match_metadata={
            "title": match.title,
            "domain": match.domain,
            "url": match.url,
            "platform": match.platform,
            "discoveredAt": "2026-09-06T12:00:00Z"
        }
    )
    fp_res = fingerprint_service.create_content_fingerprint(evidence)
    assert len(fp_res.sha256_hash) == 64
    assert fp_res.bytes32_hash.startswith("0x")

    # 6. Blockchain Registration
    bc_res = await blockchain_service.register_evidence_on_chain(evidence)
    assert bc_res.success is True
    assert bc_res.record_id > 0
    assert bc_res.evidence_hash == fp_res.bytes32_hash
    assert bc_res.transaction_hash.startswith("0x")

    # 7. Independent Cryptographic Re-Verification
    verify_res = await blockchain_service.verify_evidence(bc_res.record_id, evidence)
    assert verify_res.is_verified is True
    assert verify_res.status == "VERIFIED"
    assert verify_res.hashes_match is True
    assert verify_res.tamper_detected is False
