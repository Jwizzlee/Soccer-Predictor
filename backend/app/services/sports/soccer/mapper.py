from datetime import date

from app.models.common import SportType
from app.models.player import PlayerSummary
from app.models.stats import PlayerMatchStat
from app.services.sports.soccer.config import get_league_name


def map_player(item: dict, *, league_id: int | None = None) -> PlayerSummary:
    player = item.get("player") or item
    statistics = item.get("statistics") or []
    team_info: dict = {}
    if statistics:
        team_info = statistics[0].get("team", {}) or {}
    elif "team" in item:
        team_info = item["team"]

    return PlayerSummary(
        id=player.get("id", 0),
        name=player.get("name", "Unknown"),
        team=team_info.get("name", "Unknown"),
        team_id=team_info.get("id"),
        position=player.get("position"),
        photo_url=player.get("photo"),
        league_id=league_id,
        league_name=get_league_name(league_id) if league_id else None,
        sport=SportType.SOCCER,
    )


def map_squad_player(entry: dict, *, league_id: int, team_name: str, team_id: int) -> PlayerSummary:
    player = entry if "id" in entry and "name" in entry else entry.get("player", entry)
    return PlayerSummary(
        id=player.get("id", 0),
        name=player.get("name", "Unknown"),
        team=team_name,
        team_id=team_id,
        position=player.get("position"),
        photo_url=player.get("photo"),
        league_id=league_id,
        league_name=get_league_name(league_id),
        sport=SportType.SOCCER,
    )


def map_fixture_player_stat(
    entry: dict,
    *,
    fixture: dict,
    teams: dict,
    team: dict,
) -> PlayerMatchStat:
    player_team_id = team.get("id")
    home = teams.get("home", {})
    away = teams.get("away", {})

    opponent = "Unknown"
    if player_team_id == home.get("id"):
        opponent = away.get("name", "Unknown")
    elif player_team_id == away.get("id"):
        opponent = home.get("name", "Unknown")

    statistics = entry.get("statistics") or []
    stats = statistics[0] if statistics else {}
    games = stats.get("games", {}) or {}
    goals = stats.get("goals", {}) or {}
    shots = stats.get("shots", {}) or {}

    match_date = None
    raw_date = fixture.get("date")
    if raw_date:
        match_date = date.fromisoformat(raw_date[:10])

    minutes_raw = games.get("minutes")
    minutes = int(minutes_raw) if minutes_raw is not None else 0

    return PlayerMatchStat(
        fixture_id=fixture.get("id"),
        match_date=match_date,
        opponent=opponent,
        minutes=minutes,
        goals=_int(goals.get("total")),
        assists=_int(goals.get("assists")),
        shots=_int(shots.get("total")),
        shots_on_target=_int(shots.get("on")),
    )


def _int(value) -> int:
    if value is None:
        return 0
    return int(value)
