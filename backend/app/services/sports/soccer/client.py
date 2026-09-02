import asyncio
import time

import httpx

from app.core.config import get_settings
from app.core.exceptions import ExternalAPIError, SportsAPIRateLimitError
from app.core.http import API_SPORTS_KEY_HEADER, api_sports_headers, get_http_client
from app.services.sports.ttl_cache import (
    FIXTURE_PLAYERS_TTL_SECONDS,
    SEARCH_AND_LEAGUE_TTL_SECONDS,
    api_football_cache,
)

RATE_LIMIT_RETRY_DELAY_SECONDS = 2.5
FIXTURE_FETCH_DELAY_SECONDS = 0.6


class ApiFootballClient:
    """HTTP client for API-Football (API-Sports ecosystem)."""

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        settings = get_settings()
        self._base_url = settings.sports_api_base_url.rstrip("/")
        self._api_key = settings.sports_api_key.strip()
        self._injected_client = http_client

    def _auth_headers(self) -> dict[str, str]:
        return api_sports_headers(self._api_key)

    def _resolve_client(self) -> tuple[httpx.AsyncClient, bool]:
        if self._injected_client is not None:
            return self._injected_client, False
        shared = get_http_client()
        if shared is not None:
            return shared, False
        return (
            httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._auth_headers(),
                timeout=30.0,
            ),
            True,
        )

    def _format_api_errors(self, errors: object) -> str:
        if isinstance(errors, dict):
            return "; ".join(f"{k}: {v}" for k, v in errors.items())
        if isinstance(errors, list) and errors:
            return "; ".join(str(e) for e in errors)
        return str(errors)

    def _is_rate_limit_payload(self, *, status_code: int, body: str, errors: object) -> bool:
        if status_code == 429:
            return True
        haystack = f"{body} {self._format_api_errors(errors)}".lower()
        return "too many requests" in haystack or "rate limit" in haystack

    def _player_search_cache_key(self, params: dict) -> tuple:
        return (
            "players_search",
            params.get("league"),
            params.get("season"),
            str(params.get("search", "")).strip().lower(),
        )

    def _league_fixtures_cache_key(self, params: dict) -> tuple:
        return (
            "league_fixtures",
            params.get("team"),
            params.get("league"),
            params.get("season"),
            params.get("status"),
        )

    def _fixture_players_cache_key(
        self, *, player_id: int, season: int, fixture_id: int
    ) -> tuple:
        return ("fixtures_players", player_id, season, fixture_id)

    def _fixture_players_shared_cache_key(
        self, *, season: int, fixture_id: int
    ) -> tuple:
        return ("fixtures_players_api", season, fixture_id)

    async def get(self, path: str, params: dict | None = None) -> dict:
        """GET with TTL caching for player search and league fixture lists."""
        params = params or {}
        cache_key: tuple | None = None
        cache_ttl: float | None = None

        if path == "/players" and "search" in params:
            cache_key = self._player_search_cache_key(params)
            cache_ttl = SEARCH_AND_LEAGUE_TTL_SECONDS
        elif path == "/fixtures":
            cache_key = self._league_fixtures_cache_key(params)
            cache_ttl = SEARCH_AND_LEAGUE_TTL_SECONDS

        if cache_key is not None and cache_ttl is not None:
            cached = api_football_cache.get(cache_key)
            if cached is not None:
                return cached

        data = await self._fetch(path, params)

        if cache_key is not None and cache_ttl is not None:
            api_football_cache.set(cache_key, data, cache_ttl)

        return data

    async def get_fixture_players(
        self,
        fixture_id: int,
        *,
        season: int,
        player_id: int,
    ) -> dict:
        """GET /fixtures/players with 12h TTL (keyed by player, season, fixture)."""
        player_key = self._fixture_players_cache_key(
            player_id=player_id,
            season=season,
            fixture_id=fixture_id,
        )
        shared_key = self._fixture_players_shared_cache_key(
            season=season,
            fixture_id=fixture_id,
        )

        for key in (player_key, shared_key):
            cached = api_football_cache.get(key)
            if cached is not None:
                api_football_cache.set(player_key, cached, FIXTURE_PLAYERS_TTL_SECONDS)
                return cached

        data = await self._fetch(
            "/fixtures/players",
            {"fixture": fixture_id},
            rate_limit_after_fetch=True,
        )

        api_football_cache.set(player_key, data, FIXTURE_PLAYERS_TTL_SECONDS)
        api_football_cache.set(shared_key, data, FIXTURE_PLAYERS_TTL_SECONDS)
        return data

    async def _fetch(
        self,
        path: str,
        params: dict,
        *,
        rate_limit_after_fetch: bool = False,
    ) -> dict:
        if not self._api_key:
            raise ExternalAPIError(
                "SPORTS_API_KEY is not configured — set it in backend/.env"
            )

        headers = self._auth_headers()
        if API_SPORTS_KEY_HEADER not in headers:
            raise ExternalAPIError("SPORTS_API_KEY is empty after trim")

        client, owns_client = self._resolve_client()
        try:
            for attempt in range(2):
                response = await client.get(
                    path,
                    params=params,
                    headers=headers,
                )
                body_text = response.text
                if response.status_code == 429:
                    if attempt == 0:
                        await asyncio.sleep(RATE_LIMIT_RETRY_DELAY_SECONDS)
                        continue
                    raise SportsAPIRateLimitError()

                if response.status_code == 401:
                    raise ExternalAPIError(
                        "Sports API unauthorized — check SPORTS_API_KEY and "
                        f"{API_SPORTS_KEY_HEADER} header "
                        f"(GET {path}: {body_text[:200]})"
                    )
                if response.status_code >= 400:
                    raise ExternalAPIError(
                        f"Sports API HTTP {response.status_code} on {path}: "
                        f"{body_text[:300]}"
                    )

                data = response.json()
                errors = data.get("errors")
                if errors and self._is_rate_limit_payload(
                    status_code=response.status_code,
                    body=body_text,
                    errors=errors,
                ):
                    if attempt == 0:
                        await asyncio.sleep(RATE_LIMIT_RETRY_DELAY_SECONDS)
                        continue
                    raise SportsAPIRateLimitError()

                if errors:
                    raise ExternalAPIError(
                        f"Sports API returned errors: {self._format_api_errors(errors)}"
                    )

                if rate_limit_after_fetch:
                    await asyncio.sleep(FIXTURE_FETCH_DELAY_SECONDS)

                return data

            raise SportsAPIRateLimitError()
        except SportsAPIRateLimitError:
            raise
        except httpx.HTTPError as exc:
            raise ExternalAPIError(f"Sports API request failed: {exc}") from exc
        finally:
            if owns_client:
                await client.aclose()
