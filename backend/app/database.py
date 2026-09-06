import sqlite3
import json
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("facechain.database")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "facechain.db")

def get_db_connection():
    """Create and return a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for persistent records and creator activity logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Blockchain Records (Persistent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blockchain_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER UNIQUE,
            evidence_hash TEXT NOT NULL,
            result_url TEXT NOT NULL,
            platform TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            timestamp_iso TEXT NOT NULL,
            submitter TEXT NOT NULL,
            transaction_hash TEXT,
            block_number INTEGER,
            explorer_tx_url TEXT,
            explorer_contract_url TEXT,
            chain_name TEXT NOT NULL,
            chain_id INTEGER NOT NULL,
            evidence_json TEXT NOT NULL,
            is_simulated INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Table 2: Creator Master Activity Logs (Every upload, detection, search, verification)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            client_ip TEXT,
            user_agent TEXT,
            device_type TEXT,
            source_image_sha256 TEXT,
            face_count INTEGER DEFAULT 0,
            platform TEXT,
            matched_url TEXT,
            evidence_hash TEXT,
            blockchain_tx TEXT,
            record_id INTEGER,
            status TEXT NOT NULL,
            message TEXT,
            details_json TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    logger.info(f"SQLite database initialized at {DB_PATH}")

def save_blockchain_record(record_data: Dict[str, Any], evidence_dict: Dict[str, Any]) -> int:
    """Save or update an immutable blockchain record in the persistent database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT OR REPLACE INTO blockchain_records (
            record_id, evidence_hash, result_url, platform, timestamp, timestamp_iso,
            submitter, transaction_hash, block_number, explorer_tx_url, explorer_contract_url,
            chain_name, chain_id, evidence_json, is_simulated, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_data.get("record_id"),
        record_data.get("evidence_hash"),
        record_data.get("result_url") or record_data.get("matched_url"),
        record_data.get("platform"),
        record_data.get("timestamp", int(datetime.now(timezone.utc).timestamp())),
        record_data.get("timestamp_iso", now_iso),
        record_data.get("submitter"),
        record_data.get("transaction_hash"),
        record_data.get("block_number"),
        record_data.get("explorer_tx_url"),
        record_data.get("explorer_contract_url"),
        record_data.get("chain_name", "Polygon Amoy Testnet"),
        record_data.get("chain_id", 80002),
        json.dumps(evidence_dict),
        1 if record_data.get("is_simulated") else 0,
        now_iso
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_all_blockchain_records() -> List[Dict[str, Any]]:
    """Fetch all saved blockchain records ordered by newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blockchain_records ORDER BY id DESC")
    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        try:
            item["evidence"] = json.loads(item["evidence_json"])
        except Exception:
            item["evidence"] = {}
        item["is_simulated"] = bool(item["is_simulated"])
        results.append(item)
    conn.close()
    return results

def get_blockchain_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a specific blockchain record by record_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blockchain_records WHERE record_id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        try:
            item["evidence"] = json.loads(item["evidence_json"])
        except Exception:
            item["evidence"] = {}
        item["is_simulated"] = bool(item["is_simulated"])
        return item
    return None

def log_creator_activity(
    event_type: str,
    status: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    source_image_sha256: Optional[str] = None,
    face_count: int = 0,
    platform: Optional[str] = None,
    matched_url: Optional[str] = None,
    evidence_hash: Optional[str] = None,
    blockchain_tx: Optional[str] = None,
    record_id: Optional[int] = None,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> int:
    """Log an activity event for the creator's real-time audit trail."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Determine device type from user_agent
    device_type = "Desktop"
    if user_agent:
        ua = user_agent.lower()
        if "mobile" in ua or "android" in ua or "iphone" in ua:
            device_type = "Mobile (Android/iOS)"
        elif "tablet" in ua or "ipad" in ua:
            device_type = "Tablet"

    cursor.execute("""
        INSERT INTO activity_logs (
            event_type, client_ip, user_agent, device_type, source_image_sha256,
            face_count, platform, matched_url, evidence_hash, blockchain_tx,
            record_id, status, message, details_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_type,
        client_ip,
        user_agent,
        device_type,
        source_image_sha256,
        face_count,
        platform,
        matched_url,
        evidence_hash,
        blockchain_tx,
        record_id,
        status,
        message,
        json.dumps(details) if details else None,
        now_iso
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_activity_stats() -> Dict[str, Any]:
    """Calculate summary metrics for the Creator Master Activity Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM activity_logs")
    total_events = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE event_type = 'PIPELINE_RUN'")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM blockchain_records")
    total_blockchain_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE event_type = 'TAMPER_VERIFY' AND status = 'MISMATCH'")
    tamper_caught = cursor.fetchone()[0]

    cursor.execute("SELECT device_type, COUNT(*) FROM activity_logs GROUP BY device_type")
    device_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT platform, COUNT(*) FROM blockchain_records WHERE platform IS NOT NULL AND platform != '' GROUP BY platform")
    platform_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 50")
    recent_logs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_events": total_events,
        "total_scans": total_scans,
        "total_blockchain_records": total_blockchain_records,
        "tamper_incidents_caught": tamper_caught,
        "device_breakdown": device_breakdown,
        "platform_breakdown": platform_breakdown,
        "recent_logs": recent_logs
    }

# Initialize on import
init_db()
