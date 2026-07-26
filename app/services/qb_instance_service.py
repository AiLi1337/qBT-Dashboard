from __future__ import annotations

import asyncio
from typing import Optional, Any, Dict, List
from dataclasses import dataclass

from app.clients import QBAuthError, QBClient, QBClientError, QBCompatibilityError
from app.domain import QBConnectionProbe, QBInstance, ReannounceOutcome, ReannounceRun
from app.repositories import QBInstanceRepository, ReannounceRunRepository
from app.schemas import QBInstanceCreate, QBInstanceUpdate
from app.security import SecretCipher


class QBInstanceServiceError(RuntimeError):
    pass


@dataclass(slots=True)
class DashboardStats:
    total_instances: int
    enabled_instances: int
    recent_runs: int


@dataclass(slots=True)
class TorrentSummary:
    """Summary of torrents for an instance."""
    total_count: int
    downloading: int
    seeding: int
    paused: int
    checking: int
    error: int
    total_downloaded: int
    total_uploaded: int


class QBInstanceService:
    def __init__(
        self,
        instance_repository: QBInstanceRepository,
        run_repository: ReannounceRunRepository,
        secret_cipher: SecretCipher,
        log_run_limit: int,
    ) -> None:
        self.instance_repository = instance_repository
        self.run_repository = run_repository
        self.secret_cipher = secret_cipher
        self.log_run_limit = log_run_limit

    def list_instances(self) -> list[QBInstance]:
        return self.instance_repository.list_all()

    def get_instance(self, instance_id: int) -> QBInstance:
        instance = self.instance_repository.get(instance_id)
        if instance is None:
            raise QBInstanceServiceError("Instance not found")
        return instance

    def create_instance(self, payload: QBInstanceCreate) -> QBInstance:
        encrypted_password = self.secret_cipher.encrypt(payload.password)
        try:
            return self.instance_repository.create(payload, encrypted_password)
        except Exception as exc:
            raise QBInstanceServiceError(f"Failed to create instance: {exc}") from exc

    def update_instance(self, instance_id: int, payload: QBInstanceUpdate) -> QBInstance:
        encrypted_password = self.secret_cipher.encrypt(payload.password) if payload.password else None
        try:
            instance = self.instance_repository.update(instance_id, payload, encrypted_password)
        except Exception as exc:
            raise QBInstanceServiceError(f"Failed to update instance: {exc}") from exc
        if instance is None:
            raise QBInstanceServiceError("Instance not found")
        return instance


    def delete_instance(self, instance_id: int) -> bool:
        try:
            return self.instance_repository.delete(instance_id)
        except Exception as exc:
            raise QBInstanceServiceError(f"Failed to delete instance: {exc}") from exc
    def dashboard_stats(self) -> DashboardStats:
        instances = self.instance_repository.list_all()
        return DashboardStats(
            total_instances=len(instances),
            enabled_instances=sum(1 for item in instances if item.enabled),
            recent_runs=self.run_repository.count_recent(self.log_run_limit),
        )

    def list_runs(self, instance_id: int | None = None) -> list[ReannounceRun]:
        if instance_id is None:
            return self.run_repository.list_recent(self.log_run_limit)
        return self.run_repository.list_by_instance(instance_id, self.log_run_limit)

    def list_runs_paginated(
        self,
        instance_id: int | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[ReannounceRun], int]:
        offset = (page - 1) * page_size
        return (
            self.run_repository.list_paginated(instance_id, page_size, offset),
            self.run_repository.count(instance_id),
        )

    async def test_connection(self, instance_id: int) -> QBConnectionProbe:
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            try:
                probe = await client.probe()
            except Exception as exc:
                import logging
                _log = logging.getLogger("app.services.qb_instance_service")
                _log.warning("test_connection probe failed: %s", exc)
                raise QBInstanceServiceError(f"Connection test failed: {exc}") from exc
        finally:
            await client.close()

        probe_is_ok = probe.reachable and probe.authenticated and probe.app_version is not None
        last_status = "ok" if probe_is_ok else "error"
        self.instance_repository.update_probe_result(
            instance.id,
            last_status=last_status,
            last_error_message=None if probe_is_ok else probe.message,
            app_version=probe.app_version,
            webapi_version=probe.webapi_version,
        )
        return probe

    async def get_torrents(self, instance_id: int) -> List[Dict[str, Any]]:
        """Get all torrents from an instance."""
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            torrents = await client.get_torrents()
            return torrents
        finally:
            await client.close()

    async def get_torrent_summary(self, instance_id: int) -> TorrentSummary:
        """Get a summary of torrents grouped by state."""
        torrents = await self.get_torrents(instance_id)
        
        # Group by state
        states = {
            "downloading": 0,
            "seeding": 0,
            "paused": 0,
            "checking": 0,
            "error": 0,
        }
        for t in torrents:
            state = t.get("state", "")
            if state in ("downloading", "forcedDL"):
                states["downloading"] += 1
            elif state in ("seeding", "forcedUP"):
                states["seeding"] += 1
            elif state in ("pausedDL", "pausedUP"):
                states["paused"] += 1
            elif state in ("checkingDL", "checkingUP", "checkingResumeData"):
                states["checking"] += 1
            elif state == "error":
                states["error"] += 1

        return TorrentSummary(
            total_count=len(torrents),
            **states,
            total_downloaded=sum(t.get("downloaded", 0) for t in torrents),
            total_uploaded=sum(t.get("uploaded", 0) for t in torrents),
        )

    async def get_torrent_properties(self, instance_id: int, torrent_hash: str) -> dict:
        """Get properties for a specific torrent."""
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            properties = await client.get_torrent_properties(torrent_hash)
            return properties
        finally:
            await client.close()

    async def run_reannounce(self, instance_id: int, trigger_source: str) -> ReannounceOutcome:
        instance = self.get_instance(instance_id)
        run = self.run_repository.create(instance.id, trigger_source)
        
        # Cleanup old runs if we have too many logs
        if self.log_run_limit > 0:
            self.run_repository.cleanup_old_runs(self.log_run_limit)
        
        retry_count = instance.retry_count if instance.retry_count is not None else 3
        last_error = None
        
        client = QBClient(instance, self.secret_cipher)
        try:
            for attempt in range(1, retry_count + 1):
                try:
                    outcome = await client.reannounce_all()
                    # Success!
                    self.run_repository.mark_finished(run.id, 'succeeded', outcome.torrent_count, None)
                    self.instance_repository.mark_run_completed(
                        instance.id,
                        last_status='ok',
                        last_error_message=None,
                        app_version=outcome.app_version,
                        webapi_version=outcome.webapi_version,
                    )
                    return outcome
                except (QBAuthError, QBCompatibilityError, QBClientError) as exc:
                    last_error = str(exc)
                    if attempt < retry_count:
                        await asyncio.sleep(1)
                        continue
                except Exception as exc:
                    last_error = f'Failed to run reannounce: {exc}'
                    if attempt < retry_count:
                        await asyncio.sleep(1)
                        continue
            
            # All retries exhausted
            self.run_repository.mark_finished(run.id, 'failed', 0, last_error)
            self.instance_repository.mark_run_completed(
                instance.id,
                last_status='error',
                last_error_message=last_error,
                app_version=None,
                webapi_version=None,
            )
            raise QBInstanceServiceError(last_error)
        finally:
            await client.close()
    async def recheck_all(self, instance_id: int) -> int:
        """Trigger recheck for all torrents in an instance."""
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            count = await client.recheck_all()
            return count
        finally:
            await client.close()

    async def reannounce_one(self, instance_id: int, torrent_hash: str) -> None:
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            await client.reannounce_one(torrent_hash)
        finally:
            await client.close()

    async def recheck_one(self, instance_id: int, torrent_hash: str) -> None:
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            await client.recheck_one(torrent_hash)
        finally:
            await client.close()

    async def reannounce_batch(self, instance_id: int, torrent_hashes: list[str]) -> int:
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            return await client.reannounce_batch(torrent_hashes)
        finally:
            await client.close()



    async def get_transfer_info(self, instance_id: int) -> dict:
        """Get global transfer info from an instance."""
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            info = await client.get_transfer_info()
            return info
        finally:
            await client.close()

    async def add_torrent(self, instance_id: int, urls: str, savepath: str,
                          upload_limit_mib: float = 80.0, download_limit_mib: float = 80.0) -> str:
        upload_limit_b = int(round(upload_limit_mib * 1024 * 1024))
        download_limit_b = int(round(download_limit_mib * 1024 * 1024))
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            result = await client.add_torrent(urls, savepath, upload_limit_b, download_limit_b)
            return result
        finally:
            await client.close()
    async def recheck_batch(self, instance_id: int, torrent_hashes: list[str]) -> int:
        instance = self.get_instance(instance_id)
        client = QBClient(instance, self.secret_cipher)
        try:
            return await client.recheck_batch(torrent_hashes)
        finally:
            await client.close()
