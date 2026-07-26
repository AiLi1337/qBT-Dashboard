from __future__ import annotations

import os
import sys
import logging
import threading
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

from cryptography.fernet import Fernet


class SettingsError(RuntimeError):
    """Raised when required application settings are missing or invalid."""


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_path: Path
    app_secret_key: str
    app_encryption_key: str
    bootstrap_admin_username: str
    bootstrap_admin_password: str
    session_cookie_name: str = "qbpanel_session"
    csrf_cookie_name: str = "qbpanel_csrf"
    session_ttl_hours: int = 12
    secure_cookies: bool = False
    scheduler_enabled: bool = True
    log_run_limit: int = 2000

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"


def _get_project_root() -> Path:
    """Get the project root directory."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.resolve().parent


def _load_dotenv_file() -> None:
    """Load environment variables from .env file."""
    project_root = _get_project_root()
    dotenv_path = project_root / ".env"
    
    logger.info(f"Looking for .env file at: {dotenv_path}")
    
    if not dotenv_path.exists():
        logger.warning(f".env file not found at {dotenv_path}")
        return
    
    logger.info(f"Loading .env file: {dotenv_path}")
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())
        logger.debug(f"Loaded env: {key.strip()}")


def _read_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        raise SettingsError(f"Missing required environment variable: {name}")
    return value


def _read_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        logger.warning(f"Invalid integer for {name}: {raw}, using default {default}")
        return default


def _get_default_database_path() -> Path:
    """Get the default database path - use project directory for simplicity."""
    project_root = _get_project_root()
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "app.db"


_settings_cache: Settings | None = None
_settings_lock = threading.Lock()

def load_settings() -> Settings:
    global _settings_cache
    with _settings_lock:
        if _settings_cache is not None:
            return _settings_cache
        _load_dotenv_file()
        # Get database path from env or use default project-relative path
        database_path_str = os.getenv("DATABASE_PATH", "").strip()
        if database_path_str:
            database_path = Path(database_path_str).expanduser()
            if not database_path.is_absolute():
                database_path = _get_project_root() / database_path
        else:
            database_path = _get_default_database_path()

        # Ensure the directory exists
        database_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database path: {database_path}")

        encryption_key = _read_required_env("APP_ENCRYPTION_KEY")
        try:
            Fernet(encryption_key.encode("utf-8"))
        except Exception as exc:
            logger.error(f"Invalid Fernet key: {exc}")
            raise SettingsError("APP_ENCRYPTION_KEY must be a valid Fernet key") from exc

        settings = Settings(
            app_name=os.getenv("APP_NAME", "qBittorrent 管理面板"),
            database_path=database_path,
            app_secret_key=_read_required_env("APP_SECRET_KEY"),
            app_encryption_key=encryption_key,
            bootstrap_admin_username=_read_required_env("BOOTSTRAP_ADMIN_USERNAME"),
            bootstrap_admin_password=_read_required_env("BOOTSTRAP_ADMIN_PASSWORD"),
            session_cookie_name=os.getenv("SESSION_COOKIE_NAME", "qbpanel_session"),
            csrf_cookie_name=os.getenv("CSRF_COOKIE_NAME", "qbpanel_csrf"),
            session_ttl_hours=_read_int_env("SESSION_TTL_HOURS", 12),
            secure_cookies=_read_bool_env("SECURE_COOKIES", False),
            scheduler_enabled=_read_bool_env("SCHEDULER_ENABLED", True),
            log_run_limit=_read_int_env("LOG_RUN_LIMIT", 2000),
        )

        logger.info(f"Settings loaded successfully: app_name={settings.app_name}")
        _settings_cache = settings
    return settings

def reset_settings_cache() -> None:
    """Clear cached settings so next load_settings() re-reads environment."""
    global _settings_cache
    with _settings_lock:
        _settings_cache = None
