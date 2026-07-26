from __future__ import annotations

from typing import Optional

from app.db import Database
from app.domain import User
from app.utils import utc_now_iso


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_by_username(self, username: str) -> Optional[User]:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, created_at, updated_at FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, created_at, updated_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return self._row_to_user(row) if row else None

    def count(self) -> int:
        with self.database.connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return int(row["count"])

    def create(self, username: str, password_hash: str) -> User:
        now = utc_now_iso()
        with self.database.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (username, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, now, now),
            )
            user_id = cursor.lastrowid
        user = self.get_by_id(int(user_id))
        assert user is not None
        return user

    @staticmethod
    def _row_to_user(row) -> User:
        return User(
            id=int(row["id"]),
            username=row["username"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
