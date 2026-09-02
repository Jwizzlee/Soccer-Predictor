"""Shared async HTTP client and API-Sports auth headers."""

import httpx

# Required by https://v3.football.api-sports.io (API-Sports dashboard keys)
API_SPORTS_KEY_HEADER = "x-apisports-key"


def api_sports_headers(api_key: str) -> dict[str, str]:
    """Build auth headers for every API-Football request."""
    key = (api_key or "").strip()
    if not key:
        return {}
    return {API_SPORTS_KEY_HEADER: key}


_shared_client: httpx.AsyncClient | None = None


def set_http_client(client: httpx.AsyncClient | None) -> None:
    global _shared_client
    _shared_client = client


def get_http_client() -> httpx.AsyncClient | None:
    return _shared_client
