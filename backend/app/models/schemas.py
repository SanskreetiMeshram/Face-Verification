from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# Face Analysis Schemas
# -----------------------------------------------------------------------------
class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate in pixels")
    y: int = Field(..., description="Top-left Y coordinate in pixels")
    width: int = Field(..., description="Width of bounding box in pixels")
    height: int = Field(..., description="Height of bounding box in pixels")
    normalized_x: float = Field(..., description="Normalized X (0.0 - 1.0)")
    normalized_y: float = Field(..., description="Normalized Y (0.0 - 1.0)")
    normalized_width: float = Field(..., description="Normalized width (0.0 - 1.0)")
    normalized_height: float = Field(..., description="Normalized height (0.0 - 1.0)")

class FaceDetail(BaseModel):
    index: int
    confidence: float
    quality_score: Optional[float] = None
    embedding_dimension: int = 128
    bounding_box: BoundingBox
    landmarks: Optional[Dict[str, List[int]]] = None
    embedding_fingerprint: str = Field(..., description="Cryptographic SHA-256 fingerprint of the embedding vector")

class FaceDetectionResult(BaseModel):
    face_detected: bool
    face_count: int
    faces: List[FaceDetail] = []
    primary_confidence: float = 0.0
    embedding_generated: bool
    embedding_dimension: int = 128
    source_image_sha256: str
    image_width: int
    image_height: int
    annotated_image_url: Optional[str] = None
    detector_model: str = "OpenCV Neural & Multi-Cascade Engine"
    message: str

class FaceCompareResult(BaseModel):
    is_match: bool
    similarity_score: float = Field(..., description="Cosine similarity score between -1.0 and 1.0")
    match_percentage: float = Field(..., description="Percentage match between 0.0% and 100.0%")
    euclidean_distance: float = Field(..., description="L2 Euclidean distance between embedding vectors")
    verdict: str = Field(..., description="'BIOMETRIC_MATCH_CONFIRMED' or 'BIOMETRIC_MISMATCH'")
    confidence_level: str = Field(default="HIGH", description="Confidence level of biometric evaluation")
    face1_detected: bool
    face2_detected: bool
    face1_fingerprint: Optional[str] = None
    face2_fingerprint: Optional[str] = None
    message: str

# -----------------------------------------------------------------------------
# Reverse Image Search & Discovered Content Schemas
# -----------------------------------------------------------------------------
class SearchResultItem(BaseModel):
    title: str = ""
    url: str
    domain: str
    thumbnail: Optional[str] = None
    source: str = "Reverse Image Search"
    platform: Optional[str] = Field(None, description="Classified public web / social platform")
    is_social_media: bool = False
    similarity: Optional[str] = None
    confidence_score: Optional[float] = None
    published_at: Optional[str] = None
    discovered_at: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None

class ReverseSearchResponse(BaseModel):
    success: bool
    provider: str
    results_count: int
    match_status: str = Field(default="FOUND", description="'FOUND', 'POSSIBLE_MATCH', 'NOT_FOUND', 'ERROR'")
    social_match_found: bool
    primary_match: Optional[SearchResultItem] = None
    all_results: List[SearchResultItem] = []
    is_demo_mode: bool = False
    demo_badge_message: Optional[str] = None
    error_message: Optional[str] = None

# -----------------------------------------------------------------------------
# Canonical Evidence & Content Fingerprint Schemas
# -----------------------------------------------------------------------------
class DiscoveredContentMetadata(BaseModel):
    title: str
    url: str
    domain: str
    platform: str
    discoveredAt: str

class CanonicalEvidence(BaseModel):
    source_image_sha256: str
    reverse_search_provider: str
    matched_url: str
    platform: str
    search_timestamp: str
    match_metadata: Dict[str, Any] = {}

class EvidenceHashResult(BaseModel):
    evidence: CanonicalEvidence
    canonical_json: str
    sha256_hash: str
    bytes32_hash: str = Field(..., description="0x-prefixed 32-byte hex for EVM")
    content_fingerprint: str = Field(default="", description="Content fingerprint representation")

class FingerprintCreateRequest(BaseModel):
    title: str
    url: str
    domain: str
    platform: str
    discovered_at: Optional[str] = None
    source_image_sha256: Optional[str] = None
    search_provider: Optional[str] = None

class FingerprintCreateResponse(BaseModel):
    canonical_json: str
    sha256_hash: str
    bytes32_hash: str
    evidence: CanonicalEvidence

# -----------------------------------------------------------------------------
# Blockchain Schemas
# -----------------------------------------------------------------------------
class BlockchainRecordData(BaseModel):
    record_id: int
    evidence_hash: str
    result_url: str
    platform: str
    timestamp: int
    timestamp_iso: str
    submitter: str
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    explorer_tx_url: Optional[str] = None
    explorer_contract_url: Optional[str] = None
    chain_name: str
    chain_id: int

class BlockchainRegisterRequest(BaseModel):
    evidence: CanonicalEvidence
    evidence_hash: Optional[str] = None

class BlockchainRegisterResponse(BaseModel):
    success: bool
    record_id: int
    evidence_hash: str
    transaction_hash: str
    block_number: int
    gas_used: Optional[int] = None
    contract_address: str
    explorer_tx_url: str
    submitter: str
    timestamp: str
    chain_id: int
    chain_name: str
    is_simulated: bool = False
    error_message: Optional[str] = None

# -----------------------------------------------------------------------------
# Verification Schemas
# -----------------------------------------------------------------------------
class VerifyEvidenceRequest(BaseModel):
    record_id: int
    evidence: CanonicalEvidence

class VerificationResult(BaseModel):
    record_id: int
    is_verified: bool
    status: str = Field(..., description="'VERIFIED' or 'RECORD_MISMATCH' or 'NOT_FOUND'")
    calculated_hash: str
    blockchain_hash: str
    hashes_match: bool
    blockchain_record: Optional[BlockchainRecordData] = None
    verification_message: str
    tamper_detected: bool = False
    verified_at: str

# -----------------------------------------------------------------------------
# Full End-to-End Pipeline Response
# -----------------------------------------------------------------------------
class PipelineStepStatus(BaseModel):
    step_number: int
    name: str
    status: str = Field(..., description="'pending', 'processing', 'success', 'failed', 'skipped'")
    message: str
    timestamp: Optional[str] = None

class PipelineRunResponse(BaseModel):
    success: bool
    pipeline_id: str
    steps: List[PipelineStepStatus]
    face_analysis: Optional[FaceDetectionResult] = None
    reverse_search: Optional[ReverseSearchResponse] = None
    evidence_hash: Optional[EvidenceHashResult] = None
    blockchain_record: Optional[BlockchainRegisterResponse] = None
    verification: Optional[VerificationResult] = None
    is_demo_mode: bool = False
    error_details: Optional[str] = None

# -----------------------------------------------------------------------------
# System Status Schema
# -----------------------------------------------------------------------------
class SystemStatusResponse(BaseModel):
    app_name: str
    app_version: str
    face_ai_status: str
    face_detector_model: str
    reverse_image_provider: str
    reverse_image_api_configured: bool
    blockchain_network: str
    blockchain_chain_id: int
    blockchain_rpc_connected: bool
    smart_contract_configured: bool
    smart_contract_address: str
    is_demo_mode_active: bool
