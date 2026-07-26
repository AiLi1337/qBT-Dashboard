from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS qb_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    encrypted_password TEXT NOT NULL,
    verify_tls INTEGER NOT NULL,
    enabled INTEGER NOT NULL,
    reannounce_enabled INTEGER NOT NULL,
    interval_minutes INTEGER NOT NULL,
    request_timeout_seconds INTEGER NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 3,
    app_version TEXT,
    webapi_version TEXT,
    last_status TEXT,
    last_error_message TEXT,
    last_checked_at TEXT,
    last_run_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reannounce_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qb_instance_id INTEGER NOT NULL,
    trigger_source TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    torrent_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    FOREIGN KEY(qb_instance_id) REFERENCES qb_instances(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_runs_instance_started_at ON reannounce_runs(qb_instance_id, started_at DESC);
"""


def migrate_add_retry_count(db: Database) -> None:
    """Add retry_count column to existing databases."""
    with db.connection() as conn:
        # Check if column exists
        cursor = conn.execute("PRAGMA table_info(qb_instances)")
        columns = [row["name"] for row in cursor.fetchall()]
        
        if "retry_count" not in columns:
            conn.execute("ALTER TABLE qb_instances ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 3")

class Database:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(SCHEMA_SQL)
        migrate_add_retry_count(self)
