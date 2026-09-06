# FaceChain Verify — Face ID + Blockchain Verification Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Network: Polygon Amoy](https://img.shields.io/badge/Network-Polygon%20Amoy%20(80002)-8247E5.svg)](https://amoy.polygonscan.com/)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![React: 18](https://img.shields.io/badge/React-18%20%2B%20TypeScript-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg)](https://fastapi.tiangolo.com/)

> **Detect a face. Find the image. Verify the evidence on-chain.**

**FaceChain Verify** is a production-grade full-stack pipeline that detects and encodes faces from photos, discovers genuine indexed social media posts using real-world reverse-image search, generates canonical cryptographic evidence hashes, records immutable proofs on the **Polygon Amoy Testnet** smart contract, and performs on-chain tamper verification.

---

## 🌟 Key Highlights & Features

- 🔍 **Real Face AI & Extraction**: Detects human faces with bounding boxes, facial landmarks, and generates a normalized 128-dimensional embedding representation.
- 🛡️ **Zero Biometric Exposure on Blockchain**: Raw photos and biometric vectors are **never written to the public ledger**. Only deterministic SHA-256 evidence fingerprints and metadata are registered on-chain.
- 🌐 **Genuine Reverse Image Search**: Configurable provider abstraction supporting **SerpApi (Google Lens / Google Images)**, **Azure Bing Visual Search**, **RapidAPI**, and **TinEye**. No hardcoded or fabricated search results.
- 📱 **Automated Social Media Classification**: Dynamically identifies whether visual matches belong to Instagram, X (Twitter), TikTok, YouTube, Reddit, LinkedIn, or Facebook from real returned domains.
- 🔒 **Deterministic Canonical Evidence Hashing**: Serializes evidence in RFC 8785 compliant canonical JSON and computes SHA-256 `bytes32` hashes.
- ⛓️ **Polygon Amoy Smart Contract**: Integrates with `FaceMatchRegistry.sol` via `web3.py` for gas estimation, backend signing, transaction receipts, and Polygonscan explorer verification.
- 🧪 **Interactive Tamper-Evident Lab**: Allows evaluators to modify evidence fields and instantly verify how the calculated hash mismatches the immutable blockchain record.
- 🎨 **Modern Cyber-Security UI/UX**: Built with React, TypeScript, Tailwind CSS, Lucide icons, and Framer Motion with animated pipeline progress and interactive bounding box canvas.

---

## 🏗️ Architecture & Pipeline Flow

```text
       ┌────────────────────────┐
       │     Input Photo        │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Face AI Detection    │  ──► Bounding Boxes, Landmarks & 128-D Fingerprint
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  Reverse Image Search  │  ──► Queries Live Provider (SerpApi / Google Lens / Bing)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Social Classification  │  ──► Identifies Instagram / X / TikTok / YouTube / Reddit
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Canonical Evidence     │  ──► Deterministic JSON (RFC 8785)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  SHA-256 Hashing       │  ──► EVM-compatible bytes32 fingerprint (0x...)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Polygon Amoy Contract  │  ──► registerRecord(evidenceHash, resultUrl, platform)
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Tamper Verification    │  ──► Compare Local Re-Hash vs. On-Chain Immutable Hash
       └────────────────────────┘
```

---

## 📁 Repository Structure

```text
facechain-verify/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # FastAPI endpoints (Pipeline, Face, Search, Blockchain)
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic schemas and typed data models
│   │   ├── services/
│   │   │   ├── face_service.py        # OpenCV face detection & embedding fingerprinting
│   │   │   ├── reverse_search.py      # Provider abstraction (SerpApi, Bing, RapidAPI, Demo)
│   │   │   ├── hashing_service.py     # Deterministic JSON canonicalization & SHA-256
│   │   │   └── blockchain_service.py  # Web3.py Polygon Amoy contract integration
│   │   ├── utils/
│   │   │   └── helpers.py             # Social regex classifier, secure filenames, validation
│   │   ├── config.py                  # Pydantic settings & environment configuration
│   │   └── main.py                    # FastAPI application entrypoint
│   ├── tests/                         # Full automated test suite (12 tests)
│   ├── requirements.txt               # Python backend dependencies
│   └── .env.example                   # Environment template
│
├── contracts/
│   ├── FaceMatchRegistry.sol          # Solidity 0.8.20 registry smart contract
│   ├── FaceMatchRegistry.json         # Contract ABI definition
│   └── deploy.py                      # Python Web3 deployment tool
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx             # Navigation & connection indicators
│   │   │   ├── ImageUploader.tsx      # Drag & drop upload + benchmark sample selector
│   │   │   ├── CanvasBoundingBox.tsx  # Dynamic HTML5 canvas face bounding box overlay
│   │   │   ├── PipelineProgress.tsx   # 7-step animated execution flow
│   │   │   ├── FaceDetectionCard.tsx  # Face analysis metrics & embedding fingerprint
│   │   │   ├── ReverseSearchCard.tsx  # Genuine search result & social badge
│   │   │   ├── BlockchainCard.tsx     # Transaction hash, block height & explorer links
│   │   │   ├── VerificationBadge.tsx  # Verified on-chain / mismatch status display
│   │   │   ├── TamperTester.tsx       # Interactive tamper lab for evaluators
│   │   │   ├── TechnicalDetails.tsx   # Collapsible architecture specification drawer
│   │   │   └── LimitationsModal.tsx   # Known limitations & ethical AI disclosure
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx          # Main pipeline dashboard
│   │   │   ├── HistoryPage.tsx        # Searchable on-chain registry history
│   │   │   ├── RecordDetail.tsx       # Historical record inspector with re-verification
│   │   │   └── SettingsPage.tsx       # Live health status of all subsystems
│   │   ├── services/
│   │   │   └── api.ts                 # Typed API client
│   │   ├── types/
│   │   │   └── index.ts               # Shared TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites & Environment

- **Python**: Version `3.10` or higher
- **Node.js**: Version `18` or `20+` (and `npm`)
- **Polygon Amoy Testnet Wallet**: Any EVM private key with testnet POL (obtain free tokens from [Polygon Faucet](https://faucet.polygon.technology/))
- **Reverse Image Search API**: [SerpApi](https://serpapi.com/) API Key, Azure Bing Visual Search, or RapidAPI. (An explicitly labeled Demo Mode fallback is included if API keys are not yet configured).

---

## 🚀 Quickstart Installation

### 1. Clone & Setup Backend

```bash
# Clone the repository
git clone https://github.com/your-username/facechain-verify.git
cd facechain-verify

