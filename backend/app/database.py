import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("prooflink.database")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "prooflink.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database tables for ProofLink audit trails."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table for full verification audit records (only non-biometric metadata & hashes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verification_id TEXT UNIQUE NOT NULL,
            record_hash TEXT NOT NULL,
            selfie_sha256 TEXT NOT NULL,
            profile_sha256 TEXT NOT NULL,
            metadata_sha256 TEXT NOT NULL,
            input_url TEXT NOT NULL,
            resolved_url TEXT NOT NULL,
            platform TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            euclidean_distance REAL NOT NULL,
            cosine_similarity REAL NOT NULL,
            is_match INTEGER NOT NULL,
            notarized INTEGER NOT NULL,
            transaction_hash TEXT,
            block_number INTEGER,
            submitter TEXT,
            canonical_metadata TEXT NOT NULL,
            explorer_url TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # Table for independent re-verification check logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reverification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_hash TEXT NOT NULL,
            on_chain_exists INTEGER NOT NULL,
            tamper_detected INTEGER NOT NULL,
            submitter TEXT,
            checked_at TEXT NOT NULL
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_record_hash ON verification_records(record_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_hash ON verification_records(transaction_hash)")

    conn.commit()
    conn.close()
    logger.info("ProofLink SQLite database initialized.")

def save_record(rec: Dict[str, Any]) -> int:
    """Insert a new verification record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO verification_records (
                verification_id, record_hash, selfie_sha256, profile_sha256, metadata_sha256,
                input_url, resolved_url, platform, confidence_score, euclidean_distance,
                cosine_similarity, is_match, notarized, transaction_hash, block_number,
                submitter, canonical_metadata, explorer_url, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec.get("verification_id"),
            rec.get("record_hash"),
            rec.get("selfie_sha256"),
            rec.get("profile_sha256"),
            rec.get("metadata_sha256"),
            rec.get("input_url"),
            rec.get("resolved_url"),
            rec.get("platform"),
            rec.get("confidence_score"),
            rec.get("euclidean_distance"),
            rec.get("cosine_similarity"),
            1 if rec.get("is_match") else 0,
            1 if rec.get("notarized") else 0,
            rec.get("transaction_hash"),
            rec.get("block_number"),
            rec.get("submitter"),
            rec.get("canonical_metadata"),
            rec.get("explorer_url"),
            rec.get("timestamp") or datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        record_id = cursor.lastrowid
        return record_id
    finally:
        conn.close()

def get_records(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch latest verification records."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM verification_records 
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_record_by_hash(record_hash: str) -> Optional[Dict[str, Any]]:
    """Retrieve record by its record_hash or transaction_hash."""
    clean_hash = record_hash.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM verification_records 
            WHERE lower(record_hash) = ? OR lower(transaction_hash) = ? OR verification_id = ?
            LIMIT 1
        """, (clean_hash, clean_hash, record_hash.strip()))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def log_reverification(record_hash: str, on_chain_exists: bool, tamper_detected: bool, submitter: Optional[str]):
    """Record an independent re-verification query."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reverification_logs (
                record_hash, on_chain_exists, tamper_detected, submitter, checked_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            record_hash,
            1 if on_chain_exists else 0,
            1 if tamper_detected else 0,
            submitter,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
    finally:
        conn.close()

init_db()
