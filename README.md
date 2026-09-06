# FaceChain Verify

> **Decentralized Biometric Evidence & Cryptographic Web Discovery Protocol**
> Authorized Image → Multi-Tier Face AI → Genuine Reverse Search → Canonical Fingerprint → Blockchain Record → Independent Verification

---

## 1. Overview
**FaceChain Verify** is an end-to-end, production-ready demonstration protocol designed to discover and register immutable cryptographic proof of publicly indexed web and social media content matching an authorized face image.

By combining computer vision face detection, genuine multi-provider reverse-image search, deterministic JSON canonicalization (RFC 8785 principles), and Ethereum-compatible smart contracts, FaceChain Verify creates a tamper-evident audit trail without ever exposing or storing raw biometric data.

---

## 2. Problem
1. **Unverifiable Web Content**: When visual media appears across public platforms, verifying its origin and indexing history is difficult.
2. **Biometric Privacy Risks**: Centralized biometric databases expose sensitive personal data to surveillance, leakage, and unauthorized matching.
3. **Evidence Tampering**: Digital metadata (timestamps, URLs, platforms) can easily be manipulated without cryptographic timestamps and tamper-evident ledgers.

---

## 3. Solution
FaceChain Verify solves these challenges by establishing clear boundaries:
- **Zero Identity Claims**: Does **NOT** identify individuals by name or compare against citizen databases.
- **Zero Biometric Exposure**: Raw images and embedding vectors are **never** stored on-chain or persisted permanently.
- **Cryptographic Immutability**: Discovered web metadata is canonically formatted and hashed with SHA-256 (`bytes32`). Only this cryptographic fingerprint is written to the blockchain.
- **Independent Re-Verification**: Anyone can reconstruct the metadata object, recompute the SHA-256 digest, and independently confirm integrity against the smart contract.

---

## 4. Pipeline

```
INPUT (Authorized Image)
      ↓
FACE DETECTION (OpenCV Multi-Cascade & Contours)
      ↓
FACE ENCODING (128-D Temporary Normalized Representation)
      ↓
GENUINE REVERSE SEARCH (SerpApi / Google Lens, Bing, RapidAPI)
      ↓
PUBLIC RESULT (Live Discovered Public Web / Social Media Content)
      ↓
CONTENT FINGERPRINT (Deterministic JSON + SHA-256 Digest)
      ↓
BLOCKCHAIN (ContentFingerprintRegistry.sol Smart Contract)
      ↓
RECOMPUTE (Canonical Hash Regeneration)
      ↓
VERIFY (Cryptographic Comparison: VERIFIED vs MISMATCH)
```

---

## 5. Features
- **Multi-Scale Face Detection**: OpenCV multi-cascade and contour detector validating face presence, bounding box, quality scores, and 128-D normalized embedding vectors.
- **Genuine Reverse Image Search**: Live integrations with SerpApi (Google Lens & Google Reverse Image), Microsoft Bing Visual Search, and RapidAPI with explicit match states (`FOUND`, `POSSIBLE_MATCH`, `NOT_FOUND`, `ERROR`).
- **Deterministic Canonical Serialization**: RFC-compliant JSON serialization (sorted keys, compact separators) ensuring identical hash generation across platforms.
- **Solidity Smart Contract**: `ContentFingerprintRegistry.sol` (Solidity 0.8.20) for recording tamper-evident metadata fingerprints on Ethereum-compatible networks.
- **Independent Re-Verification & Tamper Lab**: Real-time verification engine and interactive developer testing lab to demonstrate tamper detection.
- **Premium Dark Dashboard**: Responsive React 18, TypeScript, Tailwind CSS, Lucide icons, glassmorphism UI, and PWA installation support.
- **Comprehensive Testing Suite**: Pytest unit & integration tests, Hardhat smart contract tests, and full E2E pipeline verification.

---

## 6. Architecture & Technologies

### Architecture Diagram
See [docs/architecture.md](docs/architecture.md) for complete Mermaid diagrams and architectural breakdowns.

### Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React Icons.
- **Backend**: Python 3.13 / 3.10+, FastAPI, Uvicorn, Pydantic v2, Web3.py.
- **Computer Vision**: OpenCV (Open Source Computer Vision Library), NumPy.
- **Blockchain**: Solidity 0.8.20, Hardhat, Ethers.js, Web3.py (Supports Local Hardhat Node and Polygon Amoy).
- **Database**: SQLite (Local metadata & audit activity persistence).
- **Testing**: Pytest (Backend & E2E), Hardhat / Mocha / Chai (Smart Contracts).

---

## 7. Face Processing
- **Input Formats**: JPG, JPEG, PNG, WEBP.
- **Validations**: File size (<= 10MB), image dimensions (min 50x50px, max 8000x8000px), corrupted header checks.
- **Single-Face Policy**: Prefers exactly one clearly detectable face. Zero faces halts execution gracefully; multiple faces prompts single-subject upload.
- **Ephemeral Embeddings**: Generates a temporary normalized 128-dimensional spatial feature moment vector for quality estimation. Biometric vectors are discarded after processing and never put on-chain.

---

## 8. Reverse Image Search
Supported search providers:
1. **SerpApi**: Google Lens / Google Reverse Image engine (`google_lens`, `google_reverse_image`).
2. **Bing Visual Search**: Azure Cognitive Services Visual Search API.
3. **RapidAPI**: Google Lens & Reverse Image endpoints.
4. **Demo Mode Provider**: Deterministic local sample dataset clearly labeled `DEMO DATA — NOT A LIVE SEARCH RESULT` for offline testing.

