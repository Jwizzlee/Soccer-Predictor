"""Deterministic mock players and match logs for local development."""

from dataclasses import dataclass
from datetime import date, timedelta
import random

from app.models.player import PlayerSummary
from app.models.common import SportType
from app.models.stats import PlayerMatchStat
@dataclass(frozen=True)
class MockPlayer:
    summary: PlayerSummary
    opponents: tuple[str, ...]
    # Per-game base rates (mean); noise applied per fixture
    goals_rate: float
    assists_rate: float
    shots_rate: float
    sog_rate: float


MOCK_PLAYERS: dict[int, MockPlayer] = {
    1001: MockPlayer(
        summary=PlayerSummary(
            id=1001,
            name="Erling Haaland",
            team="Manchester City",
            team_id=50,
            position="Attacker",
            photo_url=None,
            league_id=39,
            league_name="Premier League",
            sport=SportType.SOCCER,
        ),
        opponents=("Arsenal", "Chelsea", "Liverpool", "Tottenham", "Newcastle", "Brighton"),
        goals_rate=0.9,
        assists_rate=0.15,
        shots_rate=3.8,
        sog_rate=2.1,
    ),
    1002: MockPlayer(
        summary=PlayerSummary(
            id=1002,
            name="Vinícius Júnior",
            team="Real Madrid",
            team_id=541,
            position="Attacker",
            photo_url=None,
            league_id=140,
            league_name="La Liga",
            sport=SportType.SOCCER,
        ),
        opponents=("Barcelona", "Atlético Madrid", "Sevilla", "Villarreal", "Betis", "Girona"),
        goals_rate=0.45,
        assists_rate=0.35,
        shots_rate=2.6,
        sog_rate=1.4,
    ),
    1003: MockPlayer(
        summary=PlayerSummary(
            id=1003,
            name="Mohamed Salah",
            team="Liverpool",
            team_id=40,
            position="Attacker",
            photo_url=None,
            league_id=39,
            league_name="Premier League",
            sport=SportType.SOCCER,
        ),
        opponents=("Man City", "Chelsea", "Arsenal", "Everton", "West Ham", "Aston Villa"),
        goals_rate=0.55,
        assists_rate=0.4,
        shots_rate=3.2,
        sog_rate=1.6,
    ),
    1004: MockPlayer(
        summary=PlayerSummary(
            id=1004,
            name="Robert Lewandowski",
            team="Barcelona",
            team_id=529,
            position="Attacker",
            photo_url=None,
            league_id=140,
            league_name="La Liga",
            sport=SportType.SOCCER,
        ),
        opponents=("Real Madrid", "Atlético Madrid", "Sevilla", "Valencia", "Osasuna", "Mallorca"),
        goals_rate=0.65,
        assists_rate=0.2,
        shots_rate=3.0,
        sog_rate=1.5,
    ),
}


def list_mock_player_ids() -> list[int]:
    return list(MOCK_PLAYERS.keys())


def generate_match_stats(player_id: int, last_n: int) -> list[PlayerMatchStat]:
    """Simulate recent per-match stats with reproducible variance."""
    mock = MOCK_PLAYERS.get(player_id)
    if not mock:
        return []

    rng = random.Random(player_id * 9973 + last_n)
    today = date.today()
    stats: list[PlayerMatchStat] = []

    for i in range(last_n):
        minutes = rng.randint(65, 90) if rng.random() > 0.1 else rng.randint(20, 60)
        scale = minutes / 90.0

        goals = _poissonish(rng, mock.goals_rate * scale)
        assists = _poissonish(rng, mock.assists_rate * scale)
        shots = max(goals, _poissonish(rng, mock.shots_rate * scale))
        sog = min(shots, max(goals, _poissonish(rng, mock.sog_rate * scale)))

        stats.append(
            PlayerMatchStat(
                fixture_id=player_id * 10_000 + i,
                match_date=today - timedelta(days=7 * (i + 1)),
                opponent=mock.opponents[i % len(mock.opponents)],
                minutes=minutes,
                goals=goals,
                assists=assists,
                shots=shots,
                shots_on_target=sog,
            )
        )

    return stats


def _poissonish(rng: random.Random, lam: float) -> int:
    """Simple count draw for low-rate soccer stats."""
    if lam <= 0:
        return 0
    # Inverse transform-ish via repeated Bernoulli for small lambda
    count = 0
    p = min(1.0, lam / 3.0)
    for _ in range(8):
        if rng.random() < p:
            count += 1
    return count


def search_mock_players(query: str, league_id: int | None = None) -> list[PlayerSummary]:
    q = query.lower().strip()
    results: list[PlayerSummary] = []
    for mock in MOCK_PLAYERS.values():
        p = mock.summary
        if league_id and p.league_id != league_id:
            continue
        if q in p.name.lower() or q in p.team.lower():
            results.append(p)
    return results
