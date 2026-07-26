from __future__ import annotations

import httpx
import pytest

from app.clients.qbittorrent import QBClient
from app.domain import QBInstance
from app.security import SecretCipher


@pytest.fixture
def qb_instance():
    from cryptography.fernet import Fernet

    cipher = SecretCipher(Fernet.generate_key().decode())
    return QBInstance(
        id=1,
        name="qb-test",
        base_url="http://qb.local",
        username="admin",
        encrypted_password=cipher.encrypt("pass"),
        verify_tls=False,
        enabled=True,
        reannounce_enabled=True,
        interval_minutes=60,
        request_timeout_seconds=15,
        retry_count=3,
        app_version=None,
        webapi_version=None,
        last_status=None,
        last_error_message=None,
        last_checked_at=None,
        last_run_at=None,
        created_at="2024-01-01T00:00:00+00:00",
        updated_at="2024-01-01T00:00:00+00:00",
    ), cipher


@pytest.mark.asyncio
async def test_probe_supports_439_style_endpoints(qb_instance):
    instance, cipher = qb_instance

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/auth/login":
            return httpx.Response(200, text="Ok.")
        if request.url.path == "/api/v2/app/version":
            return httpx.Response(200, text="v4.3.9")
        if request.url.path == "/api/v2/app/webapiVersion":
            return httpx.Response(200, text="2.8.3")
        raise AssertionError(f"unexpected path: {request.url.path}")

    transport = httpx.MockTransport(handler)
    client = QBClient(instance, cipher)
    client.client = httpx.AsyncClient(base_url=instance.base_url, transport=transport, verify=False)
    try:
        probe = await client.probe()
    finally:
        await client.close()

    assert probe.reachable is True
    assert probe.authenticated is True
    assert probe.app_version == "v4.3.9"
    assert probe.webapi_version == "2.8.3"


@pytest.mark.asyncio
async def test_reannounce_batches_hashes_and_handles_empty_list(qb_instance):
    instance, cipher = qb_instance
    seen_batches = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/auth/login":
            return httpx.Response(200, text="Ok.")
        if request.url.path == "/api/v2/app/version":
            return httpx.Response(200, text="v5.1.0")
        if request.url.path == "/api/v2/app/webapiVersion":
            return httpx.Response(200, text="2.10.1")
        if request.url.path == "/api/v2/torrents/info":
            payload = [{"hash": str(i)} for i in range(205)]
            return httpx.Response(200, json=payload)
        if request.url.path == "/api/v2/torrents/reannounce":
            body = request.content.decode()
            seen_batches.append(body)
            return httpx.Response(200, text="")
        raise AssertionError(f"unexpected path: {request.url.path}")

    transport = httpx.MockTransport(handler)
    client = QBClient(instance, cipher)
    client.client = httpx.AsyncClient(base_url=instance.base_url, transport=transport, verify=False)
    try:
        outcome = await client.reannounce_all(batch_size=100)
    finally:
        await client.close()

    assert outcome.torrent_count == 205
    assert len(seen_batches) == 3


@pytest.mark.asyncio
async def test_probe_reports_network_failures(qb_instance):
    instance, cipher = qb_instance

    def handler(request: httpx.Request):
        raise httpx.ConnectError("boom", request=request)

    transport = httpx.MockTransport(handler)
    client = QBClient(instance, cipher)
    client.client = httpx.AsyncClient(base_url=instance.base_url, transport=transport, verify=False)
    try:
        probe = await client.probe()
    finally:
        await client.close()

    assert probe.reachable is False
    assert probe.authenticated is False
