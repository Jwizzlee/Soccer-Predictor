from app.core.config import get_settings
from app.services.sports.soccer.config import get_league_season


def resolve_season_year(*, league_id: int | None = None, season: int | None = None) -> int:
    """
    Resolve API-Football season param.

    Priority: explicit request season → league config season → settings fallback.
    """
    if season is not None:
        return season
    if league_id is not None:
        configured = get_league_season(league_id)
        if configured is not None:
            return configured
    settings = get_settings()
    if settings.sports_api_season is not None:
        return settings.sports_api_season
    return 2024
