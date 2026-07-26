from __future__ import annotations

import asyncio
import pytest

from app.domain import QBInstance
from app.scheduler import ReannounceScheduler


class DummyService:
    async def run_reannounce(self, instance_id: int, trigger_source: str):
        return None


def make_instance(instance_id: int, enabled: bool = True, reannounce_enabled: bool = True, interval_minutes: int = 60):
    return QBInstance(
        id=instance_id,
        name=f"qb-{instance_id}",
        base_url="http://127.0.0.1:8080",
        username="admin",
        encrypted_password="encrypted",
        verify_tls=True,
        enabled=enabled,
        reannounce_enabled=reannounce_enabled,
        interval_minutes=interval_minutes,
        request_timeout_seconds=15,
        retry_count=3,
        app_version=None,
        webapi_version=None,
        last_status=None,
        last_error_message=None,
        last_checked_at=None,
        last_run_at=None,
        created_at="2024-01-01T00:00:00+00:00",
        updated_at="2024-01-01T00:00:00+00:00",
    )


@pytest.mark.asyncio
async def test_scheduler_registers_and_removes_jobs():
    scheduler = ReannounceScheduler(DummyService())
    scheduler.start()
    try:
        scheduler.upsert_instance(make_instance(1, enabled=True, reannounce_enabled=True, interval_minutes=30))
        assert scheduler.scheduler.get_job("qb-instance-1") is not None

        scheduler.upsert_instance(make_instance(1, enabled=False, reannounce_enabled=True, interval_minutes=30))
        assert scheduler.scheduler.get_job("qb-instance-1") is None
    finally:
        scheduler.shutdown()


@pytest.mark.asyncio
async def test_scheduler_sync_instances_rebuilds_expected_jobs():
    scheduler = ReannounceScheduler(DummyService())
    scheduler.start()
    try:
        scheduler.sync_instances([
            make_instance(1, enabled=True, reannounce_enabled=True),
            make_instance(2, enabled=True, reannounce_enabled=False),
        ])
        assert scheduler.scheduler.get_job("qb-instance-1") is not None
        assert scheduler.scheduler.get_job("qb-instance-2") is None
    finally:
        scheduler.shutdown()
