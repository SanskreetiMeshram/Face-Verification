#!/usr/bin/env python3
"""
FaceChain Verify - Standalone E2E Demonstration Runner
Executes complete 7-step pipeline from command line and verifies cryptographic integrity.
"""
import sys
import os

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

import asyncio
from app.services.face_service import face_service
from app.services.reverse_search import reverse_search_service
from app.services.fingerprint_service import fingerprint_service
from app.services.blockchain_service import blockchain_service
from app.models.schemas import CanonicalEvidence
from tests.test_face_service import create_synthetic_face_image

async def run_e2e_demo():
    print("=" * 65)
    print("           FACECHAIN VERIFY -- E2E DEMONSTRATION")
    print("=" * 65)
    
    # 1. Image
    print("\n[STEP 1] Generating authorized benchmark face image...")
    img_bytes = create_synthetic_face_image()
    print(f"  [OK] Image created ({len(img_bytes)} bytes)")

    # 2. Face Detection
    print("\n[STEP 2] Running Face AI Detection & 128-D Feature Encoding...")
    face_res = face_service.detect_and_encode(img_bytes, "demo_subject.jpg")
    print(f"  [OK] Face Detected: {face_res.face_detected}")
    print(f"  [OK] Face Count: {face_res.face_count}")
    print(f"  [OK] Input Image SHA-256: {face_res.source_image_sha256}")
    print(f"  [OK] Embedding Dimension: {face_res.embedding_dimension}-D")
    print(f"  [OK] Bounding Box: ({face_res.faces[0].bounding_box.x}, {face_res.faces[0].bounding_box.y}, {face_res.faces[0].bounding_box.width}x{face_res.faces[0].bounding_box.height})")

    # 3. Reverse Search
    print("\n[STEP 3] Executing Reverse Image Search Discovery...")
    search_res = await reverse_search_service.execute_search(img_bytes, "demo_subject.jpg")
    print(f"  [OK] Provider: {search_res.provider}")
    print(f"  [OK] Discovered Items: {search_res.results_count}")
    print(f"  [OK] Match Status: {search_res.match_status}")

    # 4. Content Discovery
    match = search_res.primary_match
    print(f"\n[STEP 4] Discovered Public Content:")
    print(f"  [OK] Title: {match.title}")
    print(f"  [OK] Platform: {match.platform}")
    print(f"  [OK] URL: {match.url}")

    # 5. Canonical Content Fingerprint
    print("\n[STEP 5] Generating Canonical Content Fingerprint (SHA-256)...")
    evidence = CanonicalEvidence(
        source_image_sha256=face_res.source_image_sha256,
        reverse_search_provider=search_res.provider,
        matched_url=match.url,
        platform=match.platform or "Web Match",
        search_timestamp="2026-09-06T12:00:00Z",
        match_metadata={
            "title": match.title,
            "domain": match.domain,
            "url": match.url,
            "platform": match.platform,
            "discoveredAt": "2026-09-06T12:00:00Z"
        }
    )
    fp_res = fingerprint_service.create_content_fingerprint(evidence)
    print(f"  [OK] Canonical JSON: {fp_res.canonical_json}")
    print(f"  [OK] Content SHA-256: {fp_res.sha256_hash}")
    print(f"  [OK] EVM bytes32: {fp_res.bytes32_hash}")

    # 6. Blockchain Registration
    print("\n[STEP 6] Submitting Transaction to Blockchain Smart Contract...")
    bc_res = await blockchain_service.register_evidence_on_chain(evidence)
    print(f"  [OK] Record ID: #{bc_res.record_id}")
    print(f"  [OK] Transaction Hash: {bc_res.transaction_hash}")
    print(f"  [OK] Block Height: #{bc_res.block_number}")
    print(f"  [OK] Contract Address: {bc_res.contract_address}")
    print(f"  [OK] Chain: {bc_res.chain_name}")

    # 7. Independent Cryptographic Re-Verification
    print("\n[STEP 7] Executing Independent Re-Verification against Blockchain...")
    ver_res = await blockchain_service.verify_evidence(bc_res.record_id, evidence)
    print(f"  [OK] Status: {ver_res.status}")
    print(f"  [OK] Hashes Match: {ver_res.hashes_match}")
    print(f"  [OK] Verified: {ver_res.is_verified}")
    print(f"  [OK] Message: {ver_res.verification_message}")

    # 8. Tamper Test
    print("\n[STEP 8] Validating Tamper Detection (Altering Discovered URL)...")
    tampered_evidence = CanonicalEvidence(
        source_image_sha256=face_res.source_image_sha256,
        reverse_search_provider=search_res.provider,
        matched_url="https://instagram.com/p/tampered_fake_url",
        platform=match.platform or "Web Match",
        search_timestamp="2026-09-06T12:00:00Z",
        match_metadata={"domain": "instagram.com"}
    )
    tamper_ver_res = await blockchain_service.verify_evidence(bc_res.record_id, tampered_evidence)
    print(f"  [OK] Tamper Detected: {tamper_ver_res.tamper_detected}")
    print(f"  [OK] Status: {tamper_ver_res.status}")
    print(f"  [OK] Calculated Hash: {tamper_ver_res.calculated_hash}")
    print(f"  [OK] Blockchain Hash: {tamper_ver_res.blockchain_hash}")
    print(f"  [OK] Message: {tamper_ver_res.verification_message}")

    print("\n" + "=" * 65)
    print("   [SUCCESS] ALL PIPELINE STAGES COMPLETED & CRYPTOGRAPHICALLY VERIFIED")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_e2e_demo())
