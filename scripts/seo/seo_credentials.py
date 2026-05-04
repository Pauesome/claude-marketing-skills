"""
Lightweight credential helper for PSI / CrUX. Reads a single agency-level
Google API key from the environment.
"""

from __future__ import annotations

import ipaddress
import os
from typing import Optional
from urllib.parse import urlparse


def get_api_key() -> Optional[str]:
    """
    Read the Google API key for PageSpeed Insights / CrUX.

    Order: GOOGLE_PAGESPEED_API_KEY → GOOGLE_API_KEY (fallback).
    Both APIs are free with a single agency key — no per-client OAuth.
    """
    return os.environ.get("GOOGLE_PAGESPEED_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def load_config() -> dict:
    """
    Compatibility shim for upstream pagespeed_check.py which calls
    load_config().get("api_key"). We just wrap get_api_key().
    """
    key = get_api_key()
    return {"api_key": key} if key else {}


def validate_url(url: str) -> bool:
    """
    SSRF guard. Reject loopback, private, link-local, and metadata
    endpoints. Only http/https public URLs pass.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    blocked = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}
    if parsed.hostname in blocked:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        # Not an IP literal — hostname is fine.
        pass
    return True