# Create Python Virtual Environment
python -m venv .venv

# Activate Virtual Environment
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env.example` template:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# -----------------------------------------------------------------
# Reverse Image Search Configuration
# -----------------------------------------------------------------
REVERSE_IMAGE_PROVIDER=serpapi
REVERSE_IMAGE_API_KEY=your_serpapi_key_here

# -----------------------------------------------------------------
# Blockchain Configuration (Polygon Amoy Testnet default)
# -----------------------------------------------------------------
CHAIN_ID=80002
CHAIN_NAME=Polygon Amoy Testnet
BLOCKCHAIN_RPC_URL=https://rpc-amoy.polygon.technology/
BLOCKCHAIN_EXPLORER_URL=https://amoy.polygonscan.com
PRIVATE_KEY=your_testnet_private_key_here
CONTRACT_ADDRESS=0x98Fc85d03C891C808E5F495493019808381D4bA5

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Deploy the Smart Contract (Optional / Testnet)

To deploy your own instance of `FaceMatchRegistry.sol` to Polygon Amoy:

```bash
python contracts/deploy.py
```

Copy the generated contract address and paste it into `backend/.env` under `CONTRACT_ADDRESS`.

### 4. Run Backend Server

```bash
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

The API docs are immediately accessible at `http://127.0.0.1:8000/docs`.

### 5. Setup & Run Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

FaceChain Verify includes automated tests for all components:

```bash
pytest backend/tests -v
```

### Test Coverage:
- `test_face_service.py`: Multi-scale face detection, bounding box extraction, safe embedding fingerprint calculation, blank image rejection, and corrupt file error handling.
- `test_hashing.py`: Key insertion order invariance (RFC 8785 canonicalization), SHA-256 / bytes32 formatting, and tamper sensitivity.
- `test_reverse_search.py`: Social media domain classification regex and provider normalization.
- `test_blockchain.py`: Smart contract evidence registration, record querying, verified hash comparison, and tamper detection.
- `test_api.py`: FastAPI health, system configuration status, and full pipeline endpoints.

---

## 🎥 End-to-End Unedited Demonstration Workflow

To demonstrate the full pipeline in an unedited screen recording:

1. **Open Dashboard**: Start at `http://localhost:5173`. Show the connected status pill (`Polygon Amoy` / `Connected`).
2. **Upload Photograph**: Drag and drop a portrait photo (or select one of the built-in benchmark portrait samples).
3. **Face AI Detection**: Observe the interactive canvas drawing the cyan bounding box, landmarks, confidence percentage, and deterministic embedding fingerprint.
4. **Click "Run Verification"**:
   - Step 01: Image received and validated.
   - Step 02: Face detected and encoded.
   - Step 03: Reverse image search executes across genuine search providers.
   - Step 04: Social media domain classification extracts the real post URL (e.g. Instagram / X / TikTok).
   - Step 05: Canonical JSON generated and hashed to SHA-256 `bytes32`.
   - Step 06: Smart contract transaction submitted on Polygon Amoy. Transaction hash and block height returned.
   - Step 07: On-chain tamper verification executes and displays `✓ VERIFIED ON-CHAIN`.
5. **Open Blockchain Explorer**: Click "View on Explorer" to open the live transaction on Polygonscan (`https://amoy.polygonscan.com/tx/0x...`).
6. **Demonstrate Tamper Lab**:
   - Navigate to the **Tamper Lab** tab.
   - Click **⚡ Tamper URL** or alter a single character in the evidence payload.
   - Click **Verify Evidence Hash**.
   - Watch the system immediately alert: `✕ RECORD MISMATCH (TAMPERED) — Tampering Detected`.

---

## ⚖️ Known Limitations & Ethical AI Disclosure

1. **Visual Similarity ≠ Ownership**: Reverse-image search identifies indexed web matches based on visual similarity. It does **not** authenticate that the person depicted owns or controls the target social media account.
2. **Probabilistic Face Embeddings**: Facial embeddings are probabilistic mathematical representations and should not be used as infallible proof of personal identity.
3. **Zero Biometrics on Public Ledgers**: Public blockchains are permanent and public; raw biometric vectors and photos are **never stored on-chain**. Only cryptographic SHA-256 evidence hashes and verified metadata are recorded.
4. **Third-Party Indexing Policies**: Social media platforms with private profiles or strict robots.txt directives may not return indexed results through search engines.
5. **Transparency**: When search providers return no social media matches, the system transparently reports "No social match found" and will never fabricate fake results.

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).
