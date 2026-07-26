from __future__ import annotations

import re
import urllib.parse
from typing import Optional, Any
from dataclasses import dataclass

import httpx

from app.domain import QBConnectionProbe, QBInstance, ReannounceOutcome
from app.security import SecretCipher
from app.utils import assert_public_url


class QBClientError(RuntimeError):
    pass


class QBAuthError(QBClientError):
    pass


class QBCompatibilityError(QBClientError):
    pass


@dataclass
class TorrentInfo:
    """Represents a torrent in qBittorrent."""
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
    completion_on: int
    downloaded: int
    uploaded: int
    ratio: float
    save_path: str
    download_path: str
    priority: int
    seq_dl: bool
    f_l_piece_prio: bool
    num_seeds: int
    num_complete: int
    num_leechs: int
    num_incomplete: int
    total_size: int


class QBClient:
    def __init__(self, instance: QBInstance, secret_cipher: SecretCipher) -> None:
        self._assert_public_url(instance.base_url, allow_private=True)
        self.instance = instance
        self.secret_cipher = secret_cipher
        self.client = httpx.AsyncClient(
            base_url=instance.base_url,
            timeout=instance.request_timeout_seconds,
            verify=instance.verify_tls,
            headers={"Referer": instance.base_url},
        )
        self._logged_in = False
        self._dl_client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self.client.aclose()
        await self._dl_client.aclose()

    async def _login(self) -> None:
        password = self.secret_cipher.decrypt(self.instance.encrypted_password)
        try:
            response = await self.client.post(
                "/api/v2/auth/login",
                data={"username": self.instance.username, "password": password},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise QBAuthError(f"qBittorrent WebUI login failed: {exc}") from exc

        # qB 4.x:   200 OK,  body = "Ok." (success) / "Fails." (failure)
        # qB 5.x:   204 No Content, empty body (success), cookie handled by httpx jar
        # qB 5.x:   401/403 on failed auth (caught above, re-raised as QBAuthError)
        # Edge:     Some 5.x versions may return 200 with empty body
        if response.status_code == 204:
            pass  # qB 5.x: No Content = login OK
        elif response.status_code == 200:
            body = response.text.lstrip('﻿').strip()
            if body.lower() != "ok.":
                raise QBAuthError(f"qBittorrent WebUI login failed: {body[:200]!r}")
        else:
            raise QBAuthError(
                f"qBittorrent WebUI login failed: unexpected status {response.status_code}"
            )

        self._logged_in = True

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        if not self._logged_in:
            await self._login()
        response = await self.client.request(method, path, **kwargs)
        if response.status_code in {401, 403}:
            self._logged_in = False
            try:
                await self._login()
            except QBAuthError:
                raise
            response = await self.client.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            self._logged_in = False
            raise
        return response

    def _assert_public_url(self, url: str, allow_private: bool = False) -> urllib.parse.ParseResult:
        try:
            return assert_public_url(url, allow_private=allow_private)
        except ValueError as exc:
            raise QBClientError(str(exc)) from exc

    async def _get_public_url(self, url: str) -> httpx.Response:
        current_url = url
        for _ in range(5):
            self._assert_public_url(current_url)
            response = await self._dl_client.get(current_url, follow_redirects=False)
            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    response.raise_for_status()
                    return response
                current_url = urllib.parse.urljoin(str(response.url), location)
                continue
            response.raise_for_status()
            return response
        raise QBClientError("URL has too many redirects")

    async def detect_versions(self) -> tuple[Optional[str], Optional[str]]:
        app_version = None
        webapi_version = None
        try:
            app_resp = await self._request("GET", "/api/v2/app/version")
            app_version = app_resp.text.strip() or None
        except httpx.HTTPStatusError as exc:
            raise QBCompatibilityError("Unsupported endpoint: /api/v2/app/version") from exc
        try:
            webapi_resp = await self._request("GET", "/api/v2/app/webapiVersion")
            webapi_version = webapi_resp.text.strip() or None
        except httpx.HTTPStatusError:
            webapi_version = None
        return app_version, webapi_version

    async def probe(self) -> QBConnectionProbe:
        try:
            app_version, webapi_version = await self.detect_versions()
            return QBConnectionProbe(
                reachable=True,
                authenticated=True,
                app_version=app_version,
                webapi_version=webapi_version,
                message="Connection successful",
            )
        except QBAuthError as exc:
            return QBConnectionProbe(
                reachable=True,
                authenticated=False,
                app_version=None,
                webapi_version=None,
                message=str(exc),
            )
        except httpx.HTTPError as exc:
            return QBConnectionProbe(
                reachable=False,
                authenticated=False,
                app_version=None,
                webapi_version=None,
                message=f"Network error: {exc}",
            )
        except QBCompatibilityError as exc:
            return QBConnectionProbe(
                reachable=True,
                authenticated=True,
                app_version=None,
                webapi_version=None,
                message=str(exc),
            )

    async def fetch_all_hashes(self) -> list[str]:
        response = await self._request("GET", "/api/v2/torrents/info")
        data = response.json()
        if not isinstance(data, list):
            raise QBCompatibilityError("Unsupported response format from /api/v2/torrents/info")
        hashes: list[str] = []
        for item in data:
            torrent_hash = item.get("hash") if isinstance(item, dict) else None
            if torrent_hash:
                hashes.append(str(torrent_hash))
        return hashes

    async def get_torrents(self) -> list[dict]:
        """
        Fetch all torrents with detailed information.
        Returns list of torrent dictionaries with all relevant fields.
        """
        response = await self._request("GET", "/api/v2/torrents/info")
        data = response.json()
        if not isinstance(data, list):
            raise QBCompatibilityError("Unsupported response format from /api/v2/torrents/info")
        return data

    async def get_torrent_properties(self, torrent_hash: str) -> dict:
        """Get detailed properties for a specific torrent."""
        response = await self._request("GET", f"/api/v2/torrents/properties?hash={torrent_hash}")
        return response.json()

    async def reannounce_all(self, batch_size: int = 100) -> ReannounceOutcome:
        try:
            app_version, webapi_version = await self.detect_versions()
        except Exception:
            app_version, webapi_version = "unknown", "unknown"
        hashes = await self.fetch_all_hashes()
        for start in range(0, len(hashes), batch_size):
            batch = hashes[start : start + batch_size]
            await self._request(
                "POST",
                "/api/v2/torrents/reannounce",
                data={"hashes": "|".join(batch)},
            )
        return ReannounceOutcome(
            app_version=app_version,
            webapi_version=webapi_version,
            torrent_count=len(hashes),
        )

    async def set_torrent_category(self, torrent_hash: str, category: str) -> None:
        """Set category for a torrent."""
        await self._request(
            "POST",
            "/api/v2/torrents/setCategory",
            data={"hashes": torrent_hash, "category": category},
        )

    async def get_categories(self) -> dict:
        """Get all categories."""
        response = await self._request("GET", "/api/v2/torrents/categories")
        return response.json()

    async def recheck_all(self) -> int:
        """Recheck all torrents. Returns number of torrents checked."""
        hashes = await self.fetch_all_hashes()
        if not hashes:
            return 0
        for start in range(0, len(hashes), 100):
            batch = hashes[start:start + 100]
            await self._request(
                "POST",
                "/api/v2/torrents/recheck",
                data={"hashes": "|".join(batch)},
            )
        return len(hashes)

    async def reannounce_one(self, torrent_hash: str) -> None:
        await self._request("POST", "/api/v2/torrents/reannounce", data={"hashes": torrent_hash})
    async def recheck_one(self, torrent_hash: str) -> None:
        await self._request("POST", "/api/v2/torrents/recheck", data={"hashes": torrent_hash})
    async def reannounce_batch(self, torrent_hashes: list[str]) -> int:
        if not torrent_hashes: return 0
        await self._request("POST", "/api/v2/torrents/reannounce", data={"hashes": "|".join(torrent_hashes)})
        return len(torrent_hashes)
    async def get_transfer_info(self) -> dict:
        """Get global transfer info (DL/UP speed and totals) from qBittorrent."""
        response = await self._request("GET", "/api/v2/transfer/info")
        return response.json()

    async def add_torrent(self, urls: str, savepath: str = "",
                          upload_limit: int = 0, download_limit: int = 0) -> str:
        import logging
        _log = logging.getLogger("app.clients.qbittorrent")
        # First verify the URL is reachable and returns a torrent
        _log.info("add_torrent: probing %s", urls[:100])
        try:
            probe = await self._get_public_url(urls)
            ct = probe.headers.get("content-type", "")
            qb_url = str(probe.url)
            _log.info("add_torrent: probe OK, size=%d, content-type=%s", len(probe.content), ct)
        except Exception as e:
            _log.error("add_torrent: probe failed: %s", e)
            raise QBClientError(f"URL unreachable: {e}") from e
        # Pass URL to qBittorrent (simpler, no multipart)
        data = {
            "urls": qb_url,
            "upLimit": str(upload_limit),
            "dlLimit": str(download_limit),
        }
        if savepath:
            data["savepath"] = savepath
        _log.info("add_torrent: sending to qB, data=%s", {k: v[:80] if k == "urls" else v for k, v in data.items()})
        response = await self._request("POST", "/api/v2/torrents/add", data=data)
        text = response.text.lstrip('﻿').strip()
        _log.info("add_torrent response: %r", text)
        if text and text.lower() != "ok.":
            raise QBClientError(f"Failed to add torrent: {text}")
        return text

    async def recheck_batch(self, torrent_hashes: list[str]) -> int:
        if not torrent_hashes: return 0
        await self._request("POST", "/api/v2/torrents/recheck", data={"hashes": "|".join(torrent_hashes)})
        return len(torrent_hashes)
