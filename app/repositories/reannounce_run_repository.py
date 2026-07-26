from __future__ import annotations

from app.db import Database
from app.domain import ReannounceRun
from app.utils import utc_now_iso


class ReannounceRunRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, qb_instance_id: int, trigger_source: str, status: str = "running") -> ReannounceRun:
        now = utc_now_iso()
        with self.database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO reannounce_runs (
                    qb_instance_id, trigger_source, status, started_at, finished_at, torrent_count, error_message
                ) VALUES (?, ?, ?, ?, NULL, 0, NULL)
                """,
                (qb_instance_id, trigger_source, status, now),
            )
            run_id = int(cursor.lastrowid)
        run = self.get(run_id)
        assert run is not None
        return run

    def get(self, run_id: int) -> ReannounceRun | None:
        with self.database.connection() as conn:
            row = conn.execute("SELECT * FROM reannounce_runs WHERE id = ?", (run_id,)).fetchone()
        return self._row_to_run(row) if row else None

    def list_recent(self, limit: int) -> list[ReannounceRun]:
        with self.database.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM reannounce_runs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_run(row) for row in rows]

    def list_by_instance(self, qb_instance_id: int, limit: int) -> list[ReannounceRun]:
        with self.database.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM reannounce_runs WHERE qb_instance_id = ? ORDER BY id DESC LIMIT ?",
                (qb_instance_id, limit),
            ).fetchall()
        return [self._row_to_run(row) for row in rows]

    def count_recent(self, limit: int) -> int:
        with self.database.connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM (SELECT id FROM reannounce_runs ORDER BY id DESC LIMIT ?)",
                (limit,),
            ).fetchone()
        return int(row["count"])

    def mark_finished(self, run_id: int, status: str, torrent_count: int, error_message: str | None = None) -> None:
        now = utc_now_iso()
        with self.database.connection() as conn:
            conn.execute(
                "UPDATE reannounce_runs SET status = ?, finished_at = ?, torrent_count = ?, error_message = ? WHERE id = ?",
                (status, now, torrent_count, error_message, run_id),
            )

    @staticmethod
    def _row_to_run(row) -> ReannounceRun:
        return ReannounceRun(
            id=int(row["id"]),
            qb_instance_id=int(row["qb_instance_id"]),
            trigger_source=row["trigger_source"],
            status=row["status"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            torrent_count=int(row["torrent_count"]),
            error_message=row["error_message"],
        )

    def list_paginated(
        self,
        qb_instance_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ReannounceRun]:
        if qb_instance_id is not None:
            sql = "SELECT * FROM reannounce_runs WHERE qb_instance_id = ? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (qb_instance_id, limit, offset)
        else:
            sql = "SELECT * FROM reannounce_runs ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (limit, offset)
        with self.database.connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_run(row) for row in rows]

    def count(self, qb_instance_id: int | None = None) -> int:
        if qb_instance_id is not None:
            sql = "SELECT COUNT(*) AS count FROM reannounce_runs WHERE qb_instance_id = ?"
            params = (qb_instance_id,)
        else:
            sql = "SELECT COUNT(*) AS count FROM reannounce_runs"
            params = ()
        with self.database.connection() as conn:
            row = conn.execute(sql, params).fetchone()
        return int(row["count"])

    def cleanup_old_runs(self, keep_count: int = 2000) -> int:
        """Delete old runs keeping only the most recent keep_count entries.
        Returns the number of deleted runs."""
        if keep_count <= 0:
            with self.database.connection() as conn:
                cursor = conn.execute("DELETE FROM reannounce_runs")
                return cursor.rowcount

        with self.database.connection() as conn:
            # Get the id threshold - keep the 'keep_count' newest entries
            cursor = conn.execute(
                """
                SELECT id FROM reannounce_runs 
                ORDER BY id DESC 
                LIMIT 1 OFFSET ?
                """,
                (keep_count - 1,)
            )
            row = cursor.fetchone()
            if row is None:
                # Not enough records to need cleanup
                return 0
            
            threshold_id = row["id"]
            
            # Delete records older than the threshold id
            cursor = conn.execute(
                "DELETE FROM reannounce_runs WHERE id < ?",
                (threshold_id,)
            )
            return cursor.rowcount
