"""Abstract interface for multi-sport stats providers."""

from abc import ABC, abstractmethod

from app.models.common import SportType
from app.models.player import PlayerSummary
from app.models.prediction import PropType
from app.models.stats import PlayerMatchStat


class SportsStatsProvider(ABC):
    """Contract each sport module (soccer, nba, nfl) must implement."""

    sport: SportType

    @abstractmethod
    async def search_players(
        self,
        query: str,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerSummary]:
        ...

    @abstractmethod
    async def get_player(
        self,
        player_id: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> PlayerSummary | None:
        ...

    @abstractmethod
    async def get_player_recent_stats(
        self,
        player_id: int,
        last_n: int,
        *,
        league_id: int | None = None,
        season: int | None = None,
    ) -> list[PlayerMatchStat]:
        ...

    def extract_prop_value(self, stat: PlayerMatchStat, prop_type: PropType) -> float:
        """Map a match stat row to the numeric value for a given prop."""
        mapping = {
            PropType.GOALS: stat.goals,
            PropType.ASSISTS: stat.assists,
            PropType.SHOTS: stat.shots,
            PropType.SHOTS_ON_TARGET: stat.shots_on_target,
        }
        return float(mapping[prop_type])
