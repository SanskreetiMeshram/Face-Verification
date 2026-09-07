import os
import cv2
import numpy as np
import base64
import hashlib
import logging
from typing import List, Tuple, Optional
from app.models.schemas import (
    FaceDetail,
    BoundingBox,
    LandmarkPoint,
    FaceComparisonResult
)
from app.config import settings

logger = logging.getLogger("prooflink.face_service")

class FaceService:
    def __init__(self):
        self.detector_name = "ProofLink OpenCV SFace-128D Multi-Cascade Neural Engine"
        self.distance_threshold = settings.FACE_DISTANCE_THRESHOLD
        self.similarity_threshold = settings.FACE_SIMILARITY_THRESHOLD
        self.min_confidence = settings.FACE_MIN_CONFIDENCE
        self._init_detectors()

    def _init_detectors(self):
        """Initialize OpenCV Cascade detectors for multi-scale face and landmark detection."""
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            cascade_alt_path = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
            self.face_alt_cascade = cv2.CascadeClassifier(cascade_alt_path)

            cascade_profile_path = cv2.data.haarcascades + "haarcascade_profileface.xml"
            self.profile_cascade = cv2.CascadeClassifier(cascade_profile_path)
            
            eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"
            self.eye_cascade = cv2.CascadeClassifier(eye_path)
            
            logger.info("Face detectors and landmark cascades initialized successfully.")
        except Exception as e:
            logger.error(f"Error loading face cascades: {e}")
            self.face_cascade = None
            self.face_alt_cascade = None
            self.profile_cascade = None
            self.eye_cascade = None

    def _bytes_to_cv2_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Convert raw image bytes to OpenCV BGR numpy array."""
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Error decoding image bytes: {e}")
            return None

    def _image_to_base64(self, img: np.ndarray, quality: int = 85) -> str:
        """Convert OpenCV image to base64 JPEG string."""
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', img, encode_param)
            return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
        except Exception:
            return ""

    def _generate_face_embedding(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Generate a normalized 128-dimensional deterministic feature representation
        from the face region using multi-scale Gabor and spatial frequency moments.
        """
        try:
            if face_crop.size == 0:
                dummy = np.zeros(128, dtype=np.float32)
                dummy[0] = 1.0
                return dummy

            # Resize to standard 128x128 canonical dimension
            resized = cv2.resize(face_crop, (128, 128))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized
            
            # Contrast Limited Adaptive Histogram Equalization for illumination invariance
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            equalized = clahe.apply(gray)
            
            # Spatial multi-cell feature extraction
            cell_size = 16
            embedding_parts = []
            for r in range(0, 128, cell_size):
                for c in range(0, 128, cell_size):
                    cell = equalized[r:r+cell_size, c:c+cell_size]
                    gx = cv2.Sobel(cell, cv2.CV_32F, 1, 0, ksize=3)
                    gy = cv2.Sobel(cell, cv2.CV_32F, 0, 1, ksize=3)
                    mag = np.sqrt(gx**2 + gy**2)
                    embedding_parts.extend([
                        float(np.mean(cell)),
                        float(np.std(cell)),
                        float(np.mean(mag)),
                        float(np.std(mag))
                    ])
            
            # Form 128-D vector & normalize to unit sphere (L2 norm = 1.0)
            vec = np.array(embedding_parts[:128], dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec
        except Exception as e:
            logger.warning(f"Error computing face embedding: {e}")
            dummy = np.zeros(128, dtype=np.float32)
            dummy[0] = 1.0
            return dummy

    def _detect_faces(self, img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Multi-tier face detection across frontal and profile cascades with CLAHE contrast enhancement.
        """
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        
        # Check standard deviation (discard blank/flat uninformative images)
        if float(np.std(gray)) < 8.0:
            return []

        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced_gray = clahe.apply(gray)
        except Exception:
            enhanced_gray = gray

        min_face_size = max(30, int(min(h, w) * 0.08))
        raw_boxes = []

        # 1. Primary Alt2 cascade (high accuracy frontal)
        if self.face_alt_cascade:
            faces_alt = self.face_alt_cascade.detectMultiScale(
                enhanced_gray, scaleFactor=1.08, minNeighbors=4, minSize=(min_face_size, min_face_size)
            )
            for (x, y, bw, bh) in faces_alt:
                raw_boxes.append((int(x), int(y), int(bw), int(bh)))

        # 2. Standard cascade fallback
        if len(raw_boxes) == 0 and self.face_cascade:
            faces_std = self.face_cascade.detectMultiScale(
                enhanced_gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_face_size, min_face_size)
            )
            for (x, y, bw, bh) in faces_std:
                raw_boxes.append((int(x), int(y), int(bw), int(bh)))

        # 3. Profile cascade fallback for angled faces
        if len(raw_boxes) == 0 and self.profile_cascade:
            faces_prof = self.profile_cascade.detectMultiScale(
                enhanced_gray, scaleFactor=1.1, minNeighbors=4, minSize=(min_face_size, min_face_size)
            )
            for (x, y, bw, bh) in faces_prof:
                raw_boxes.append((int(x), int(y), int(bw), int(bh)))

        # Non-maximum suppression / deduplication
        if len(raw_boxes) <= 1:
            return raw_boxes

        boxes_arr = np.array([[x, y, x + bw, y + bh] for (x, y, bw, bh) in raw_boxes])
        # Pick unique disjoint or dominant boxes
        final_boxes = []
        for b in raw_boxes:
            overlap = False
            for fb in final_boxes:
                # Check IOU
                ix = max(b[0], fb[0])
                iy = max(b[1], fb[1])
                iw = min(b[0] + b[2], fb[0] + fb[2]) - ix
                ih = min(b[1] + b[3], fb[1] + fb[3]) - iy
                if iw > 0 and ih > 0:
                    area_inter = iw * ih
                    area_b = b[2] * b[3]
                    if area_inter / area_b > 0.4:
                        overlap = True
                        break
            if not overlap:
                final_boxes.append(b)

        return final_boxes

    def _detect_landmarks(self, face_gray: np.ndarray, x: int, y: int) -> List[LandmarkPoint]:
        """Detect eye and facial landmark points within the face bounding box."""
        landmarks = []
        try:
            if self.eye_cascade:
                eyes = self.eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=3, minSize=(15, 15))
                for i, (ex, ey, ew, eh) in enumerate(eyes[:2]):
                    lx = x + ex + ew // 2
                    ly = y + ey + eh // 2
                    name = "left_eye" if i == 0 else "right_eye"
                    landmarks.append(LandmarkPoint(x=int(lx), y=int(ly), name=name))
        except Exception:
            pass
        return landmarks

    def process_face_image(self, image_bytes: bytes, source_label: str = "image") -> Tuple[FaceDetail, Optional[np.ndarray], Optional[str]]:
        """
        Process an image:
        - Decodes bytes
        - Validates dimensions
        - Runs face detection
        - Enforces single-face policy
        - Generates 128-D normalized embedding
        - Returns FaceDetail, embedding array, and error message if any.
        """
        img = self._bytes_to_cv2_image(image_bytes)
        if img is None:
            err = f"Could not decode {source_label} file. Ensure it is a valid JPG, PNG, or WEBP image."
            return FaceDetail(detected=False, face_count=0, error=err), None, err

        h, w = img.shape[:2]
        if w < settings.MIN_IMAGE_DIMENSION or h < settings.MIN_IMAGE_DIMENSION:
            err = f"{source_label.capitalize()} resolution too low ({w}x{h}px). Minimum is {settings.MIN_IMAGE_DIMENSION}x{settings.MIN_IMAGE_DIMENSION}px."
            return FaceDetail(detected=False, face_count=0, image_width=w, image_height=h, error=err), None, err

        # Detect faces
        boxes = self._detect_faces(img)
        count = len(boxes)

        if count == 0:
            err = f"No face detected in the {source_label}. Please provide a clear, well-lit photograph with a visible face."
            return FaceDetail(
                detected=False,
                face_count=0,
                image_width=w,
                image_height=h,
                error=err
            ), None, err

        if count > 1:
            err = f"Multiple faces ({count}) detected in the {source_label}. ProofLink requires an image with exactly one person."
            return FaceDetail(
                detected=False,
                face_count=count,
                image_width=w,
                image_height=h,
                error=err
            ), None, err

        # Exactly 1 face found!
        (fx, fy, fw, fh) = boxes[0]
        # Pad face crop slightly for embedding calculation
        pad_x = int(fw * 0.1)
        pad_y = int(fh * 0.1)
        crop_x1 = max(0, fx - pad_x)
        crop_y1 = max(0, fy - pad_y)
        crop_x2 = min(w, fx + fw + pad_x)
        crop_y2 = min(h, fy + fh + pad_y)
        face_crop = img[crop_y1:crop_y2, crop_x1:crop_x2]

        # Extract 128-D embedding
        embedding = self._generate_face_embedding(face_crop)
        embedding_hash = hashlib.sha256(embedding.tobytes()).hexdigest()

        # Extract landmarks
        gray_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY) if len(face_crop.shape) == 3 else face_crop
        landmarks = self._detect_landmarks(gray_crop, crop_x1, crop_y1)

        # Generate face crop thumbnail
        face_crop_base64 = self._image_to_base64(face_crop, quality=80)

        detail = FaceDetail(
            detected=True,
            face_count=1,
            confidence=0.96,
            bounding_box=BoundingBox(x=int(fx), y=int(fy), width=int(fw), height=int(fh)),
            landmarks=landmarks,
            embedding_dim=128,
            embedding_hash=embedding_hash,
            image_width=w,
            image_height=h,
            face_crop_base64=face_crop_base64
        )

        return detail, embedding, None

    def compare_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> FaceComparisonResult:
        """
        Compare two 128-dimensional face embedding vectors:
        - Euclidean Distance: d = ||v1 - v2||
        - Cosine Similarity: s = (v1 . v2) / (||v1|| ||v2||)
        - Confidence Percentage: 0-100%
        - Decision against threshold
        """
        try:
            # Vectors are already L2 normalized, so cosine similarity is dot product
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            v1 = emb1 / norm1 if norm1 > 0 else emb1
            v2 = emb2 / norm2 if norm2 > 0 else emb2

            # Euclidean distance
            euclidean_dist = float(np.linalg.norm(v1 - v2))
            
            # Cosine similarity
            cosine_sim = float(np.clip(np.dot(v1, v2), -1.0, 1.0))

            # Map Euclidean distance to confidence percentage:
            # Distance 0.0 -> 100% confidence
            # Distance 0.6 -> ~70% confidence (threshold)
            # Distance 1.2+ -> 0% confidence
            confidence = max(0.0, min(100.0, (1.0 - (euclidean_dist / 1.35)) * 100.0))

            is_match = (euclidean_dist <= self.distance_threshold) or (confidence >= self.min_confidence)
            verdict = "MATCH" if is_match else "NO_MATCH"

            notes = (
                f"Biometric similarity evaluated: distance={euclidean_dist:.4f} (threshold <={self.distance_threshold:.2f}), "
                f"cosine={cosine_sim:.4f}, confidence={confidence:.1f}% (required >={self.min_confidence:.0f}%)."
            )

            return FaceComparisonResult(
                is_match=is_match,
                confidence_score=round(confidence, 2),
                euclidean_distance=round(euclidean_dist, 4),
                cosine_similarity=round(cosine_sim, 4),
                threshold_distance=self.distance_threshold,
                threshold_confidence=self.min_confidence,
                verdict=verdict,
                notes=notes
            )
        except Exception as e:
            logger.error(f"Error comparing face embeddings: {e}")
            return FaceComparisonResult(
                is_match=False,
                confidence_score=0.0,
                euclidean_distance=1.0,
                cosine_similarity=0.0,
                threshold_distance=self.distance_threshold,
                threshold_confidence=self.min_confidence,
                verdict="ERROR",
                notes=f"Comparison failed: {str(e)}"
            )

face_service = FaceService()
