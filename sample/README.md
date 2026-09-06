# Sample Test Images & Benchmark Guidelines

FaceChain Verify includes sample test images and synthetic face generators for validating the pipeline offline and online.

---

## Benchmark Image Types

1. **Standard High-Contrast Portrait (`portrait_female.jpg`)**:
   - Single clearly visible frontal face.
   - Used for validating cascade detection, 128-D embedding moments, and reverse search.

2. **Speaker Headshot (`portrait_male.jpg`)**:
   - Natural ambient lighting portrait with neutral background.
   - Validates multi-scale cascade detection and bounding box clamping.

3. **Profile / Angle Headshot (`portrait_profile.jpg`)**:
   - Tilted face angle.
   - Validates multi-cascade profile fallbacks.

4. **Negative Test: Blank / Landscape Image (`landscape_no_face.jpg`)**:
   - Contains no human face.
   - Validates that the face detection stage halts gracefully with `face_detected = false` and clear user notification.

---

## Offline Synthetic Face Generator
The frontend includes an embedded HTML5 Canvas procedural face generator (`ImageUploader.tsx`), allowing deterministic pipeline demonstrations with zero external internet dependencies.
