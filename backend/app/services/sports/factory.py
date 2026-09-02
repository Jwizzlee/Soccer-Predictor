from functools import lru_cache

from app.core.config import get_settings
from app.models.common import SportType
from app.services.sports.base import SportsStatsProvider
from app.services.sports.registry import create_provider


def get_sports_provider(sport: SportType | None = None) -> SportsStatsProvider:
    """Return the stats provider for the requested sport (defaults from settings)."""
    resolved = sport or SportType(get_settings().default_sport)
    return create_provider(resolved)


@lru_cache
def _ensure_sports_registered() -> None:
    """Lazy registration of sport modules to avoid circular imports."""
    from app.services.sports.soccer import register_soccer_provider

    register_soccer_provider()
    # Future: register_nba_provider(), register_nfl_provider()


def init_sports_registry() -> None:
    _ensure_sports_registered()
