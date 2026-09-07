import pytest
import cv2
import numpy as np
from app.services.face_service import face_service

def create_synthetic_face_image() -> bytes:
    """Create a synthetic image with face-like structures for OpenCV Cascade detection."""
    # 300x300 canvas
    img = np.ones((300, 300, 3), dtype=np.uint8) * 200
    
    # Face oval
    cv2.ellipse(img, (150, 150), (70, 90), 0, 0, 360, (140, 160, 200), -1)
    
    # Eyes
    cv2.circle(img, (120, 130), 12, (50, 50, 50), -1)
    cv2.circle(img, (180, 130), 12, (50, 50, 50), -1)
    
    # Nose
    cv2.line(img, (150, 140), (150, 165), (80, 80, 80), 3)
    
    # Mouth
    cv2.ellipse(img, (150, 190), (30, 15), 0, 0, 180, (40, 40, 180), 4)
    
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def create_blank_image() -> bytes:
    """Create a blank white image with no face."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def test_detect_face_on_synthetic_image():
    """Verify face service execution and embedding fingerprint output."""
    img_bytes = create_synthetic_face_image()
    result = face_service.detect_and_encode(img_bytes, "test_face.jpg")
    
    assert result.source_image_sha256 is not None
    assert len(result.source_image_sha256) == 64
    assert result.image_width == 300
    assert result.image_height == 300

def test_detect_face_on_blank_image():
    """Verify that a blank image correctly reports 0 faces without crashing."""
    img_bytes = create_blank_image()
    result = face_service.detect_and_encode(img_bytes, "blank.jpg")
    
    assert result.face_detected is False
    assert result.face_count == 0
    assert len(result.faces) == 0
    assert "No face detected" in result.message

def test_invalid_image_bytes():
    """Verify that corrupt or invalid image bytes raise ValueError."""
    corrupt_bytes = b"NOT_A_VALID_IMAGE_FILE_DATA_12345"
    with pytest.raises(ValueError, match="Failed to decode image"):
        face_service.detect_and_encode(corrupt_bytes, "corrupt.jpg")

def test_compare_faces_identical():
    """Verify 1-to-1 biometric comparison of identical images returns 100% match."""
    img_bytes = create_synthetic_face_image()
    res = face_service.compare_faces(img_bytes, img_bytes)
    assert res.is_match is True
    assert res.similarity_score >= 0.99
    assert res.match_percentage >= 99.0
    assert res.verdict == "BIOMETRIC_MATCH_CONFIRMED"

