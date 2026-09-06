import pytest
from app.models.schemas import CanonicalEvidence
from app.services.hashing_service import hashing_service

def test_canonical_json_key_order_invariance():
    """Verify that different dictionary key orders produce the EXACT same canonical JSON and SHA-256."""
    dict1 = {
        "source_image_sha256": "abc123def456",
        "reverse_search_provider": "SerpApi",
        "matched_url": "https://instagram.com/p/test",
        "platform": "Instagram",
        "search_timestamp": "2026-09-05T15:00:00Z",
        "match_metadata": {"title": "Test Post", "similarity": "95%"}
    }
    
    dict2 = {
        "platform": "Instagram",
        "match_metadata": {"similarity": "95%", "title": "Test Post"},
        "search_timestamp": "2026-09-05T15:00:00Z",
        "matched_url": "https://instagram.com/p/test",
        "reverse_search_provider": "SerpApi",
        "source_image_sha256": "abc123def456"
    }
    
    str1 = hashing_service.canonicalize_json(dict1)
    str2 = hashing_service.canonicalize_json(dict2)
    
    assert str1 == str2, "Canonical strings must be identical regardless of insertion order"

def test_evidence_hashing_structure():
    """Verify SHA-256 and bytes32 generation for CanonicalEvidence."""
    evidence = CanonicalEvidence(
        source_image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        reverse_search_provider="SerpApi (google_lens)",
        matched_url="https://www.instagram.com/p/Sample123",
        platform="Instagram",
        search_timestamp="2026-09-05T12:00:00Z",
        match_metadata={"domain": "instagram.com"}
    )
    
    result = hashing_service.hash_evidence(evidence)
    
    assert len(result.sha256_hash) == 64
    assert result.bytes32_hash.startswith("0x")
    assert len(result.bytes32_hash) == 66
    assert result.bytes32_hash == f"0x{result.sha256_hash}"

def test_tamper_sensitivity():
    """Verify that changing a single character in the evidence changes the resulting hash completely."""
    evidence_original = CanonicalEvidence(
        source_image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        reverse_search_provider="SerpApi",
        matched_url="https://www.instagram.com/p/Sample123",
        platform="Instagram",
        search_timestamp="2026-09-05T12:00:00Z",
        match_metadata={"domain": "instagram.com"}
    )
    
    evidence_tampered = CanonicalEvidence(
        source_image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        reverse_search_provider="SerpApi",
        matched_url="https://www.instagram.com/p/Sample124", # Altered by 1 character
        platform="Instagram",
        search_timestamp="2026-09-05T12:00:00Z",
        match_metadata={"domain": "instagram.com"}
    )
    
    res_orig = hashing_service.hash_evidence(evidence_original)
    res_tamp = hashing_service.hash_evidence(evidence_tampered)
    
    assert res_orig.sha256_hash != res_tamp.sha256_hash, "Altered evidence MUST produce a different SHA-256 hash"
    
    is_match, _, _ = hashing_service.verify_hash(evidence_tampered, res_orig.bytes32_hash)
    assert is_match is False, "Tampered evidence verification must fail"
