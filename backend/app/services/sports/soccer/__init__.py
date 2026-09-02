from app.core.config import get_settings
from app.core.http import get_http_client
from app.models.common import SportType
from app.services.sports.registry import register_sport
from app.services.sports.soccer.mock_provider import MockSoccerStatsProvider
from app.services.sports.soccer.provider import SoccerStatsProvider


def _create_soccer_provider():
    if get_settings().use_mock_sports_data:
        return MockSoccerStatsProvider()
    return SoccerStatsProvider(http_client=get_http_client())


def register_soccer_provider() -> None:
    register_sport(SportType.SOCCER, _create_soccer_provider)


__all__ = [
    "register_soccer_provider",
    "SoccerStatsProvider",
    "MockSoccerStatsProvider",
]
