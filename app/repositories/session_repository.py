from __future__ import annotations

from typing import Optional

from app.db import Database
from app.domain import Session
from app.utils import utc_now_iso


class SessionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, session: Session) -> None:
        with self.database.connection() as conn:
            conn.execute(
                "INSERT INTO sessions (session_id, user_id, csrf_token, created_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (
                    session.session_id,
                    session.user_id,
                    session.csrf_token,
                    session.created_at,
                    session.expires_at,
                ),
            )

    def get(self, session_id: str) -> Optional[Session]:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT session_id, user_id, csrf_token, created_at, expires_at FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return self._row_to_session(row) if row else None

    def delete(self, session_id: str) -> None:
        with self.database.connection() as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    def delete_expired(self) -> None:
        now = utc_now_iso()
        with self.database.connection() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))

    @staticmethod
    def _row_to_session(row) -> Session:
        return Session(
            session_id=row["session_id"],
            user_id=int(row["user_id"]),
            csrf_token=row["csrf_token"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )
