import logging
from typing import Optional
from app.models.schemas import CanonicalEvidence, VerificationResult
from app.services.blockchain_service import blockchain_service

logger = logging.getLogger("facechain.verification_service")

class VerificationService:
    """
    Independent Verification Service.
    Retrieves stored on-chain fingerprint, reconstructs canonical discovered metadata,
    recomputes SHA-256, compares the two, and returns VERIFIED or RECORD_MISMATCH.
    """

    @staticmethod
    async def verify_record(record_id: int, evidence: CanonicalEvidence) -> VerificationResult:
        """
        Execute independent cryptographic re-verification against immutable blockchain state.
        """
        return await blockchain_service.verify_evidence(record_id, evidence)

verification_service = VerificationService()
