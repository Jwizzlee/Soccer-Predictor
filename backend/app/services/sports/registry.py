"""Registry of sport-specific provider factories."""

from collections.abc import Callable

from app.models.common import SportType
from app.services.sports.base import SportsStatsProvider

ProviderFactory = Callable[[], SportsStatsProvider]

_REGISTRY: dict[SportType, ProviderFactory] = {}


def register_sport(sport: SportType, factory: ProviderFactory) -> None:
    _REGISTRY[sport] = factory


def get_registered_sports() -> list[SportType]:
    return list(_REGISTRY.keys())


def create_provider(sport: SportType) -> SportsStatsProvider:
    factory = _REGISTRY.get(sport)
    if factory is None:
        supported = ", ".join(s.value for s in _REGISTRY)
        raise ValueError(
            f"Sport '{sport.value}' is not supported. Available: {supported or 'none'}"
        )
    return factory()
