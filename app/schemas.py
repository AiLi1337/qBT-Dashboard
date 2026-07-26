from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Dict, Any
import re

from app.utils import assert_public_url


class QBInstanceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_url: str
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1)
    verify_tls: bool = True
    enabled: bool = True
    reannounce_enabled: bool = True
    interval_minutes: int = 60
    request_timeout_seconds: int = 15
    retry_count: int = 3

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        assert_public_url(v, 'base_url', allow_private=True)
        return v


class QBInstanceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    base_url: Optional[str] = None
    username: Optional[str] = Field(default=None, min_length=1, max_length=120)
    password: Optional[str] = Field(default=None, min_length=1)
    verify_tls: Optional[bool] = None
    enabled: Optional[bool] = None
    reannounce_enabled: Optional[bool] = None
    interval_minutes: Optional[int] = None
    request_timeout_seconds: Optional[int] = None
    retry_count: Optional[int] = None

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        assert_public_url(v, 'base_url', allow_private=True)
        return v


class QBInstanceView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    base_url: str
    username: str
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


class QBConnectionStatus(BaseModel):
    reachable: bool
    authenticated: bool
    app_version: Optional[str]
    webapi_version: Optional[str]
    message: str


class ReannounceRunView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    qb_instance_id: int
    trigger_source: str
    status: str
    started_at: str
    finished_at: Optional[str]
    torrent_count: int
    error_message: Optional[str]


class DashboardSummary(BaseModel):
    total_instances: int
    enabled_instances: int
    recent_runs: int


class TorrentSummaryView(BaseModel):
    total_count: int
    downloading: int
    seeding: int
    paused: int
    checking: int
    error: int
    total_downloaded: int
    total_uploaded: int


class TransferInfo(BaseModel):
    """Global qBittorrent transfer information."""
    dl_info_speed: int = 0
    dl_info_data: int = 0
    up_info_speed: int = 0
    up_info_data: int = 0
    dl_rate_limit: int = 0
    up_rate_limit: int = 0
    dht_nodes: int = 0
    connection_status: str = ""



class TorrentView(BaseModel):
    """Simplified torrent view for list display."""
    hash: str
    name: str
    size: int
    progress: float
    dlspeed: int
    upspeed: int
    state: str
    category: str
    tags: str
    added_on: int
    completion_on: Optional[int]
    downloaded: int
    uploaded: int
    ratio: float
    save_path: str
    num_seeds: int
    num_complete: int
    num_leechs: int
    num_incomplete: int
    total_size: int


class TorrentPropertiesView(BaseModel):
    """Detailed torrent properties."""
    save_path: str
    download_path: Optional[str]
    creation_date: Optional[int]
    piece_size: int
    pieces_num: int
    pieces_have: int
    progress: float
    downloaded: int
    uploaded: int
    download_speed: int
    upload_speed: int
    active: bool
    semi_active: bool
    inactive: bool
    resume_cap: int
    nb_seeds: int
    total_seeds: int
    nb_leechs: int
    total_leechs: int
    torrent_size: int
    total_size: int
    comment: str
    free_space_on_disk: int

class AddTorrentRequest(BaseModel):
    '''Request to add a torrent.'''
    urls: str
    savepath: str = ''
    upload_limit_speed: float = 80.0
    download_limit_speed: float = 80.0

    @field_validator('savepath')
    @classmethod
    def validate_savepath(cls, v: str) -> str:
        if '..' in v:
            raise ValueError('savepath must not contain path traversal (..)')
        normalized = v.replace('\\\\', '/')
        if '%2e%2e' in normalized.lower():
            raise ValueError('savepath must not contain path traversal (..)')
        return normalized

class BatchHashesRequest(BaseModel):
    """Batch request with torrent hash list, capped for safety."""
    hashes: list[str]

    @field_validator('hashes')
    @classmethod
    def check_size(cls, v: list[str]) -> list[str]:
        if len(v) > 5000:
            raise ValueError('too many hashes (max 5000)')
        if not v:
            raise ValueError('hashes list must not be empty')
        for torrent_hash in v:
            if not re.fullmatch(r'^[0-9a-fA-F]{40}$', torrent_hash):
                raise ValueError('invalid torrent hash format')
        return v
