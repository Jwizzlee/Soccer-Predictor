"""Mock soccer stats provider — no external API required."""

from app.models.common import SportType
from app.models.player import PlayerSummary
from app.models.stats import PlayerMatchStat
from app.services.sports.base import SportsStatsProvider
from app.services.sports.soccer.mock_data import (
    MOCK_PLAYERS,
    generate_match_stats,
    search_mock_players,
)


class MockSoccerStatsProvider(SportsStatsProvider):
    """
    Simulates API-Football responses for Premier League / La Liga players.
    Use player IDs 1001–1004 (see mock_data.MOCK_PLAYERS).
    """

    sport = SportType.SOCCER

    async def search_players(
        self,
        query: str,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerSummary]:
        return search_mock_players(query, league_id)

    async def get_player(
        self,
        player_id: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> PlayerSummary | None:
        mock = MOCK_PLAYERS.get(player_id)
        if not mock:
            return None
        if league_id and mock.summary.league_id != league_id:
            return None
        return mock.summary

    async def get_player_recent_stats(
        self,
        player_id: int,
        last_n: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerMatchStat]:
        if player_id not in MOCK_PLAYERS:
            return []
        if league_id:
            mock = MOCK_PLAYERS[player_id]
            if mock.summary.league_id != league_id:
                return []
        return generate_match_stats(player_id, last_n)
