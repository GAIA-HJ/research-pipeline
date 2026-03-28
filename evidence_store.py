import sqlite3
import json
from datetime import datetime


class EvidenceStore:
    def __init__(self, db_path: str = "evidence.db"):
        self.db = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS evidence_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                content_hash TEXT,
                payload TEXT,
                blockchain_tx TEXT
            );
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                topics_count INTEGER,
                articles_count INTEGER,
                status TEXT
            );
        """)
        self.db.commit()

    def store(self, data: dict, event_type: str = "article_generated"):
        self.db.execute(
            "INSERT INTO evidence_log (timestamp, event_type, content_hash, payload) VALUES (?,?,?,?)",
            (datetime.utcnow().isoformat(), event_type,
             data.get("content_hash", ""), json.dumps(data, default=str)),
        )
        self.db.commit()

    def log_run(self, cycle_id: str, topics: int, articles: int, status: str):
        self.db.execute(
            "INSERT INTO pipeline_runs (cycle_id, started_at, completed_at, topics_count, articles_count, status) VALUES (?,?,?,?,?,?)",
            (cycle_id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
             topics, articles, status),
        )
        self.db.commit()

    def get_history(self, limit: int = 50) -> list:
        rows = self.db.execute(
            "SELECT * FROM evidence_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [{"id": r[0], "ts": r[1], "type": r[2], "hash": r[3], "payload": r[4]} for r in rows]
