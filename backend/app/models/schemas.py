from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    width: int = Field(..., description="Face bounding box width")
    height: int = Field(..., description="Face bounding box height")

class LandmarkPoint(BaseModel):
    x: int
    y: int
    name: Optional[str] = None

class FaceDetail(BaseModel):
    detected: bool = Field(default=False, description="Whether a face was detected")
    face_count: int = Field(default=0, description="Number of faces found")
    confidence: float = Field(default=0.0, description="Face detector confidence score")
    bounding_box: Optional[BoundingBox] = None
    landmarks: Optional[List[LandmarkPoint]] = None
    embedding_dim: int = Field(default=128, description="Dimensions of normalized face embedding")
    embedding_hash: Optional[str] = Field(default=None, description="SHA-256 fingerprint of face embedding vector")
    image_width: int = Field(default=0)
    image_height: int = Field(default=0)
    face_crop_base64: Optional[str] = Field(default=None, description="Base64 thumbnail of cropped face for visual confirmation")
    error: Optional[str] = None

class FaceComparisonResult(BaseModel):
    is_match: bool = Field(default=False, description="Whether face comparison passes confidence threshold")
    confidence_score: float = Field(default=0.0, description="Calculated biometric match confidence percentage (0-100%)")
    euclidean_distance: float = Field(default=1.0, description="Euclidean distance between 128-D embeddings (lower = more similar)")
    cosine_similarity: float = Field(default=0.0, description="Cosine similarity between normalized embeddings (-1.0 to 1.0)")
    threshold_distance: float = Field(default=0.60, description="Maximum distance threshold used for match decision")
    threshold_confidence: float = Field(default=70.0, description="Minimum percentage confidence required for match decision")
    verdict: str = Field(default="NO_MATCH", description="MATCH, NO_MATCH, INCONCLUSIVE, or ERROR")
    notes: Optional[str] = None

class UrlMetadata(BaseModel):
    input_url: str = Field(..., description="Original user-submitted URL")
    resolved_url: str = Field(..., description="Final resolved URL after redirects")
    content_type: str = Field(default="unknown", description="MIME content type of fetched resource")
    http_status: int = Field(default=200, description="HTTP response status code")
    platform_detected: str = Field(default="Generic Web", description="Detected social media platform (X, Instagram, LinkedIn, GitHub, etc.)")
    fetch_timestamp: str = Field(..., description="ISO 8601 UTC timestamp of fetch")
    image_size_bytes: int = Field(default=0, description="Byte size of fetched image")
    is_direct_image: bool = Field(default=False, description="Whether URL directly linked to image vs HTML OpenGraph")
    error: Optional[str] = None

class CryptographicProof(BaseModel):
    selfie_sha256: str = Field(..., description="SHA-256 hash of user's uploaded selfie bytes")
    profile_sha256: str = Field(..., description="SHA-256 hash of fetched profile image bytes")
    metadata_sha256: str = Field(..., description="SHA-256 hash of canonical JSON verification metadata")
    record_hash: str = Field(..., description="Combined bytes32 record hash = SHA256(selfie_hash + profile_hash + metadata_hash)")
    algorithm: str = Field(default="SHA-256 (RFC 8785 Canonical Merkle Root)", description="Cryptographic hashing standard")
    canonical_metadata_json: str = Field(..., description="Deterministic RFC-compliant JSON string stored in on-chain proof")

class BlockchainNotarization(BaseModel):
    status: str = Field(default="PENDING", description="NOTARIZED, SKIPPED_NO_MATCH, MOCK_NOTARIZED, or FAILED")
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    contract_address: Optional[str] = None
    explorer_url: Optional[str] = None
    submitter_address: Optional[str] = None
    network: str = Field(default="Polygon Amoy Testnet")
    chain_id: int = Field(default=80002)
    timestamp: Optional[str] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None

class VerificationResponse(BaseModel):
    success: bool = Field(default=False)
    verification_id: str = Field(..., description="Unique UUID for this verification session")
    selfie_face: FaceDetail
    profile_face: FaceDetail
    comparison: FaceComparisonResult
    url_metadata: UrlMetadata
    cryptographic_proof: CryptographicProof
    blockchain: BlockchainNotarization
    message: str
    timestamp: str
    execution_time_ms: float

class ReverifyRequest(BaseModel):
    record_hash: Optional[str] = Field(default=None, description="0x-prefixed 32-byte record hash")
    transaction_hash: Optional[str] = Field(default=None, description="Blockchain transaction hash")
    metadata_json: Optional[str] = Field(default=None, description="Optional metadata JSON to test tamper detection")

class ReverifyResponse(BaseModel):
    verified: bool = Field(..., description="True if on-chain record exists and matches without tampering")
    record_hash: str
    on_chain_exists: bool
    submitter: Optional[str] = None
    blockchain_timestamp: Optional[int] = None
    blockchain_timestamp_iso: Optional[str] = None
    on_chain_metadata: Optional[str] = None
    tamper_detected: bool = Field(default=False)
    tamper_details: Optional[str] = None
    explorer_url: Optional[str] = None
    network: str = "Polygon Amoy Testnet"

class AuditRecord(BaseModel):
    id: int
    verification_id: str
    record_hash: str
    transaction_hash: Optional[str] = None
    input_url: str
    platform: str
    confidence_score: float
    is_match: bool
    notarized: bool
    submitter: Optional[str] = None
    timestamp: str

class SystemHealth(BaseModel):
    status: str = "healthy"
    app_name: str
    version: str
    rpc_connected: bool
    chain_id: int
    chain_name: str
    contract_configured: bool
    contract_address: str
    wallet_address: Optional[str] = None
    wallet_balance_eth: Optional[float] = None
    explorer_url: str
    active_face_detector: str
