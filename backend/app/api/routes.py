import os
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
import io

from app.config import settings
from app.models.schemas import (
    FaceDetectionResult,
    ReverseSearchResponse,
    CanonicalEvidence,
    EvidenceHashResult,
    FingerprintCreateRequest,
    FingerprintCreateResponse,
    BlockchainRegisterRequest,
    BlockchainRegisterResponse,
    BlockchainRecordData,
    VerifyEvidenceRequest,
    VerificationResult,
    PipelineRunResponse,
    PipelineStepStatus,
    SystemStatusResponse
)
from app.services.face_service import face_service
from app.services.reverse_search import reverse_search_service
from app.services.hashing_service import hashing_service
from app.services.blockchain_service import blockchain_service
from app.database import log_creator_activity, get_activity_stats, get_all_blockchain_records
from app.utils.helpers import (
    validate_image_bytes,
    generate_safe_filename,
    safe_delete_file,
    ensure_temp_dir
)

logger = logging.getLogger("facechain.api")
router = APIRouter()

# -----------------------------------------------------------------------------
# System Status & Health
# -----------------------------------------------------------------------------
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/config/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Return public system status and configuration without revealing secrets."""
    is_demo = (
        not settings.active_search_api_key or 
        settings.active_search_provider == "demo"
    )
    return SystemStatusResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        face_ai_status="Ready" if face_service.face_cascade is not None else "Cascade Active",
        face_detector_model=face_service.detector_name,
        reverse_image_provider=settings.active_search_provider,
        reverse_image_api_configured=bool(settings.active_search_api_key),
        blockchain_network=settings.CHAIN_NAME,
        blockchain_chain_id=settings.CHAIN_ID,
        blockchain_rpc_connected=blockchain_service.is_rpc_connected(),
        smart_contract_configured=blockchain_service.is_contract_configured(),
        smart_contract_address=settings.CONTRACT_ADDRESS if settings.CONTRACT_ADDRESS else "Not Configured",
        is_demo_mode_active=is_demo
    )

# -----------------------------------------------------------------------------
# Modular Step Endpoints
# -----------------------------------------------------------------------------
@router.post("/face/analyze", response_model=FaceDetectionResult)
@router.post("/face/detect", response_model=FaceDetectionResult)
async def detect_face(file: UploadFile = File(...)):
    """Detect faces, compute bounding box, and generate temporary normalized embedding fingerprint."""
    image_bytes = await file.read()
    valid, err = validate_image_bytes(image_bytes, file.filename or "upload.jpg")
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    try:
        result = face_service.detect_and_encode(image_bytes, file.filename or "upload.jpg")
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Face detection failed: {str(e)}")

@router.post("/search/reverse", response_model=ReverseSearchResponse)
@router.post("/reverse-search", response_model=ReverseSearchResponse)
async def reverse_image_search(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None)
):
    """Execute reverse image search across genuine providers and discover public web/social matches."""
    if not file and not image_url:
        raise HTTPException(status_code=400, detail="Either an image file or an image_url must be provided.")

    image_bytes = b""
    filename = "query.jpg"
    if file:
        image_bytes = await file.read()
        filename = file.filename or "query.jpg"

    return await reverse_search_service.execute_search(
        image_bytes=image_bytes,
        filename=filename,
        image_url=image_url
    )

@router.post("/fingerprint/create", response_model=FingerprintCreateResponse)
async def create_content_fingerprint(req: FingerprintCreateRequest):
    """
    Generate deterministic canonical representation and SHA-256 cryptographic fingerprint
    from discovered public content metadata.
    """
    now_iso = req.discovered_at or datetime.now(timezone.utc).isoformat()
    evidence = CanonicalEvidence(
        source_image_sha256=req.source_image_sha256 or "0"*64,
        reverse_search_provider=req.search_provider or settings.active_search_provider,
        matched_url=req.url,
        platform=req.platform,
        search_timestamp=now_iso,
        match_metadata={
            "title": req.title,
            "domain": req.domain,
            "url": req.url,
            "platform": req.platform,
            "discoveredAt": now_iso
        }
    )
    hash_res = hashing_service.hash_evidence(evidence)
    return FingerprintCreateResponse(
        canonical_json=hash_res.canonical_json,
        sha256_hash=hash_res.sha256_hash,
        bytes32_hash=hash_res.bytes32_hash,
        evidence=evidence
    )

@router.post("/blockchain/register", response_model=BlockchainRegisterResponse)
async def register_evidence_on_chain(req: BlockchainRegisterRequest):
    """Register content fingerprint on Ethereum-compatible blockchain."""
    try:
        return await blockchain_service.register_evidence_on_chain(req.evidence)
    except Exception as e:
        logger.error(f"Blockchain registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/blockchain/record/{record_id}", response_model=BlockchainRecordData)
async def get_blockchain_record(record_id: int):
    """Retrieve an immutable record from the blockchain registry."""
    record = await blockchain_service.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record #{record_id} not found on-chain.")
    return record

@router.post("/blockchain/verify", response_model=VerificationResult)
async def verify_evidence(req: VerifyEvidenceRequest):
    """Recalculate evidence hash and verify directly against the blockchain record."""
    return await blockchain_service.verify_evidence(req.record_id, req.evidence)

@router.get("/blockchain/history")
async def get_verification_history():
    """Retrieve history of registered evidence records."""
    return {"history": blockchain_service.get_history()}

# -----------------------------------------------------------------------------
# Primary Full End-to-End Pipeline
# -----------------------------------------------------------------------------
@router.post("/pipeline/run", response_model=PipelineRunResponse)
async def run_verification_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Execute complete end-to-end pipeline:
    1. Upload validation
    2. Face AI detection & encoding
    3. Genuine reverse image search
    4. Matching public content discovery
    5. Canonical content fingerprinting (SHA-256)
    6. Blockchain registration (ContentFingerprintRegistry)
    7. Independent cryptographic re-verification
    """
    pipeline_id = uuid.uuid4().hex[:10]
    steps: List[PipelineStepStatus] = []
    
    def log_step(num: int, name: str, status: str, msg: str):
        ts = datetime.now(timezone.utc).isoformat()
        steps.append(PipelineStepStatus(step_number=num, name=name, status=status, message=msg, timestamp=ts))
        logger.info(f"[PIPELINE #{pipeline_id}] Step {num} ({name}): {status} - {msg}")

    # Step 1: Image Upload & Validation
    image_bytes = await file.read()
    filename = file.filename or "upload.jpg"
    valid, err_msg = validate_image_bytes(image_bytes, filename)
    if not valid:
        log_step(1, "IMAGE UPLOAD", "failed", err_msg or "Invalid image file")
        return PipelineRunResponse(
            success=False,
            pipeline_id=pipeline_id,
            steps=steps,
            error_details=err_msg
        )
    log_step(1, "IMAGE UPLOAD", "success", f"Authorized image received ({len(image_bytes)//1024} KB). SHA-256 fingerprint generated.")

    # Step 2: Face Detection & Encoding
    face_result: Optional[FaceDetectionResult] = None
    try:
        face_result = face_service.detect_and_encode(image_bytes, filename)
        if not face_result.face_detected:
            log_step(2, "FACE AI", "failed", face_result.message)
            return PipelineRunResponse(
                success=False,
                pipeline_id=pipeline_id,
                steps=steps,
                face_analysis=face_result,
                error_details="No face detected. Process halted."
            )
        log_step(2, "FACE AI", "success", f"Detected {face_result.face_count} face(s). Generated 128-D normalized embedding vector.")
    except Exception as e:
        log_step(2, "FACE AI", "failed", f"Face analysis error: {str(e)}")
        return PipelineRunResponse(
            success=False,
            pipeline_id=pipeline_id,
            steps=steps,
            error_details=str(e)
        )

    # Step 3: Reverse Image Search
    search_res: Optional[ReverseSearchResponse] = None
    try:
        search_res = await reverse_search_service.execute_search(image_bytes=image_bytes, filename=filename)
        if not search_res.success:
            log_step(3, "REVERSE SEARCH", "failed", f"Search provider error: {search_res.error_message}")
            return PipelineRunResponse(
                success=False,
                pipeline_id=pipeline_id,
                steps=steps,
                face_analysis=face_result,
                reverse_search=search_res,
                error_details=search_res.error_message
            )
        log_step(3, "REVERSE SEARCH", "success", f"Completed reverse search via {search_res.provider}. Discovered {search_res.results_count} public item(s).")
    except Exception as e:
        log_step(3, "REVERSE SEARCH", "failed", f"Reverse search execution failed: {str(e)}")
        return PipelineRunResponse(
            success=False,
            pipeline_id=pipeline_id,
            steps=steps,
            face_analysis=face_result,
            error_details=str(e)
        )

    # Step 4: Discovered Web / Social Match
    if not search_res.primary_match:
        log_step(4, "MATCH DISCOVERY", "failed", "No matching public web content returned by provider.")
        return PipelineRunResponse(
            success=False,
            pipeline_id=pipeline_id,
            steps=steps,
            face_analysis=face_result,
            reverse_search=search_res,
            error_details="No matching public content found to fingerprint."
        )

    matched_item = search_res.primary_match
    matched_platform = matched_item.platform or "Public Web Match"
    matched_url = matched_item.url
    log_step(4, "MATCH DISCOVERY", "success", f"Discovered public content on {matched_platform} ({matched_item.domain})")

    # Step 5: Discovered Content Canonicalization & Fingerprinting
    now_iso = datetime.now(timezone.utc).isoformat()
    evidence = CanonicalEvidence(
        source_image_sha256=face_result.source_image_sha256,
        reverse_search_provider=search_res.provider,
        matched_url=matched_url,
        platform=matched_platform,
        search_timestamp=now_iso,
        match_metadata={
            "title": matched_item.title,
            "domain": matched_item.domain,
            "url": matched_url,
            "platform": matched_platform,
            "discoveredAt": now_iso,
            "similarity": matched_item.similarity,
            "face_count": face_result.face_count,
            "embedding_fingerprint": face_result.faces[0].embedding_fingerprint if face_result.faces else None
        }
    )

    evidence_hash_res = hashing_service.hash_evidence(evidence)
    log_step(5, "CONTENT FINGERPRINT", "success", f"Canonical JSON serialized. Content SHA-256 fingerprint: {evidence_hash_res.bytes32_hash[:10]}...{evidence_hash_res.bytes32_hash[-6:]}")

    # Step 6: Blockchain Registration
    blockchain_reg: Optional[BlockchainRegisterResponse] = None
    try:
        blockchain_reg = await blockchain_service.register_evidence_on_chain(evidence)
        if not blockchain_reg.success:
            log_step(6, "BLOCKCHAIN", "failed", "Smart contract transaction failed to confirm.")
            return PipelineRunResponse(
                success=False,
                pipeline_id=pipeline_id,
                steps=steps,
                face_analysis=face_result,
                reverse_search=search_res,
                evidence_hash=evidence_hash_res,
                blockchain_record=blockchain_reg,
                error_details="Blockchain transaction reverted or failed."
            )
        mode_note = " (Verifiable Local Registry)" if blockchain_reg.is_simulated else ""
        log_step(6, "BLOCKCHAIN", "success", f"Record #{blockchain_reg.record_id} registered on {blockchain_reg.chain_name}{mode_note}. Tx: {blockchain_reg.transaction_hash[:10]}...")
    except Exception as e:
        log_step(6, "BLOCKCHAIN", "failed", f"Blockchain registration failed: {str(e)}")
        return PipelineRunResponse(
            success=False,
            pipeline_id=pipeline_id,
            steps=steps,
            face_analysis=face_result,
            reverse_search=search_res,
            evidence_hash=evidence_hash_res,
            error_details=str(e)
        )

    # Step 7: Independent Cryptographic Re-Verification
    verification_res: Optional[VerificationResult] = None
    try:
        verification_res = await blockchain_service.verify_evidence(blockchain_reg.record_id, evidence)
        if verification_res.is_verified:
            log_step(7, "VERIFICATION", "success", "✓ VERIFIED: Recomputed content fingerprint exactly matches immutable on-chain record.")
        else:
            log_step(7, "VERIFICATION", "failed", "✕ MISMATCH: Recomputed fingerprint does not match on-chain record.")
    except Exception as e:
        log_step(7, "VERIFICATION", "failed", f"Verification query failed: {str(e)}")

    try:
        log_creator_activity(
            event_type="PIPELINE_RUN",
            status="SUCCESS",
            source_image_sha256=face_result.source_image_sha256 if face_result else None,
            face_count=face_result.face_count if face_result else 0,
            platform=matched_platform,
            matched_url=matched_url,
            evidence_hash=evidence_hash_res.bytes32_hash if evidence_hash_res else None,
            blockchain_tx=blockchain_reg.transaction_hash if blockchain_reg else None,
            record_id=blockchain_reg.record_id if blockchain_reg else None,
            message=f"Pipeline verified on-chain for {matched_platform}",
            details={
                "pipeline_id": pipeline_id,
                "confidence": face_result.primary_confidence if face_result else 0.0,
                "is_demo_mode": search_res.is_demo_mode if search_res else False
            }
        )
    except Exception as ex:
        logger.warning(f"Could not log master activity: {ex}")

    return PipelineRunResponse(
        success=True,
        pipeline_id=pipeline_id,
        steps=steps,
        face_analysis=face_result,
        reverse_search=search_res,
        evidence_hash=evidence_hash_res,
        blockchain_record=blockchain_reg,
        verification=verification_res,
        is_demo_mode=search_res.is_demo_mode or (blockchain_reg.is_simulated if blockchain_reg else False)
    )

