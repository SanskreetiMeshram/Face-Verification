import os
import time
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.schemas import (
    VerificationResponse,
    FaceDetail,
    FaceComparisonResult,
    UrlMetadata,
    CryptographicProof,
    BlockchainNotarization,
    ReverifyRequest,
    ReverifyResponse,
    AuditRecord,
    SystemHealth
)
from app.services.face_service import face_service
from app.services.url_service import url_service
from app.services.hashing_service import hashing_service
from app.services.blockchain_service import blockchain_service
from app.database import (
    save_record,
    get_records,
    get_record_by_hash,
    log_reverification
)

logger = logging.getLogger("prooflink.routes")
router = APIRouter()

# Curated sample pairs for quick testing in UI
SAMPLE_PRESETS = [
    {
        "id": "sample-alex",
        "name": "Alex Mercer (Verified Identity)",
        "selfie_name": "sample_selfie_1.jpg",
        "profile_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
        "description": "High-confidence self-identity match with public photographic portrait."
    },
    {
        "id": "sample-elena",
        "name": "Elena Rostova (Creative Profile)",
        "selfie_name": "sample_selfie_2.jpg",
        "profile_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=600&q=80",
        "description": "Public Instagram/Unsplash profile image self-verification."
    },
    {
        "id": "sample-marcus",
        "name": "Marcus Vance (Developer Profile)",
        "selfie_name": "sample_selfie_3.jpg",
        "profile_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=600&q=80",
        "description": "Public GitHub / LinkedIn developer avatar match."
    }
]

@router.get("/health", response_model=SystemHealth)
async def get_health():
    """Check API, AI model, and blockchain network connectivity."""
    chain_info = blockchain_service.get_system_status()
    return SystemHealth(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        rpc_connected=chain_info["rpc_connected"],
        chain_id=chain_info["chain_id"],
        chain_name=chain_info["chain_name"],
        contract_configured=chain_info["contract_configured"],
        contract_address=chain_info["contract_address"],
        wallet_address=chain_info["wallet_address"],
        wallet_balance_eth=chain_info["wallet_balance_eth"],
        explorer_url=chain_info["explorer_url"],
        active_face_detector=face_service.detector_name
    )

@router.get("/samples")
async def get_samples():
    """Retrieve pre-configured sample URLs for 1-click testing."""
    return {"samples": SAMPLE_PRESETS}