---

## 9. Blockchain & Smart Contract
- **Contract Name**: `ContentFingerprintRegistry.sol`
- **Network**: Local Hardhat / Anvil (`http://127.0.0.1:8545`) or Ethereum Testnet (Polygon Amoy / Sepolia).
- **Data Model Stored On-Chain**:
  ```solidity
  struct VerificationRecord {
      bytes32 fingerprint;   // SHA-256 hash of canonical discovered metadata JSON
      string sourceUrl;      // Discovered public web/social URL
      uint256 timestamp;     // Block timestamp of registration
      address submitter;     // Address of submitting wallet
  }
  mapping(bytes32 => VerificationRecord) public records;
  ```
- **Events**: Emits `FingerprintRegistered(bytes32 indexed fingerprint, string sourceUrl, uint256 timestamp, address indexed submitter)`.

---

## 10. Privacy & Ethics Statement
> **IMPORTANT PRIVACY NOTICE**
> This demonstration processes only images the user is authorized to use. It does NOT identify people by name or compare faces against a database of individuals. Blockchain records contain cryptographic metadata fingerprints, never raw biometric data or images.

---

## 11. Project Structure

```
facechain-verify/
├── frontend/                     # React + TypeScript + Vite UI
│   ├── src/
│   │   ├── components/           # UI Cards, Uploader, TamperTester, Progress
│   │   ├── pages/                # Dashboard, HistoryPage, TamperLab, Settings
│   │   ├── services/api.ts       # Typed API Client
│   │   └── types/index.ts        # TypeScript Interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── main.py               # Application entrypoint & SPA mounting
│   │   ├── config.py             # App settings & env loading
│   │   ├── models/schemas.py     # Pydantic validation schemas
│   │   ├── services/             # Face AI, Search, Hashing, Blockchain, Verification
│   │   └── utils/helpers.py      # Image validation & domain classifier
│   ├── tests/                    # Pytest test suite (19 test cases)
│   ├── requirements.txt
│   └── .env.example
│
├── blockchain/                   # Hardhat Smart Contract Environment
│   ├── contracts/                # ContentFingerprintRegistry.sol
│   ├── scripts/deploy.js         # Deployment script
│   ├── test/                     # Hardhat Chai test suite (8 test cases)
│   ├── hardhat.config.js
│   └── package.json
│
├── sample/                       # Benchmark test guidelines & images
│   └── README.md
├── docs/                         # Architecture & Walkthrough Documentation
│   ├── architecture.md
│   └── demo.md
├── .gitignore
├── README.md
├── docker-compose.yml
└── LICENSE
```

---

## 12. Installation & Quick Start

### Prerequisites
- **Node.js**: v18+ (tested on Node v22.15.1)
- **Python**: 3.10+ (tested on Python 3.13.2)
- **Git**

---

### Step 1: Clone Repository
```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd facechain-verify
```

---

### Step 2: Blockchain Setup (Hardhat)
```powershell
cd blockchain
npm install
# Terminal A: Start local blockchain node
npx hardhat node
```

In a second terminal, deploy the smart contract:
```powershell
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

---

### Step 3: Backend Setup
```powershell
# In a new terminal (repository root)
python -m venv backend_venv

# Windows PowerShell:
.\backend_venv\Scripts\Activate.ps1
# Linux / macOS:
# source backend_venv/bin/activate

pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

---

### Step 4: Frontend Setup
```powershell
# In a new terminal (repository root)
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 13. Running Automated Tests

### 1. Smart Contract Tests (Hardhat)
```powershell
cd blockchain
npx hardhat test
```
*Output: 8 passing tests (registration, verification, duplicate rejection, event emission).*

### 2. Backend & E2E Pipeline Tests (Pytest)
```powershell
# From repository root
.\backend_venv\Scripts\python -m pytest backend/tests
```
*Output: 19 passing tests covering API endpoints, face detection, blank images, corrupt files, canonical JSON hashing, and blockchain verification.*

### 3. Frontend Build & Typecheck
```powershell
cd frontend
npm run build
```
*Output: Zero TypeScript errors; production build generated in `dist/`.*

---

## 14. Docker Deployment (Optional)
To run the full stack with Docker Compose:
```powershell
docker-compose up --build
```
Services will be accessible at:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Blockchain Node: `http://localhost:8545`

---

## 15. Troubleshooting & FAQ

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `No face detected` | Uploaded image contains no human face or lighting is too dark. | Upload a clear frontal portrait with adequate lighting. |
| `Multiple faces detected` | Image contains several subjects. | For individual record verification, crop to single face. |
| `Reverse-image search provider is not configured` | `REVERSE_SEARCH_API_KEY` is empty and demo fallback is disabled. | Provide an API key in `.env` or enable `ALLOW_DEMO_FALLBACK=true`. |
| `Blockchain RPC connection failed` | Hardhat node is not running on port 8545. | Run `npx hardhat node` in `blockchain/`. |
| `Verification Mismatch` | Discovered metadata or image hash was altered. | Re-verify with unaltered canonical JSON evidence. |

---

## 16. Git Push Commands

```bash
git init
git add .
git commit -m "Build FaceChain Verify pipeline end-to-end"
git branch -M main
git remote add origin <USER_GITHUB_REPOSITORY_URL>
git push -u origin main
```

---

## 17. License
Distributed under the MIT License. See [LICENSE](LICENSE) for details.
