from __future__ import annotations

import math
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.deps import get_container, get_current_session, template_context
from app.services import AuthError, QBInstanceServiceError

router = APIRouter()


def _page_session_or_redirect(request: Request):
    try:
        return get_current_session(request)
    except AuthError:
        return None


def format_size(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    if bytes_value == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_value, 1024)))
    size = bytes_value / (1024 ** i)
    return f"{size:.1f} {units[i]}"


@router.get("/")
def dashboard(request: Request):
    """Dashboard home page."""
    session_context = _page_session_or_redirect(request)
    if session_context is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    container = get_container(request)
    stats = container.qb_instance_service.dashboard_stats()
    instances = container.qb_instance_service.list_instances()
    recent_runs = (container.qb_instance_service.list_runs() or [])[:10]

    return container.templates.TemplateResponse(
        "dashboard.html",
        template_context(
            request,
            session_context,
            stats=stats,
            instances=instances,
            recent_runs=recent_runs,
        ),
    )


@router.get("/login")
def login_page(request: Request, error: str = ""):
    """Login page."""
    session_context = _page_session_or_redirect(request)
    if session_context is not None:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    container = get_container(request)
    return container.templates.TemplateResponse(
        "login.html",
        template_context(
            request,
            None,
            error=error,
        ),
    )


@router.get("/instances")
def instances_page(request: Request):
    """Instances management page."""
    session_context = _page_session_or_redirect(request)
    if session_context is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    container = get_container(request)
    instances = container.qb_instance_service.list_instances()

    return container.templates.TemplateResponse(
        "instances.html",
        template_context(
            request,
            session_context,
            instances=instances,
        ),
    )



@router.get("/runs")
def runs_page(request: Request, page: int = 1, page_size: int = 100, instance_id: int | None = None):
    """Run logs page with pagination."""
    session_context = _page_session_or_redirect(request)
    if session_context is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    container = get_container(request)
    instances_list = container.qb_instance_service.list_instances()
    instances = {inst.id: inst for inst in instances_list}

    if instance_id is not None and instance_id not in instances:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="实例不存在")

    page_size = max(10, min(page_size, 200))
    runs, total = container.qb_instance_service.list_runs_paginated(instance_id, page, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)

    return container.templates.TemplateResponse(
        "runs.html",
        template_context(
            request,
            session_context,
            runs=runs,
            instances=instances,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            filter_instance_id=instance_id,
        ),
    )


@router.get("/instances/{instance_id}")
async def instance_detail(request: Request, instance_id: int):
    session_context = _page_session_or_redirect(request)
    if session_context is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    
    container = get_container(request)
    
    try:
        instance = container.qb_instance_service.get_instance(instance_id)
    except QBInstanceServiceError:
        return RedirectResponse("/instances", status_code=status.HTTP_303_SEE_OTHER)
    
    torrent_error = None
    try:
        torrents = await container.qb_instance_service.get_torrents(instance_id)
    except QBInstanceServiceError as exc:
        torrents = []
        torrent_error = str(exc)
    
    for t in torrents:
        t["size_formatted"] = format_size(t.get("size", 0))
        t["downloaded_formatted"] = format_size(t.get("downloaded", 0))
        t["uploaded_formatted"] = format_size(t.get("uploaded", 0))
        t["progress_pct"] = int(t.get("progress", 0) * 100)
        t["dlspeed_formatted"] = format_size(t.get("dlspeed", 0)) + "/s"
        t["upspeed_formatted"] = format_size(t.get("upspeed", 0)) + "/s"
    
    return container.templates.TemplateResponse(
        "instance_detail.html",
        template_context(
            request,
            session_context,
            instance=instance,
            torrents=torrents,
            torrent_error=torrent_error if torrent_error else None,
        ),
    )
