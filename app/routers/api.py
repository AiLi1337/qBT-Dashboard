from __future__ import annotations
import logging
import re


def _is_valid_hash(h: str) -> bool:
    """Validate torrent hash is 40-char hex."""
    return bool(re.fullmatch(r"^[0-9a-fA-F]{40}$", h))

from fastapi import APIRouter, HTTPException, Request, status

from app.deps import get_container, get_current_session, require_csrf
from app.routers.auth import _check_rate_limit
from app.schemas import (
    AddTorrentRequest,
    BatchHashesRequest,
    DashboardSummary,
    QBConnectionStatus,
    QBInstanceCreate,
    QBInstanceUpdate,
    QBInstanceView,
    ReannounceRunView,
    TorrentSummaryView,
    TransferInfo,
)
from app.services import AuthError, QBInstanceServiceError

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)


def _authenticated(request: Request):
    try:
        return get_current_session(request)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def _csrf(request: Request):
    session_context = _authenticated(request)
    try:
        require_csrf(request, session_context)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return session_context


@router.get("/summary", response_model=DashboardSummary)
def summary(request: Request):
    _ = _authenticated(request)
    container = get_container(request)
    stats = container.qb_instance_service.dashboard_stats()
    return DashboardSummary(
        total_instances=stats.total_instances,
        enabled_instances=stats.enabled_instances,
        recent_runs=stats.recent_runs,
    )


@router.get("/instances", response_model=list[QBInstanceView])
def list_instances(request: Request):
    _ = _authenticated(request)
    container = get_container(request)
    return container.qb_instance_service.list_instances()


@router.post("/instances", response_model=QBInstanceView, status_code=status.HTTP_201_CREATED)
def create_instance(request: Request, payload: QBInstanceCreate):
    _csrf(request)
    container = get_container(request)
    try:
        instance = container.qb_instance_service.create_instance(payload)
    except QBInstanceServiceError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if container.settings.scheduler_enabled:
        container.scheduler.upsert_instance(instance)
    return instance


@router.patch("/instances/{instance_id}", response_model=QBInstanceView)
def update_instance(request: Request, instance_id: int, payload: QBInstanceUpdate):
    _csrf(request)
    container = get_container(request)
    try:
        instance = container.qb_instance_service.update_instance(instance_id, payload)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if container.settings.scheduler_enabled:
        container.scheduler.upsert_instance(instance)
    return instance


@router.delete("/instances/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instance(request: Request, instance_id: int):
    _csrf(request)
    container = get_container(request)
    try:
        deleted = container.qb_instance_service.delete_instance(instance_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实例未找到")
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if container.settings.scheduler_enabled:
        container.scheduler.remove_job(container.scheduler.job_id(instance_id))


@router.post("/instances/{instance_id}/test-connection", response_model=QBConnectionStatus)
async def test_connection(request: Request, instance_id: int):
    _csrf(request)
    _check_rate_limit(request, "test-connection", max_requests=5, window_seconds=60)
    container = get_container(request)
    try:
        return await container.qb_instance_service.test_connection(instance_id)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/instances/{instance_id}/run-now")
async def run_now(request: Request, instance_id: int):
    _csrf(request)
    _check_rate_limit(request, "run-now", max_requests=5, window_seconds=60)
    container = get_container(request)
    try:
        outcome = await container.qb_instance_service.run_reannounce(instance_id, "manual")
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "status": "succeeded",
        "torrent_count": outcome.torrent_count,
        "app_version": outcome.app_version,
        "webapi_version": outcome.webapi_version,
    }


@router.post("/instances/{instance_id}/recheck")
async def recheck_torrents(request: Request, instance_id: int):
    """Trigger recheck for all torrents in an instance to trigger completion events."""
    _csrf(request)
    _check_rate_limit(request, "recheck", max_requests=5, window_seconds=60)
    container = get_container(request)
    try:
        count = await container.qb_instance_service.recheck_all(instance_id)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "status": "succeeded",
        "torrent_count": count,
    }


