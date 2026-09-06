# FaceChain Verify: Step-by-Step Demonstration Guide

This guide walks through verifying the FaceChain Verify pipeline locally.

---

## 1. Prerequisites
- **Node.js**: v18+ (tested on Node v22.15.1)
- **Python**: 3.10+ (tested on Python 3.13.2)
- **PowerShell** (Windows) or **Bash** (Linux / macOS)

---

## 2. Quick Start

### Step 1: Start Local Hardhat Blockchain (Terminal 1)
```powershell
cd blockchain
npm install
npx hardhat node
```
This runs a local EVM network at `http://127.0.0.1:8545` with deterministic test accounts.

### Step 2: Deploy Smart Contract (Terminal 2)
```powershell
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```
Note the deployed address:
```
✓ ContentFingerprintRegistry deployed at: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### Step 3: Start Backend API (Terminal 3)
```powershell
# From repository root
.\backend_venv\Scripts\activate
cd backend
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000`.

### Step 4: Start Frontend UI (Terminal 4)
```powershell
# From repository root
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 3. Demonstration Walkthrough

1. **Upload Authorized Image**:
   - Drag and drop an authorized face image (or click one of the benchmark portraits).
   - Notice the preview and file size metadata.

2. **Run Verification**:
   - Click **"Run Verification"**.
   - Observe the 7-step pipeline progress:
     1. Image Upload & Validation (generates image SHA-256)
     2. Face AI (detects face bounding box & computes 128-D normalized embedding)
     3. Reverse Image Search (queries configured provider)
     4. Match Discovery (identifies potential public web/social content)
     5. Content Fingerprint (creates canonical JSON and SHA-256 hash)
     6. Blockchain Registration (registers `bytes32` fingerprint on smart contract)
     7. Independent Verification (queries blockchain to verify hash match)

3. **Explore Results**:
   - Inspect the **Face Detection Card** (bounding box, confidence, 128-D embedding representation).
   - Inspect the **Reverse Search Card** (actual discovered URL, platform badge).
   - Inspect the **Blockchain Card** (transaction hash, block height, contract address, copy buttons).

4. **Tamper Testing**:
   - Click **"Open in Tamper Lab"**.
   - Click **"Tamper URL"** or edit any field in the canonical JSON.
   - Click **"Verify Evidence Hash with On-Chain Record"**.
   - Observe immediate `RECORD_MISMATCH` detection and tamper alerts!
