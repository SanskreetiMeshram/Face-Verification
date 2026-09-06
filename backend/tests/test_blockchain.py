import pytest
from app.models.schemas import CanonicalEvidence
from app.services.blockchain_service import blockchain_service
from app.services.hashing_service import hashing_service

@pytest.mark.asyncio
async def test_register_and_verify_evidence():
    """Verify end-to-end evidence registration, on-chain retrieval, and tamper detection."""
    evidence = CanonicalEvidence(
        source_image_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        reverse_search_provider="SerpApi (Google Lens)",
        matched_url="https://www.instagram.com/p/TestRecord99",
        platform="Instagram",
        search_timestamp="2026-09-05T15:00:00Z",
        match_metadata={"domain": "instagram.com", "title": "Verified Profile Match"}
    )
    
    # 1. Register evidence
    reg_resp = await blockchain_service.register_evidence_on_chain(evidence)
    assert reg_resp.success is True
    assert reg_resp.record_id > 0
    assert reg_resp.evidence_hash.startswith("0x")
    assert reg_resp.transaction_hash.startswith("0x")
    
    # 2. Query record by ID
    record = await blockchain_service.get_record_by_id(reg_resp.record_id)
    assert record is not None
    assert record.evidence_hash.lower() == reg_resp.evidence_hash.lower()
    assert record.result_url == evidence.matched_url
    assert record.platform == evidence.platform
    
    # 3. Verify identical evidence (Must pass: VERIFIED)
    verify_pass = await blockchain_service.verify_evidence(reg_resp.record_id, evidence)
    assert verify_pass.is_verified is True
    assert verify_pass.status == "VERIFIED"
    assert verify_pass.hashes_match is True
    assert verify_pass.tamper_detected is False
    
    # 4. Verify tampered evidence (Must fail: RECORD_MISMATCH)
    tampered_evidence = CanonicalEvidence(
        source_image_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        reverse_search_provider="SerpApi (Google Lens)",
        matched_url="https://www.instagram.com/p/TAMPERED_URL", # Tampered!
        platform="Instagram",
        search_timestamp="2026-09-05T15:00:00Z",
        match_metadata={"domain": "instagram.com"}
    )
    verify_fail = await blockchain_service.verify_evidence(reg_resp.record_id, tampered_evidence)
    assert verify_fail.is_verified is False
    assert verify_fail.status == "RECORD_MISMATCH"
    assert verify_fail.hashes_match is False
    assert verify_fail.tamper_detected is True
