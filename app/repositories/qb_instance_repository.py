from __future__ import annotations

from typing import Optional

from app.db import Database
from app.domain import QBInstance
from app.schemas import QBInstanceCreate, QBInstanceUpdate
from app.utils import utc_now_iso


class QBInstanceRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list_all(self) -> list[QBInstance]:
        with self.database.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM qb_instances ORDER BY id ASC"
            ).fetchall()
        return [self._row_to_instance(row) for row in rows]

    def get(self, instance_id: int) -> Optional[QBInstance]:
        with self.database.connection() as conn:
            row = conn.execute("SELECT * FROM qb_instances WHERE id = ?", (instance_id,)).fetchone()
        return self._row_to_instance(row) if row else None

    def create(self, payload: QBInstanceCreate, encrypted_password: str) -> QBInstance:
        now = utc_now_iso()
        with self.database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO qb_instances (
                    name, base_url, username, encrypted_password, verify_tls, enabled,
                    reannounce_enabled, interval_minutes, request_timeout_seconds, retry_count,
                    app_version, webapi_version, last_status, last_error_message,
                    last_checked_at, last_run_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, ?, ?)
                """,
                (
                    payload.name,
                    payload.base_url,
                    payload.username,
                    encrypted_password,
                    int(payload.verify_tls),
                    int(payload.enabled),
                    int(payload.reannounce_enabled),
                    payload.interval_minutes,
                    payload.request_timeout_seconds,
                    payload.retry_count,
                    now,
                    now,
                ),
            )
            instance_id = int(cursor.lastrowid)
        instance = self.get(instance_id)
        assert instance is not None
        return instance

    def update(self, instance_id: int, payload: QBInstanceUpdate, encrypted_password: str | None = None) -> Optional[QBInstance]:
        current = self.get(instance_id)
        if current is None:
            return None

        values = {
            "name": payload.name if payload.name is not None else current.name,
            "base_url": payload.base_url if payload.base_url is not None else current.base_url,
            "username": payload.username if payload.username is not None else current.username,
            "encrypted_password": encrypted_password if encrypted_password is not None else current.encrypted_password,
            "verify_tls": int(payload.verify_tls if payload.verify_tls is not None else current.verify_tls),
            "enabled": int(payload.enabled if payload.enabled is not None else current.enabled),
            "reannounce_enabled": int(payload.reannounce_enabled if payload.reannounce_enabled is not None else current.reannounce_enabled),
            "interval_minutes": payload.interval_minutes if payload.interval_minutes is not None else current.interval_minutes,
            "request_timeout_seconds": payload.request_timeout_seconds if payload.request_timeout_seconds is not None else current.request_timeout_seconds,
            "retry_count": payload.retry_count if payload.retry_count is not None else current.retry_count,
            "updated_at": utc_now_iso(),
            "id": instance_id,
        }
        with self.database.connection() as conn:
            conn.execute(
                """
                UPDATE qb_instances SET
                    name = :name,
                    base_url = :base_url,
                    username = :username,
                    encrypted_password = :encrypted_password,
                    verify_tls = :verify_tls,
                    enabled = :enabled,
                    reannounce_enabled = :reannounce_enabled,
                    interval_minutes = :interval_minutes,
                    request_timeout_seconds = :request_timeout_seconds,
                    retry_count = :retry_count,
                    updated_at = :updated_at
                WHERE id = :id
                """,
                values,
            )
        return self.get(instance_id)

    def update_probe_result(
        self,
        instance_id: int,
        *,
        last_status: str,
        last_error_message: str | None,
        app_version: str | None,
        webapi_version: str | None,
    ) -> None:
        now = utc_now_iso()
        with self.database.connection() as conn:
            conn.execute(
                """
                UPDATE qb_instances SET
                    app_version = ?,
                    webapi_version = ?,
                    last_status = ?,
                    last_error_message = ?,
                    last_checked_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (app_version, webapi_version, last_status, last_error_message, now, now, instance_id),
            )

    def mark_run_completed(
        self,
        instance_id: int,
        *,
        last_status: str,
        last_error_message: str | None,
        app_version: str | None,
        webapi_version: str | None,
    ) -> None:
        now = utc_now_iso()
        with self.database.connection() as conn:
            conn.execute(
                """
                UPDATE qb_instances SET
                    app_version = ?,
                    webapi_version = ?,
                    last_status = ?,
                    last_error_message = ?,
                    last_checked_at = ?,
                    last_run_at = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (app_version, webapi_version, last_status, last_error_message, now, now, now, instance_id),
            )

    def delete(self, instance_id: int) -> bool:
        with self.database.connection() as conn:
            cursor = conn.execute("DELETE FROM qb_instances WHERE id = ?", (instance_id,))
        return cursor.rowcount > 0

    def _row_to_instance(self, row) -> QBInstance:
        return QBInstance(
            id=int(row["id"]),
            name=row["name"],
            base_url=row["base_url"],
            username=row["username"],
            encrypted_password=row["encrypted_password"],
            verify_tls=bool(row["verify_tls"]),
            enabled=bool(row["enabled"]),
            reannounce_enabled=bool(row["reannounce_enabled"]),
            interval_minutes=int(row["interval_minutes"]),
            request_timeout_seconds=int(row["request_timeout_seconds"]),
            retry_count=int(row["retry_count"]) if row["retry_count"] is not None else 3,
            app_version=row["app_version"],
            webapi_version=row["webapi_version"],
            last_status=row["last_status"],
            last_error_message=row["last_error_message"],
            last_checked_at=row["last_checked_at"],
            last_run_at=row["last_run_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
