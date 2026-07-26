from __future__ import annotations

import ipaddress
import urllib.parse
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def beijing_now() -> datetime:
    """Get current time in Beijing timezone (UTC+8 +08:00)"""
    return datetime.now(ZoneInfo("Asia/Shanghai"))


def beijing_now_iso() -> str:
    """Get current time in Beijing timezone as ISO string"""
    return beijing_now().isoformat()


def add_hours_iso(hours: int) -> str:
    return (utc_now() + timedelta(hours=hours)).isoformat()


def assert_public_url(url: str, label: str = "url", allow_private: bool = False) -> urllib.parse.ParseResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"{label} must use http or https")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"{label} must contain a valid hostname")
    host = hostname.lower().rstrip(".").strip("[]")
    # ponytail: block private/loopback IP literals inline only; no DNS resolve (attacker
    # controls DNS anyway, and resolution makes startup slow and breaks offline tests)
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None:
        if address.is_unspecified or address.is_multicast:
            raise ValueError(f"{label} must not point to an unspecified/multicast address")
        if not allow_private and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
            raise ValueError(f"{label} must not point to a private/internal IP address")
    elif not allow_private and host in {"localhost", "localhost.localdomain"}:
        raise ValueError(f"{label} must not point to localhost")
    return parsed


def mask_url_host(url: str) -> str:
    """Mask the last two octets of an IPv4 host in a URL for display.

    Non-IP hostnames pass through unchanged. Port is preserved.
    e.g. http://192.168.1.100:8080 -> http://192.168.*.***:8080
    """
    if not url:
        return ''
    import re
    m = re.match(r'^(https?://)(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(.*)$', url)
    if not m:
        return url
    scheme, a, b = m.group(1), m.group(2), m.group(3)
    return f'{scheme}{a}.{b}.*.***{m.group(6)}'


def format_beijing_time(iso_string: str) -> str:
    """Convert UTC ISO string to Beijing time string for display"""
    if not iso_string:
        return ""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        beijing_dt = dt.astimezone(ZoneInfo("Asia/Shanghai"))
        return beijing_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_string
