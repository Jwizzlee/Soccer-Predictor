from datetime import datetime, timezone

from app.core.exceptions import InsufficientDataError, NotFoundError
from app.models.common import SportType
from app.models.prediction import PredictionRequest, PredictionResponse
from app.models.stats import PlayerMatchStat
from app.services.llm.client import OpenAIClient
from app.services.llm.prompts import build_prediction_prompt
from app.services.sports.factory import get_sports_provider
from app.services.sports.soccer.provider import SoccerStatsProvider
from app.services.stats_aggregator import compute_supporting_stats

RATE_LIMIT_USER_MESSAGE = (
    "Sports data is temporarily rate-limited (10 requests/min on the free plan). "
    "Please wait about a minute, avoid searching players right before analyzing, "
    "and keep Last N games at 5 or fewer."
)


class PredictionService:
    def __init__(self, llm_client: OpenAIClient | None = None):
        self._llm = llm_client or OpenAIClient()

    async def create_prediction(
        self, request: PredictionRequest
    ) -> PredictionResponse:
        provider = get_sports_provider(request.sport)

        player = await provider.get_player(
            request.player_id,
            league_id=request.league_id,
            season=request.season,
        )
        if not player:
            raise NotFoundError(f"Player {request.player_id} not found")

        sample_note: str | None = None
        if request.sport == SportType.SOCCER and isinstance(provider, SoccerStatsProvider):
            stats_result = await provider.get_player_recent_stats_result(
                request.player_id,
                request.last_n_games,
                league_id=request.league_id,
                season=request.season,
            )
            match_stats = stats_result.stats
            if stats_result.rate_limited and not match_stats:
                raise InsufficientDataError(RATE_LIMIT_USER_MESSAGE)
            if stats_result.rate_limited and len(match_stats) < 3:
                raise InsufficientDataError(
                    f"Only {len(match_stats)} recent game(s) could be loaded before "
                    "the API rate limit was reached. "
                    f"{RATE_LIMIT_USER_MESSAGE}"
                )
            if stats_result.rate_limited and len(match_stats) < stats_result.requested_games:
                sample_note = (
                    f"Note: requested {stats_result.requested_games} games but only "
                    f"{len(match_stats)} were available before the API per-minute rate "
                    "limit was hit. Weight conclusions accordingly."
                )
        else:
            match_stats = await provider.get_player_recent_stats(
                request.player_id,
                request.last_n_games,
                league_id=request.league_id,
                season=request.season,
            )

        if len(match_stats) < 3:
            raise InsufficientDataError(
                f"Need at least 3 games; found {len(match_stats)}"
            )

        supporting = compute_supporting_stats(
            provider, match_stats, request.prop_type, request.line
        )

        match_dicts = [_stat_to_dict(s) for s in match_stats]
        prompt = build_prediction_prompt(
            player,
            request.prop_type,
            request.line,
            supporting,
            match_dicts,
            sample_note=sample_note,
        )

        llm_output = await self._llm.generate_prediction(
            prompt,
            prop_type=request.prop_type,
            line=request.line,
            supporting=supporting,
            player_name=player.name,
        )

        return PredictionResponse(
            player_id=player.id,
            player_name=player.name,
            team_name=player.team,
            sport=request.sport,
            prop_type=request.prop_type,
            line=request.line,
            recommendation=llm_output.recommendation,
            confidence=llm_output.confidence,
            reasoning=llm_output.reasoning,
            key_factors=llm_output.key_factors,
            risk_flags=llm_output.risk_flags,
            supporting_stats=supporting,
            generated_at=datetime.now(timezone.utc),
        )


def _stat_to_dict(stat: PlayerMatchStat) -> dict:
    return {
        "date": str(stat.match_date) if stat.match_date else None,
        "opponent": stat.opponent,
        "minutes": stat.minutes,
        "goals": stat.goals,
        "assists": stat.assists,
        "shots": stat.shots,
        "shots_on_target": stat.shots_on_target,
    }
