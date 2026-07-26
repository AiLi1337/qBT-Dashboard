from __future__ import annotations

from app.routers.api import router as api_router
from app.routers.auth import router as auth_router
from app.routers.pages import router as pages_router

__all__ = ["api_router", "auth_router", "pages_router"]
