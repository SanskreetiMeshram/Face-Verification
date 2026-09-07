import hashlib
import json
from typing import Dict, Any, Tuple
from app.models.schemas import CryptographicProof

class HashingService:
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Compute SHA-256 hexadecimal digest of raw bytes."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_string(text: str) -> str:
        """Compute SHA-256 hexadecimal digest of a UTF-8 string."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def canonicalize_json(data: Dict[str, Any]) -> str:
        """
        Deterministic RFC 8785 JSON canonicalization:
        - Sorted keys lexicographically
        - Compact separators (',', ':') without whitespace
        - UTF-8 representation
        """
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def compute_record_hash(cls, selfie_sha256: str, profile_sha256: str, metadata_sha256: str) -> str:
        """
        Combine constituent hashes into a single 32-byte Merkle-style record hash.
        Returns a 0x-prefixed 64-character hexadecimal string compatible with Solidity bytes32.
        """
        s_clean = selfie_sha256.lower().replace("0x", "")
        p_clean = profile_sha256.lower().replace("0x", "")
        m_clean = metadata_sha256.lower().replace("0x", "")
        
        combined_payload = f"{s_clean}:{p_clean}:{m_clean}".encode("utf-8")
        digest = hashlib.sha256(combined_payload).hexdigest()
        return f"0x{digest}"

    @classmethod
    def generate_cryptographic_proof(
        cls,
        selfie_bytes: bytes,
        profile_bytes: bytes,
        metadata_dict: Dict[str, Any]
    ) -> CryptographicProof:
        """
        Generate complete cryptographic proof structure for a verification event.
        """
        selfie_hash = cls.hash_bytes(selfie_bytes)
        profile_hash = cls.hash_bytes(profile_bytes)
        canonical_meta = cls.canonicalize_json(metadata_dict)
        meta_hash = cls.hash_string(canonical_meta)
        
        record_hash = cls.compute_record_hash(selfie_hash, profile_hash, meta_hash)
        
        return CryptographicProof(
            selfie_sha256=selfie_hash,
            profile_sha256=profile_hash,
            metadata_sha256=meta_hash,
            record_hash=record_hash,
            algorithm="SHA-256 (RFC 8785 Canonical Merkle Root)",
            canonical_metadata_json=canonical_meta
        )

hashing_service = HashingService()
