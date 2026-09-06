import json
import hashlib
from typing import Dict, Any, Tuple
from app.models.schemas import CanonicalEvidence, EvidenceHashResult
from app.services.hashing_service import hashing_service

class FingerprintService:
    """
    Fingerprint service for deterministic canonicalization and cryptographic SHA-256 generation.
    Canonical format: { "title": "...", "url": "...", "domain": "...", "platform": "...", "discoveredAt": "..." }
    """

    @staticmethod
    def canonicalize_metadata(metadata: Dict[str, Any]) -> str:
        """
        Deterministically canonicalize discovery metadata.
        Sorts keys alphabetically and strips redundant whitespace.
        """
        return hashing_service.canonicalize_json(metadata)

    @staticmethod
    def generate_sha256(data: bytes | str) -> str:
        """Generate hex-encoded SHA-256 digest."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    @classmethod
    def create_content_fingerprint(cls, evidence: CanonicalEvidence) -> EvidenceHashResult:
        """
        Produce a tamper-evident SHA-256 fingerprint from canonical evidence JSON.
        Returns EvidenceHashResult containing SHA-256 and EVM-compatible bytes32 hex.
        """
        return hashing_service.hash_evidence(evidence)

fingerprint_service = FingerprintService()
