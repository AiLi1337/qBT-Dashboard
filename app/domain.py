from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class User:
    id: int
    username: str
    password_hash: str
    created_at: str
    updated_at: str


@dataclass(slots=True)
class Session:
    session_id: str
    user_id: int
    csrf_token: str
    created_at: str
    expires_at: str


@dataclass(slots=True)
class SessionContext:
    user: User
    session: Session


@dataclass(slots=True)
class QBInstance:
    id: int
    name: str
    base_url: str
    username: str
    encrypted_password: str
    verify_tls: bool
    enabled: bool
    reannounce_enabled: bool
    interval_minutes: int
    request_timeout_seconds: int
    retry_count: int
    app_version: Optional[str]
    webapi_version: Optional[str]
    last_status: Optional[str]
    last_error_message: Optional[str]
    last_checked_at: Optional[str]
    last_run_at: Optional[str]
    created_at: str
    updated_at: str


@dataclass(slots=True)
class ReannounceRun:
    id: int
    qb_instance_id: int
    trigger_source: str
    status: str
    started_at: str
    finished_at: Optional[str]
    torrent_count: int
    error_message: Optional[str]


@dataclass(slots=True)
class QBConnectionProbe:
    reachable: bool
    authenticated: bool
    app_version: Optional[str]
    webapi_version: Optional[str]
    message: str


@dataclass(slots=True)
class ReannounceOutcome:
    app_version: Optional[str]
    webapi_version: Optional[str]
    torrent_count: int


@dataclass(slots=True)
class SchedulerDecision:
    should_schedule: bool
    interval_minutes: int


@dataclass(slots=True)
class TimestampPair:
    started_at: datetime
    finished_at: datetime
