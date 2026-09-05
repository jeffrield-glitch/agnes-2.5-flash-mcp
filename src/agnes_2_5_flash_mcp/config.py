"""API key / base URL resolution: explicit arg > env var > .env file."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_BASE_URL = "https://apihub.agnes-ai.com/v1"

_ENV_LOADED = False


def _maybe_load_dotenv() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    try:
        from dotenv import load_dotenv

        # Load .env from CWD and from the project root (two levels above src).
        load_dotenv(Path.cwd() / ".env", override=False)
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
    except ImportError:
        pass


def resolve_api_key(explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    _maybe_load_dotenv()
    key = os.environ.get("AGNES_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "Missing Agnes API key. Pass api_key to the tool, "
            "set env var AGNES_API_KEY, or create a .env file (see .env.example)."
        )
    return key


def resolve_base_url(explicit: str | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip().rstrip("/")
    _maybe_load_dotenv()
    return os.environ.get("AGNES_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/") or DEFAULT_BASE_URL


def query_base_url(base_url: str) -> str:
    """Poll endpoint lives at the apihub root: <root>/agnesapi (not under /v1)."""
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[: -len("/v1")]
    return root
