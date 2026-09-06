import json
import hashlib
from typing import Dict, Any, Tuple
from app.models.schemas import CanonicalEvidence, EvidenceHashResult

class HashingService:
    """
    Service responsible for deterministic JSON canonicalization and SHA-256 hashing.
    Generates EVM-compatible bytes32 evidence fingerprints for smart contract registration.
    """

    @staticmethod
    def canonicalize_json(data: Dict[str, Any]) -> str:
        """
        Canonicalize a dictionary into a deterministic JSON string:
        - Sorted keys at all levels
        - Standard separators (',', ':') with no extraneous whitespace
        - UTF-8 string representation
        - Ensures identical JSON hashes regardless of key insertion order.
        """
        return json.dumps(
            data,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
        )

    @classmethod
    def hash_evidence(cls, evidence: CanonicalEvidence) -> EvidenceHashResult:
        """
        Convert CanonicalEvidence into a deterministic JSON string and calculate its SHA-256 hash.
        Returns the EvidenceHashResult containing the canonical JSON, SHA-256 hex, and bytes32.
        """
        evidence_dict = evidence.model_dump()
        canonical_str = cls.canonicalize_json(evidence_dict)
        
        # Calculate SHA-256
        sha256_hex = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        bytes32_hash = f"0x{sha256_hex}"
        
        return EvidenceHashResult(
            evidence=evidence,
            canonical_json=canonical_str,
            sha256_hash=sha256_hex,
            bytes32_hash=bytes32_hash,
            content_fingerprint=sha256_hex
        )

    @classmethod
    def verify_hash(cls, evidence: CanonicalEvidence, expected_hash: str) -> Tuple[bool, str, str]:
        """
        Verify whether the evidence calculates to the expected hash.
        Returns: (is_match, calculated_bytes32, expected_bytes32_normalized)
        """
        result = cls.hash_evidence(evidence)
        calc_b32 = result.bytes32_hash.lower()
        
        exp_normalized = expected_hash.strip().lower()
        if not exp_normalized.startswith("0x"):
            exp_normalized = f"0x{exp_normalized}"
            
        is_match = (calc_b32 == exp_normalized)
        return is_match, calc_b32, exp_normalized

# Global singleton instance
hashing_service = HashingService()
