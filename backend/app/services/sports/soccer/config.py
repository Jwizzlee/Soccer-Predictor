"""Soccer-specific configuration (leagues, seasons)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LeagueConfig:
    id: int
    name: str
    country: str
    season: int


# API-Football league IDs + configured testing seasons
MVP_LEAGUES: dict[int, LeagueConfig] = {
    39: LeagueConfig(id=39, name="Premier League", country="England", season=2024),
    140: LeagueConfig(id=140, name="La Liga", country="Spain", season=2024),
    135: LeagueConfig(id=135, name="Serie A", country="Italy", season=2024),
    2: LeagueConfig(
        id=2, name="UEFA Champions League", country="Europe", season=2024
    ),
    1: LeagueConfig(id=1, name="FIFA World Cup", country="World", season=2026),
}

DEFAULT_LEAGUE_IDS: list[int] = list(MVP_LEAGUES.keys())


def get_league_name(league_id: int) -> str | None:
    league = MVP_LEAGUES.get(league_id)
    return league.name if league else None


def get_league_season(league_id: int) -> int | None:
    league = MVP_LEAGUES.get(league_id)
    return league.season if league else None