# -----------------------------------------------------------------------------
# Creator / Admin Activity Audit Logs & Export
# -----------------------------------------------------------------------------
@router.get("/admin/activity")
async def get_admin_activity():
    """Retrieve full creator activity stats, real-time uploads, and device metrics."""
    return get_activity_stats()

@router.get("/admin/export")
async def export_audit_log(format: str = "json"):
    """Export complete persistent history as downloadable JSON or CSV format."""
    records = get_all_blockchain_records()
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "csv":
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Record ID", "Evidence Hash", "Platform", "Result URL", "Timestamp", "Submitter", "Transaction Hash", "Chain Name"])
        for r in records:
            writer.writerow([
                r.get("record_id"),
                r.get("evidence_hash"),
                r.get("platform"),
                r.get("result_url"),
                r.get("timestamp_iso"),
                r.get("submitter"),
                r.get("transaction_hash"),
                r.get("chain_name")
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=facechain_audit_{now_str}.csv"}
        )
    else:
        content = json.dumps(records, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=facechain_audit_{now_str}.json"}
        )

@router.post("/activity/log")
async def log_client_event(payload: Dict[str, Any], request: Request):
    """Log client-side user events."""
    try:
        client_ip = request.client.host if request.client else "Unknown"
        ua = request.headers.get("user-agent", "Unknown")
        log_creator_activity(
            event_type=payload.get("event_type", "CLIENT_ACTION"),
            status=payload.get("status", "INFO"),
            client_ip=client_ip,
            user_agent=ua,
            message=payload.get("message", "Client event recorded"),
            details=payload.get("details")
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -----------------------------------------------------------------------------
# Temporary File Serving
# -----------------------------------------------------------------------------
@router.get("/temp/{filename}")
async def get_temp_file(filename: str):
    """Serve temporary preview image files (e.g. annotated face bounding boxes)."""
    clean_name = os.path.basename(filename)
    filepath = os.path.join(ensure_temp_dir(), clean_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found or expired.")
    return FileResponse(filepath)
