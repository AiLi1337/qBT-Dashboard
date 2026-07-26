from __future__ import annotations

from fastapi import Request

from app.container import AppContainer
from app.domain import SessionContext
from app.services import AuthError


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_current_session(request: Request) -> SessionContext:
    container = get_container(request)
    signed_session = request.cookies.get(container.settings.session_cookie_name)
    return container.auth_service.authenticate(signed_session)


def require_csrf(request: Request, session_context: SessionContext, form_csrf_token: str = "") -> None:
    container = get_container(request)
    csrf_header = request.headers.get("X-CSRF-Token") or form_csrf_token or None
    csrf_cookie = request.cookies.get(container.settings.csrf_cookie_name)
    container.auth_service.verify_csrf(session_context, csrf_header, csrf_cookie)


def template_context(request: Request, session_context: SessionContext | None = None, **extra):
    container = get_container(request)
    
    # Build base context - ensure all values are simple types
    current_user = None
    csrf_token = ""
    
    if session_context is not None:
        # Safely extract user and session info
        if session_context.user is not None:
            current_user = session_context.user
        if hasattr(session_context, 'session') and session_context.session is not None:
            csrf_token = getattr(session_context.session, 'csrf_token', "") or ""
    
    context = {
        "request": request,
        "app_name": container.settings.app_name,
        "current_user": current_user,
        "csrf_token": csrf_token,
    }
    
    # Add extra context - filter out None values for safety
    for key, value in extra.items():
        if value is not None:
            context[key] = value
    
    return context
