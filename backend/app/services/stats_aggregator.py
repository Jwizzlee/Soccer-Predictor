from app.models.prediction import PropType
from app.models.stats import PlayerMatchStat, SupportingStats
from app.services.sports.base import SportsStatsProvider


def compute_supporting_stats(
    provider: SportsStatsProvider,
    match_stats: list[PlayerMatchStat],
    prop_type: PropType,
    line: float,
) -> SupportingStats:
    values = [provider.extract_prop_value(s, prop_type) for s in match_stats]
    last_n = len(values)

    over = sum(1 for v in values if v > line)
    under = sum(1 for v in values if v < line)
    push = sum(1 for v in values if v == line)
    average = sum(values) / last_n if last_n else 0.0

    return SupportingStats(
        last_n=last_n,
        average=round(average, 2),
        over_count=over,
        under_count=under,
        push_count=push,
        recent_values=values,
    )
