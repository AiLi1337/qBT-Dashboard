from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

# Setup logging first
import logging
from logging.handlers import RotatingFileHandler
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Configure root logger with rotation (5 files x 10MB max)
log_handler = RotatingFileHandler(
    log_dir / "app.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
)
logging.basicConfig(
    level=logging.INFO,
    force=True,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        log_handler,
    ]
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response

from app.config import load_settings
from app.container import build_container
from app.routers import api_router, auth_router, pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    container = app.state.container
    container.database.initialize()
    # Cleanup old runs on startup if limit is set
    if container.settings.log_run_limit > 0:
        container.reannounce_run_repository.cleanup_old_runs(container.settings.log_run_limit)
    logger.info("Database initialized")
    
    container.auth_service.ensure_bootstrap_admin(
        container.settings.bootstrap_admin_username,
        container.settings.bootstrap_admin_password,
    )
    logger.info("Bootstrap admin ensured")
    
    if container.settings.scheduler_enabled:
        container.scheduler.start()
        container.scheduler.sync_instances(container.qb_instance_service.list_instances())
        logger.info("Scheduler started")
    
    try:
        yield
    finally:
        logger.info("Application shutting down...")
        if container.settings.scheduler_enabled:
            container.scheduler.shutdown()


def create_app() -> FastAPI:
    logger.info("Creating application...")
    settings = load_settings()
    logger.info(f"Settings loaded: app_name={settings.app_name}")
    
    container = build_container(settings)
    logger.info("Container built")
    
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.container = container
    
    static_dir = Path(__file__).resolve().parent / "static"
    if not static_dir.exists():
        logger.warning(f"Static directory not found: {static_dir}")
        static_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Mounting static files from: {static_dir}")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Add exception handler for better error reporting
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
                    content={"detail": "服务器内部错误", "type": "InternalError"}
        )
    
    # Security headers middleware
    @app.middleware('http')
    async def add_security_headers(request: Request, call_next):
        response: Response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        return response
    
    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(pages_router)
    logger.info("Routers included")
    
    logger.info("Application created successfully")
    return app


app = create_app()
