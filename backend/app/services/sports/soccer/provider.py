from dataclasses import dataclass

import httpx

from app.core.exceptions import SportsAPIRateLimitError
from app.models.common import SportType
from app.models.player import PlayerSummary
from app.models.stats import PlayerMatchStat
from app.services.sports.base import SportsStatsProvider
from app.services.sports.soccer.client import ApiFootballClient
from app.services.sports.soccer.config import DEFAULT_LEAGUE_IDS
from app.services.sports.soccer.mapper import (
    map_fixture_player_stat,
    map_player,
    map_squad_player,
)
from app.services.sports.soccer.season import resolve_season_year

MAX_FIXTURE_DETAIL_LOOKUPS = 40
MAX_RECENT_GAMES_FREE_TIER = 5


@dataclass
class RecentStatsResult:
    stats: list[PlayerMatchStat]
    rate_limited: bool = False
    requested_games: int = 0


@dataclass
class _PlayerContext:
    summary: PlayerSummary
    team_id: int
    league_id: int
    season: int


class SoccerStatsProvider(SportsStatsProvider):
    """Live API-Football provider for global soccer leagues."""

    sport = SportType.SOCCER

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._client = ApiFootballClient(http_client=http_client)

    async def search_players(
        self,
        query: str,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerSummary]:
        if not query.strip():
            return []

        league_ids = [league_id] if league_id else DEFAULT_LEAGUE_IDS
        results: list[PlayerSummary] = []
        seen: set[int] = set()

        for lid in league_ids:
            resolved_season = resolve_season_year(league_id=lid, season=season)
            data = await self._client.get(
                "/players",
                params={"league": lid, "season": resolved_season, "search": query},
            )
            for item in data.get("response", []):
                player = map_player(item, league_id=lid)
                if player.id and player.id not in seen:
                    seen.add(player.id)
                    results.append(player)

        return results[:25]

    async def get_player(
        self,
        player_id: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> PlayerSummary | None:
        ctx = await self._resolve_player_context(player_id, league_id, season)
        return ctx.summary if ctx else None

    async def get_team_roster(
        self,
        team_id: int,
        *,
        league_id: int,
        season: int | None = None,
    ) -> list[PlayerSummary]:
        data = await self._client.get(
            "/players/squads",
            params={"team": team_id},
        )
        roster: list[PlayerSummary] = []
        for block in data.get("response", []):
            team = block.get("team", {})
            team_name = team.get("name", "Unknown")
            for entry in block.get("players", []):
                player = map_squad_player(
                    entry,
                    league_id=league_id,
                    team_name=team_name,
                    team_id=team_id,
                )
                if player.id:
                    roster.append(player)
        return roster

    async def list_teams(
        self, league_id: int, season: int | None = None
    ) -> list[dict]:
        resolved_season = resolve_season_year(league_id=league_id, season=season)
        data = await self._client.get(
            "/teams",
            params={"league": league_id, "season": resolved_season},
        )
        teams = []
        for item in data.get("response", []):
            team = item.get("team", item)
            teams.append(
                {
                    "id": team.get("id"),
                    "name": team.get("name"),
                    "logo": team.get("logo"),
                    "league_id": league_id,
                }
            )
        return teams

    async def get_player_recent_stats(
        self,
        player_id: int,
        last_n: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerMatchStat]:
        result = await self.get_player_recent_stats_result(
            player_id,
            last_n,
            league_id=league_id,
            season=season,
        )
        return result.stats

    async def get_player_recent_stats_result(
        self,
        player_id: int,
        last_n: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> RecentStatsResult:
        last_n = min(last_n, MAX_RECENT_GAMES_FREE_TIER)
        ctx = await self._resolve_player_context(player_id, league_id, season)
        if not ctx:
            return RecentStatsResult(stats=[], requested_games=last_n)

        fixtures = await self._fetch_team_fixtures(
            team_id=ctx.team_id,
            league_id=ctx.league_id,
            season=ctx.season,
        )

        stats: list[PlayerMatchStat] = []
        lookups = 0
        rate_limited = False
        max_lookups = min(len(fixtures), max(last_n * 4, last_n), MAX_FIXTURE_DETAIL_LOOKUPS)

        for fixture_row in fixtures:
            if len(stats) >= last_n or lookups >= max_lookups:
                break

            fixture = fixture_row.get("fixture", {})
            teams = fixture_row.get("teams", {})
            fixture_id = fixture.get("id")
            if not fixture_id:
                continue

            lookups += 1
            try:
                players_data = await self._client.get_fixture_players(
                    fixture_id,
                    season=ctx.season,
                    player_id=player_id,
                )
            except SportsAPIRateLimitError:
                rate_limited = True
                break

            stat = self._extract_player_fixture_stat(
                players_data.get("response", []),
                player_id=player_id,
                fixture=fixture,
                teams=teams,
            )
            if stat is not None and stat.minutes > 0:
                stats.append(stat)

        return RecentStatsResult(
            stats=stats[:last_n],
            rate_limited=rate_limited,
            requested_games=last_n,
        )

    async def _resolve_player_context(
        self,
        player_id: int,
        league_id: int | None,
        season: int | None = None,
    ) -> _PlayerContext | None:
        league_ids = [league_id] if league_id else DEFAULT_LEAGUE_IDS

        for lid in league_ids:
            resolved_season = resolve_season_year(league_id=lid, season=season)
            data = await self._client.get(
                "/players",
                params={"id": player_id, "league": lid, "season": resolved_season},
            )
            response = data.get("response", [])
            if not response:
                continue

            item = response[0]
            summary = map_player(item, league_id=lid)
            statistics = item.get("statistics") or []
            if not statistics:
                continue

            team_id = statistics[0].get("team", {}).get("id")
            if not team_id:
                continue

            return _PlayerContext(
                summary=summary,
                team_id=team_id,
                league_id=lid,
                season=resolved_season,
            )
        return None

    async def _fetch_team_fixtures(
        self,
        *,
        team_id: int,
        league_id: int,
        season: int,
    ) -> list[dict]:
        data = await self._client.get(
            "/fixtures",
            params={
                "team": team_id,
                "league": league_id,
                "season": season,
                "status": "FT",
            },
        )
        rows = data.get("response", [])
        return sorted(
            rows,
            key=lambda r: r.get("fixture", {}).get("date", ""),
            reverse=True,
        )

    def _extract_player_fixture_stat(
        self,
        fixture_blocks: list[dict],
        *,
        player_id: int,
        fixture: dict,
        teams: dict,
    ) -> PlayerMatchStat | None:
        for team_block in fixture_blocks:
            team = team_block.get("team", {})
            for entry in team_block.get("players", []):
                p = entry.get("player", {})
                if p.get("id") != player_id:
                    continue
                return map_fixture_player_stat(
                    entry,
                    fixture=fixture,
                    teams=teams,
                    team=team,
                )
        return None
