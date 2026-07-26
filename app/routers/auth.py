from __future__ import annotations

import time
import threading

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.deps import get_container, get_current_session, require_csrf
from app.services import AuthError

# ponytail: in-memory rate limiter, per-IP, 5 attempts per 60s window
_login_attempts: dict = {}  # ponytail: plain dict, cleaned on each access
_login_lock = threading.Lock()
_last_cleanup: float = 0.0
CLEANUP_INTERVAL = 300
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60


def _cleanup_rate_limits(now: float, window_seconds: int) -> None:
    global _last_cleanup
    if now - _last_cleanup <= CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    stale_keys = [
        key for key, attempts in _login_attempts.items()
        if not attempts or all(now - t >= window_seconds for t in attempts)
    ]
    for key in stale_keys:
        del _login_attempts[key]


def _check_rate_limit(request: Request, endpoint: str, max_requests: int = 5, window_seconds: int = 60):
    """ponytail: shared in-memory rate limiter, per-IP+endpoint.
    Uses the socket peer, not X-Forwarded-For — XFF is spoofable by any client."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{endpoint}"
    now = time.time()
    with _login_lock:
        _cleanup_rate_limits(now, window_seconds)
        attempts = _login_attempts.get(key, [])
        attempts = [t for t in attempts if now - t < window_seconds]
        if attempts:
            _login_attempts[key] = attempts
        elif key in _login_attempts:
            del _login_attempts[key]
        if len(attempts) >= max_requests:
            raise HTTPException(status_code=429, detail="Too many requests, please try again later")
        _login_attempts.setdefault(key, []).append(now)

router = APIRouter()


@router.post("/auth/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    _check_rate_limit(request, "login", max_requests=LOGIN_RATE_LIMIT, window_seconds=LOGIN_RATE_WINDOW)

    container = get_container(request)
    try:
        session_context, signed_session = container.auth_service.login(username, password)
    except AuthError as exc:
        from urllib.parse import quote
        response = RedirectResponse(f"/login?error={quote(str(exc))}", status_code=status.HTTP_303_SEE_OTHER)
        return response

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        container.settings.session_cookie_name,
        signed_session,
        httponly=True,
        samesite="lax",
        secure=container.settings.secure_cookies,
        max_age=container.settings.session_ttl_hours * 3600,
    )
    response.set_cookie(
        container.settings.csrf_cookie_name,
        session_context.session.csrf_token,
        httponly=False,
        samesite="lax",
        secure=container.settings.secure_cookies,
        max_age=container.settings.session_ttl_hours * 3600,
    )
    return response


@router.post("/auth/logout")
def logout(request: Request, csrf_token: str = Form("")):
    container = get_container(request)
    signed_session = request.cookies.get(container.settings.session_cookie_name)
    try:
        session_context = get_current_session(request)
        require_csrf(request, session_context, form_csrf_token=csrf_token)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    container.auth_service.logout(signed_session)

    redirect = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(container.settings.session_cookie_name)
    redirect.delete_cookie(container.settings.csrf_cookie_name)
    return redirect


@router.get("/auth/me")
def me(request: Request):
    try:
        session_context = get_current_session(request)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return {"username": session_context.user.username}
