import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from web3 import Web3
from eth_account import Account
from app.config import settings
from app.models.schemas import (
    CanonicalEvidence,
    BlockchainRegisterResponse,
    BlockchainRecordData,
    VerificationResult
)
from app.services.hashing_service import hashing_service
from app.database import (
    save_blockchain_record,
    get_all_blockchain_records,
    get_blockchain_record_by_id,
    log_creator_activity
)

logger = logging.getLogger("facechain.blockchain_service")

# Default ABI path
ABI_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "contracts", "FaceMatchRegistry.json")

class BlockchainService:
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.account = None
        self.abi = self._load_abi()
        self._in_memory_records: Dict[int, Dict[str, Any]] = {}
        self._in_memory_tx_history: List[Dict[str, Any]] = []
        self._init_web3()

    def _load_abi(self) -> list:
        """Load contract ABI from JSON file."""
        if os.path.exists(ABI_PATH):
            try:
                with open(ABI_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("abi", [])
            except Exception as e:
                logger.error(f"Failed to read contract ABI: {e}")
        return []

    def _init_web3(self):
        """Initialize Web3 connection and Contract instance."""
        try:
            rpc_url = settings.BLOCKCHAIN_RPC_URL.strip()
            if rpc_url:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 15}))
                if self.w3.is_connected():
                    logger.info(f"Connected to Blockchain RPC: {rpc_url} (Chain ID: {self.w3.eth.chain_id})")
                else:
                    logger.warning(f"Could not connect to Blockchain RPC: {rpc_url}")
            
            # Setup backend account if private key is provided
            pk = settings.PRIVATE_KEY.strip()
            if pk:
                if not pk.startswith("0x"):
                    pk = f"0x{pk}"
                self.account = Account.from_key(pk)
                logger.info(f"Signer account loaded: {self.account.address}")
                
            # Setup contract instance if address is provided
            addr = settings.CONTRACT_ADDRESS.strip()
            if self.w3 and addr and Web3.is_address(addr) and self.abi:
                checksum_addr = Web3.to_checksum_address(addr)
                self.contract = self.w3.eth.contract(address=checksum_addr, abi=self.abi)
                logger.info(f"Smart contract attached at: {checksum_addr}")
        except Exception as e:
            logger.warning(f"Blockchain service initialization notice: {e}")

    def is_rpc_connected(self) -> bool:
        """Check whether Web3 is connected to an active RPC node."""
        try:
            return bool(self.w3 and self.w3.is_connected())
        except Exception:
            return False

    def is_contract_configured(self) -> bool:
        """Check if contract and signer account are ready for live transactions."""
        return bool(self.is_rpc_connected() and self.contract and self.account)

    def _get_explorer_tx_url(self, tx_hash: str) -> str:
        base = settings.BLOCKCHAIN_EXPLORER_URL.rstrip("/")
        return f"{base}/tx/{tx_hash}"

    def _get_explorer_contract_url(self, address: str) -> str:
        base = settings.BLOCKCHAIN_EXPLORER_URL.rstrip("/")
        return f"{base}/address/{address}"

    async def register_evidence_on_chain(self, evidence: CanonicalEvidence) -> BlockchainRegisterResponse:
        """
        Submit a transaction to register evidence hash on-chain.
        Uses live Polygon Amoy testnet if configured, or in-memory verifiable test registry if keys are unset.
        """
        hash_res = hashing_service.hash_evidence(evidence)
        bytes32_evidence_hash = Web3.to_bytes(hexstr=hash_res.bytes32_hash)

        # Attempt live on-chain transaction if contract and account are configured
        if self.is_contract_configured():
            try:
                sender_addr = self.account.address
                nonce = self.w3.eth.get_transaction_count(sender_addr, "pending")
                gas_price = self.w3.eth.gas_price

                # Build transaction
                tx = self.contract.functions.registerRecord(
                    bytes32_evidence_hash,
                    evidence.matched_url,
                    evidence.platform
                ).build_transaction({
                    'from': sender_addr,
                    'nonce': nonce,
                    'gasPrice': gas_price,
                    'chainId': settings.CHAIN_ID
                })

                # Estimate gas or provide safe limit
                try:
                    estimated_gas = self.w3.eth.estimate_gas(tx)
                    tx['gas'] = int(estimated_gas * 1.2)
                except Exception:
                    tx['gas'] = 300000

                # Sign and send transaction
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=settings.PRIVATE_KEY)
                tx_hash_bytes = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_hash_hex = self.w3.to_hex(tx_hash_bytes)

                # Wait for receipt
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=60)
                
                # Parse RecordRegistered event from receipt logs
                record_id = None
                try:
                    logs = self.contract.events.RecordRegistered().process_receipt(receipt)
                    if logs:
                        record_id = logs[0]['args']['recordId']
                except Exception as ex:
                    logger.warning(f"Could not parse event logs: {ex}")
                
                if record_id is None:
                    # Fallback to reading current recordCount - 1
                    try:
                        record_id = self.contract.functions.recordCount().call() - 1
                    except Exception:
                        record_id = 0

                now_iso = datetime.now(timezone.utc).isoformat()

                resp = BlockchainRegisterResponse(
                    success=bool(receipt.status == 1),
                    record_id=int(record_id),
                    evidence_hash=hash_res.bytes32_hash,
                    transaction_hash=tx_hash_hex,
                    block_number=receipt.blockNumber,
                    gas_used=receipt.gasUsed,
                    contract_address=settings.CONTRACT_ADDRESS,
                    explorer_tx_url=self._get_explorer_tx_url(tx_hash_hex),
                    submitter=sender_addr,
                    timestamp=now_iso,
                    chain_id=settings.CHAIN_ID,
                    chain_name=settings.CHAIN_NAME,
                    is_simulated=False
                )

                # Save to local cache for instant UI lookups
                self._cache_record(resp, evidence)
                return resp

            except Exception as e:
                logger.error(f"Live blockchain transaction failed: {e}")
                if not settings.ALLOW_DEMO_FALLBACK:
                    raise RuntimeError(f"Blockchain registration failed on {settings.CHAIN_NAME}: {e}")
                logger.info("Falling back to local verifiable test registry for offline/demo run.")

        # Fallback verifiable in-memory simulation for local testing without gas expenditure
        sim_id = len(self._in_memory_records) + 1
        sim_tx_hash = f"0x{Web3.keccak(text=f'{sim_id}-{hash_res.bytes32_hash}-{time.time()}').hex()}"
        sim_block = 14829300 + sim_id
        now_ts = int(time.time())
        now_iso = datetime.fromtimestamp(now_ts, timezone.utc).isoformat()
        sim_submitter = self.account.address if self.account else "0x71C5A87a2C0c8e23fC67104e137b0cD882A31a61"
        sim_contract = settings.CONTRACT_ADDRESS if settings.CONTRACT_ADDRESS else "0x98Fc85d03C891C808E5F495493019808381D4bA5"

        sim_record = {
            "record_id": sim_id,
            "evidence_hash": hash_res.bytes32_hash,
            "result_url": evidence.matched_url,
            "platform": evidence.platform,
            "timestamp": now_ts,
            "timestamp_iso": now_iso,
            "submitter": sim_submitter,
            "transaction_hash": sim_tx_hash,
            "block_number": sim_block,
            "explorer_tx_url": self._get_explorer_tx_url(sim_tx_hash),
            "explorer_contract_url": self._get_explorer_contract_url(sim_contract),
            "chain_name": settings.CHAIN_NAME,
            "chain_id": settings.CHAIN_ID,
            "evidence": evidence.model_dump(),
            "is_simulated": True
        }
        self._in_memory_records[sim_id] = sim_record
        self._in_memory_tx_history.insert(0, sim_record)

        return BlockchainRegisterResponse(
            success=True,
            record_id=sim_id,
            evidence_hash=hash_res.bytes32_hash,
            transaction_hash=sim_tx_hash,
            block_number=sim_block,
            gas_used=42150,
            contract_address=sim_contract,
            explorer_tx_url=self._get_explorer_tx_url(sim_tx_hash),
            submitter=sim_submitter,
            timestamp=now_iso,
            chain_id=settings.CHAIN_ID,
            chain_name=settings.CHAIN_NAME,
            is_simulated=True
        )

    def _cache_record(self, reg_resp: BlockchainRegisterResponse, evidence: CanonicalEvidence):
        record_data = {
            "record_id": reg_resp.record_id,
            "evidence_hash": reg_resp.evidence_hash,
            "result_url": evidence.matched_url,
            "platform": evidence.platform,
            "timestamp": int(time.time()),
            "timestamp_iso": reg_resp.timestamp,
            "submitter": reg_resp.submitter,
            "transaction_hash": reg_resp.transaction_hash,
            "block_number": reg_resp.block_number,
            "explorer_tx_url": reg_resp.explorer_tx_url,
            "explorer_contract_url": self._get_explorer_contract_url(reg_resp.contract_address),
            "chain_name": reg_resp.chain_name,
            "chain_id": reg_resp.chain_id,
            "evidence": evidence.model_dump(),
            "is_simulated": reg_resp.is_simulated
        }
        self._in_memory_records[reg_resp.record_id] = record_data
        self._in_memory_tx_history.insert(0, record_data)
        
        # Persist to SQLite Database
        try:
            save_blockchain_record(record_data, evidence.model_dump())
        except Exception as e:
            logger.warning(f"Failed to persist blockchain record to SQLite: {e}")

    async def get_record_by_id(self, record_id: int) -> Optional[BlockchainRecordData]:
        """Fetch record data from on-chain smart contract, SQLite DB, or cache."""
        if self.is_contract_configured():
            try:
                res = self.contract.functions.getRecord(record_id).call()
                ev_hash_bytes = res[0]
                ev_hash_hex = f"0x{ev_hash_bytes.hex()}"
                result_url = res[1]
                platform = res[2]
                ts = res[3]
                submitter = res[4]
                ts_iso = datetime.fromtimestamp(ts, timezone.utc).isoformat()
                
                return BlockchainRecordData(
                    record_id=record_id,
                    evidence_hash=ev_hash_hex,
                    result_url=result_url,
                    platform=platform,
                    timestamp=ts,
                    timestamp_iso=ts_iso,
                    submitter=submitter,
                    chain_name=settings.CHAIN_NAME,
                    chain_id=settings.CHAIN_ID,
                    explorer_contract_url=self._get_explorer_contract_url(settings.CONTRACT_ADDRESS)
                )
            except Exception as e:
                logger.warning(f"Failed to query on-chain record #{record_id}: {e}")

        # Check in-memory store
        cached = self._in_memory_records.get(record_id)
        if not cached:
            # Check SQLite Database
            db_rec = get_blockchain_record_by_id(record_id)
            if db_rec:
                cached = db_rec
                self._in_memory_records[record_id] = cached

        if cached:
            return BlockchainRecordData(
                record_id=cached["record_id"],
                evidence_hash=cached["evidence_hash"],
                result_url=cached["result_url"],
                platform=cached["platform"],
                timestamp=cached["timestamp"],
                timestamp_iso=cached["timestamp_iso"],
                submitter=cached["submitter"],
                transaction_hash=cached.get("transaction_hash"),
                block_number=cached.get("block_number"),
                explorer_tx_url=cached.get("explorer_tx_url"),
                explorer_contract_url=cached.get("explorer_contract_url"),
                chain_name=cached["chain_name"],
                chain_id=cached["chain_id"]
            )

        return None

    async def verify_evidence(self, record_id: int, evidence: CanonicalEvidence) -> VerificationResult:
        """
        Recalculate the SHA-256 evidence hash from the provided evidence JSON,
        read the record from the blockchain, and compare them.
        """
        # 1. Recalculate local hash
        hash_res = hashing_service.hash_evidence(evidence)
        calc_hash = hash_res.bytes32_hash.lower()

        # 2. Query blockchain record
        bc_record = await self.get_record_by_id(record_id)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not bc_record:
            return VerificationResult(
                record_id=record_id,
                is_verified=False,
                status="NOT_FOUND",
                calculated_hash=calc_hash,
                blockchain_hash="0x0000000000000000000000000000000000000000000000000000000000000000",
                hashes_match=False,
                blockchain_record=None,
                verification_message=f"Record #{record_id} does not exist on {settings.CHAIN_NAME}.",
                tamper_detected=False,
                verified_at=now_iso
            )

        on_chain_hash = bc_record.evidence_hash.lower()
        hashes_match = (calc_hash == on_chain_hash)

        if hashes_match:
            status = "VERIFIED"
            tamper_detected = False
            message = "✓ Evidence fingerprint matches the immutable blockchain record. Verification confirmed."
        else:
            status = "RECORD_MISMATCH"
            tamper_detected = True
            message = "✕ VERIFICATION FAILED: The provided evidence hash does not match the immutable record registered on the blockchain. Tampering detected."

        # Log verification to database
        try:
            log_creator_activity(
                event_type="TAMPER_VERIFY",
                status="VERIFIED" if hashes_match else "MISMATCH",
                evidence_hash=calc_hash,
                record_id=record_id,
                message=message,
                details={"calculated_hash": calc_hash, "blockchain_hash": on_chain_hash, "is_verified": hashes_match}
            )
        except Exception:
            pass

        return VerificationResult(
            record_id=record_id,
            is_verified=hashes_match,
            status=status,
            calculated_hash=calc_hash,
            blockchain_hash=on_chain_hash,
            hashes_match=hashes_match,
            blockchain_record=bc_record,
            verification_message=message,
            tamper_detected=tamper_detected,
            verified_at=now_iso
        )

    def get_history(self) -> List[Dict[str, Any]]:
        """Return history of registered verification records from SQLite database."""
        try:
            db_records = get_all_blockchain_records()
            if db_records:
                return db_records
        except Exception:
            pass
        return self._in_memory_tx_history

# Global singleton instance
blockchain_service = BlockchainService()