@router.post("/verify", response_model=VerificationResponse)
async def verify_identity(
    selfie: UploadFile = File(..., description="User's live selfie image file (JPG, PNG, WEBP)"),
    profile_url: str = Form(..., description="Public social media post or profile picture URL")
):
    """
    End-to-End Self-Identity Verification Pipeline:
    1. Validates selfie format & size.
    2. Safely fetches user's profile image from the specified URL.
    3. Detects face in selfie and extracts 128-D embedding.
    4. Detects face in profile image and extracts 128-D embedding.
    5. Measures Euclidean distance, Cosine similarity, and confidence score.
    6. Computes deterministic SHA-256 Merkle hashes.
    7. If match passes threshold, notarizes the cryptographic record hash on Polygon Amoy.
    """
    start_time = time.time()
    verification_id = f"pl_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_url = profile_url.strip()

    # 1. Validate Selfie File
    if not selfie.filename:
        raise HTTPException(status_code=400, detail="Selfie file is required.")

    ext = selfie.filename.split(".")[-1].lower() if "." in selfie.filename else ""
    if ext not in settings.allowed_extensions_set:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )

    try:
        selfie_bytes = await selfie.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read selfie file: {str(e)}")

    if len(selfie_bytes) == 0:
        raise HTTPException(status_code=400, detail="Selfie file is empty.")

    if len(selfie_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Selfie file size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 2. Fetch Profile Image from URL
    profile_bytes, url_meta, url_error = await url_service.fetch_profile_image(clean_url)

    if url_error or not profile_bytes:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        return VerificationResponse(
            success=False,
            verification_id=verification_id,
            selfie_face=FaceDetail(detected=False, face_count=0),
            profile_face=FaceDetail(detected=False, face_count=0, error=url_error),
            comparison=FaceComparisonResult(is_match=False, verdict="ERROR", notes=url_error),
            url_metadata=url_meta,
            cryptographic_proof=CryptographicProof(
                selfie_sha256=hashing_service.hash_bytes(selfie_bytes),
                profile_sha256="",
                metadata_sha256="",
                record_hash="",
                canonical_metadata_json=""
            ),
            blockchain=BlockchainNotarization(status="SKIPPED", error=url_error),
            message=f"Failed to retrieve profile image from provided URL: {url_error}",
            timestamp=now_iso,
            execution_time_ms=exec_ms
        )

    # 3. Process Selfie Face
    selfie_detail, selfie_emb, selfie_err = face_service.process_face_image(selfie_bytes, "selfie photo")

    # 4. Process Profile Face
    profile_detail, profile_emb, profile_err = face_service.process_face_image(profile_bytes, "profile URL image")

    # If either image fails face detection / single-face policy
    if selfie_err or profile_err or selfie_emb is None or profile_emb is None:
        exec_ms = round((time.time() - start_time) * 1000, 2)
        fail_msg = selfie_err or profile_err or "Face detection failed."
        return VerificationResponse(
            success=False,
            verification_id=verification_id,
            selfie_face=selfie_detail,
            profile_face=profile_detail,
            comparison=FaceComparisonResult(
                is_match=False,
                verdict="NO_MATCH",
                notes=fail_msg
            ),
            url_metadata=url_meta,
            cryptographic_proof=CryptographicProof(
                selfie_sha256=hashing_service.hash_bytes(selfie_bytes),
                profile_sha256=hashing_service.hash_bytes(profile_bytes),
                metadata_sha256="",
                record_hash="",
                canonical_metadata_json=""
            ),
            blockchain=BlockchainNotarization(status="SKIPPED", error=fail_msg),
            message=fail_msg,
            timestamp=now_iso,
            execution_time_ms=exec_ms
        )

    # 5. Biometric Face Comparison
    comparison = face_service.compare_embeddings(selfie_emb, profile_emb)

    # 6. Generate Cryptographic Proof
    meta_dict = {
        "algorithm": settings.FACE_DETECTION_MODEL,
        "confidence_score": comparison.confidence_score,
        "euclidean_distance": comparison.euclidean_distance,
        "fetch_timestamp": url_meta.fetch_timestamp,
        "is_match": comparison.is_match,
        "platform": url_meta.platform_detected,
        "profile_url": url_meta.resolved_url,
        "threshold_confidence": comparison.threshold_confidence,
        "threshold_distance": comparison.threshold_distance,
        "verification_id": verification_id,
        "version": "1.0.0"
    }

    crypto_proof = hashing_service.generate_cryptographic_proof(
        selfie_bytes=selfie_bytes,
        profile_bytes=profile_bytes,
        metadata_dict=meta_dict
    )

    # 7. Blockchain Notarization (Only if match passes threshold)
    if comparison.is_match:
        blockchain_proof = blockchain_service.notarize_record(
            record_hash=crypto_proof.record_hash,
            canonical_metadata=crypto_proof.canonical_metadata_json
        )
    else:
        blockchain_proof = BlockchainNotarization(
            status="SKIPPED_NO_MATCH",
            error="Biometric confidence did not meet required threshold for on-chain notarization.",
            network=settings.CHAIN_NAME,
            chain_id=settings.CHAIN_ID
        )

    exec_ms = round((time.time() - start_time) * 1000, 2)

    # 8. Persist Audit Record (hashes + metadata only)
    save_record({
        "verification_id": verification_id,
        "record_hash": crypto_proof.record_hash,
        "selfie_sha256": crypto_proof.selfie_sha256,
        "profile_sha256": crypto_proof.profile_sha256,
        "metadata_sha256": crypto_proof.metadata_sha256,
        "input_url": clean_url,
        "resolved_url": url_meta.resolved_url,
        "platform": url_meta.platform_detected,
        "confidence_score": comparison.confidence_score,
        "euclidean_distance": comparison.euclidean_distance,
        "cosine_similarity": comparison.cosine_similarity,
        "is_match": comparison.is_match,
        "notarized": bool(blockchain_proof.status in ("NOTARIZED", "MOCK_NOTARIZED")),
        "transaction_hash": blockchain_proof.transaction_hash,
        "block_number": blockchain_proof.block_number,
        "submitter": blockchain_proof.submitter_address,
        "canonical_metadata": crypto_proof.canonical_metadata_json,
        "explorer_url": blockchain_proof.explorer_url,
        "timestamp": now_iso
    })

    msg = (
        f"Verification completed successfully! Match confidence: {comparison.confidence_score:.1f}%."
        if comparison.is_match
        else f"Face comparison completed: No match found (confidence {comparison.confidence_score:.1f}% below {comparison.threshold_confidence:.0f}% threshold)."
    )

    return VerificationResponse(
        success=True,
        verification_id=verification_id,
        selfie_face=selfie_detail,
        profile_face=profile_detail,
        comparison=comparison,
        url_metadata=url_meta,
        cryptographic_proof=crypto_proof,
        blockchain=blockchain_proof,
        message=msg,
        timestamp=now_iso,
        execution_time_ms=exec_ms
    )

@router.post("/reverify", response_model=ReverifyResponse)
async def reverify_record(req: ReverifyRequest):
    """
    Independent Re-Verification Engine:
    Given a record hash or transaction hash:
    - Queries on-chain smart contract verify() function.
    - Confirms existence, submitter, and timestamp.
    - If metadata is provided, tests for cryptographic tamper detection.
    """
    target_hash = req.record_hash or req.transaction_hash
    if not target_hash:
        raise HTTPException(status_code=400, detail="Either record_hash or transaction_hash must be provided.")

    # Check database for existing record
    db_rec = get_record_by_hash(target_hash)
    record_hash_to_query = db_rec["record_hash"] if db_rec else target_hash

    # Query on-chain smart contract
    exists, submitter, timestamp_int, onchain_metadata = blockchain_service.verify_record(record_hash_to_query)

    ts_iso = datetime.fromtimestamp(timestamp_int, tz=timezone.utc).isoformat() if timestamp_int else None

    # Check for tampering if test metadata provided
    tamper_detected = False
    tamper_details = None

    if req.metadata_json and db_rec:
        # Recompute hash with altered metadata
        recomputed_meta_hash = hashing_service.hash_string(req.metadata_json)
        recomputed_record_hash = hashing_service.compute_record_hash(
            db_rec["selfie_sha256"],
            db_rec["profile_sha256"],
            recomputed_meta_hash
        )
        if recomputed_record_hash.lower() != record_hash_to_query.lower():
            tamper_detected = True
            tamper_details = (
                f"Tampering detected! Recomputed hash '{recomputed_record_hash[:18]}...' "
                f"does not match on-chain record hash '{record_hash_to_query[:18]}...'."
            )

    explorer_url = blockchain_service.get_explorer_tx_url(db_rec["transaction_hash"]) if db_rec and db_rec.get("transaction_hash") else None

    log_reverification(
        record_hash=record_hash_to_query,
        on_chain_exists=exists,
        tamper_detected=tamper_detected,
        submitter=submitter
    )

    return ReverifyResponse(
        verified=bool(exists and not tamper_detected),
        record_hash=record_hash_to_query,
        on_chain_exists=exists,
        submitter=submitter,
        blockchain_timestamp=timestamp_int,
        blockchain_timestamp_iso=ts_iso,
        on_chain_metadata=onchain_metadata or (db_rec["canonical_metadata"] if db_rec else None),
        tamper_detected=tamper_detected,
        tamper_details=tamper_details,
        explorer_url=explorer_url,
        network=settings.CHAIN_NAME
    )

@router.get("/blockchain/verify/{record_hash}")
async def get_blockchain_verify(record_hash: str):
    """Direct on-chain read query to ProofRegistry.verify(recordHash)."""
    exists, submitter, timestamp_int, metadata = blockchain_service.verify_record(record_hash)
    ts_iso = datetime.fromtimestamp(timestamp_int, tz=timezone.utc).isoformat() if timestamp_int else None
    return {
        "record_hash": record_hash,
        "exists": exists,
        "submitter": submitter,
        "timestamp": timestamp_int,
        "timestamp_iso": ts_iso,
        "metadata": metadata
    }

@router.get("/records")
async def list_records(limit: int = Query(default=25, ge=1, le=100)):
    """List recent verification audit records."""
    records = get_records(limit=limit)
    return {"records": records, "count": len(records)}

@router.get("/records/{identifier}")
async def get_record_detail(identifier: str):
    """Retrieve details of a single verification record."""
    rec = get_record_by_hash(identifier)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Record '{identifier}' not found.")
    return {"record": rec}

@router.websocket("/ws/verify")
async def websocket_verify_stream(websocket: WebSocket):
    """
    WebSocket endpoint for live real-time pipeline status updates.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping / keepalive
            await websocket.send_json({"type": "pong", "time": time.time()})
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected.")
    except Exception as e:
        logger.debug(f"WebSocket error: {e}")