@router.get("/instances/{instance_id}/runs", response_model=list[ReannounceRunView])
def list_instance_runs(request: Request, instance_id: int):
    _ = _authenticated(request)
    container = get_container(request)
    try:
        container.qb_instance_service.get_instance(instance_id)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return container.qb_instance_service.list_runs(instance_id)


@router.get("/instances/{instance_id}/torrents", response_model=list[dict])
async def list_torrents(request: Request, instance_id: int):
    """Get all torrents from an instance."""
    _ = _authenticated(request)
    _check_rate_limit(request, f"list-torrents:{instance_id}", max_requests=12, window_seconds=60)
    container = get_container(request)
    try:
        torrents = await container.qb_instance_service.get_torrents(instance_id)
        logger.info("list_torrents: instance_id=%s count=%s", instance_id, len(torrents))
        return torrents
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/instances/{instance_id}/torrents/summary", response_model=TorrentSummaryView)
async def get_torrent_summary(request: Request, instance_id: int):
    """Get torrent summary for an instance."""
    _ = _authenticated(request)
    _check_rate_limit(request, f"torrent-summary:{instance_id}", max_requests=12, window_seconds=60)
    container = get_container(request)
    try:
        summary = await container.qb_instance_service.get_torrent_summary(instance_id)
        return TorrentSummaryView(
            total_count=summary.total_count,
            downloading=summary.downloading,
            seeding=summary.seeding,
            paused=summary.paused,
            checking=summary.checking,
            error=summary.error,
            total_downloaded=summary.total_downloaded,
            total_uploaded=summary.total_uploaded,
        )
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/instances/{instance_id}/torrents/{torrent_hash}/properties")
async def get_torrent_properties(request: Request, instance_id: int, torrent_hash: str):
    """Get detailed properties for a specific torrent."""
    _ = _authenticated(request)
    container = get_container(request)
    try:
        properties = await container.qb_instance_service.get_torrent_properties(instance_id, torrent_hash)
        return properties
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/instances/{instance_id}/torrents/{torrent_hash}/reannounce")
async def reannounce_torrent(request: Request, instance_id: int, torrent_hash: str):
    _csrf(request)
    container = get_container(request)
    if not _is_valid_hash(torrent_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid torrent hash format")
    try:
        await container.qb_instance_service.reannounce_one(instance_id, torrent_hash)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "succeeded"}

@router.post("/instances/{instance_id}/torrents/{torrent_hash}/recheck")
async def recheck_torrent(request: Request, instance_id: int, torrent_hash: str):
    _csrf(request)
    container = get_container(request)
    if not _is_valid_hash(torrent_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid torrent hash format")
    try:
        await container.qb_instance_service.recheck_one(instance_id, torrent_hash)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "succeeded"}

@router.post("/instances/{instance_id}/torrents/reannounce-batch")
async def reannounce_torrents_batch(request: Request, instance_id: int, payload: BatchHashesRequest):
    _csrf(request)
    container = get_container(request)
    try:
        count = await container.qb_instance_service.reannounce_batch(instance_id, payload.hashes)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "succeeded", "torrent_count": count}

@router.get("/instances/{instance_id}/transfer-info", response_model=TransferInfo)
async def get_transfer_info(request: Request, instance_id: int):
    """Get global transfer (DL/UP) info from qBittorrent instance."""
    _ = _authenticated(request)
    container = get_container(request)
    try:
        info = await container.qb_instance_service.get_transfer_info(instance_id)
        return info
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/instances/{instance_id}/torrents/add")
async def add_torrent(request: Request, instance_id: int, payload: AddTorrentRequest):
    """Add a torrent to a qBittorrent instance."""
    _csrf(request)
    container = get_container(request)
    try:
        result = await container.qb_instance_service.add_torrent(
            instance_id, payload.urls, payload.savepath,
            payload.upload_limit_speed, payload.download_limit_speed
        )
        return {"status": result or "Ok."}
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.post("/instances/{instance_id}/torrents/recheck-batch")
async def recheck_torrents_batch(request: Request, instance_id: int, payload: BatchHashesRequest):
    _csrf(request)
    container = get_container(request)
    try:
        count = await container.qb_instance_service.recheck_batch(instance_id, payload.hashes)
    except QBInstanceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"status": "succeeded", "torrent_count": count}
