import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_prediction_service, require_active_subscription
from app.core.clerk_auth import ClerkUser
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from app.services.prediction_store import prediction_store
from app.services.sports.factory import init_sports_registry
from app.services.sports.soccer.mock_data import list_mock_player_ids

logger = logging.getLogger(__name__)

router = APIRouter()


async def _save_prediction_history(
    user: ClerkUser,
    result: PredictionResponse,
    request: PredictionRequest,
) -> None:
    stats = result.supporting_stats
    hit_rate = (
        round((stats.over_count / stats.last_n) * 100, 1) if stats.last_n else 0.0
    )
    await prediction_store.insert_prediction(
        clerk_user_id=user.user_id,
        player_id=result.player_id,
        league_id=request.league_id,
        player_name=result.player_name,
        team_name=result.team_name,
        prop_type=result.prop_type.value,
        line=result.line,
        recommendation=result.recommendation.value,
        confidence=round(result.confidence * 100),
        hit_rate=hit_rate,
    )


@router.post("", response_model=PredictionResponse)
async def predict(
    body: PredictionRequest,
    user: ClerkUser = Depends(require_active_subscription),
    service: PredictionService = Depends(get_prediction_service),
):
    """Over/Under recommendation for a player prop. Mock IDs: 1001–1004 when USE_MOCK_SPORTS_DATA=true."""
    init_sports_registry()
    try:
        result = await service.create_prediction(body)
    except AppError as exc:
        traceback.print_exc()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

    try:
        await _save_prediction_history(user, result, body)
    except Exception:
        logger.exception("Failed to save prediction history for user %s", user.user_id)

    return result


@router.get("/info")
async def predict_info():
    settings = get_settings()
    return {
        "endpoint": "POST /api/v1/predict",
        "mock_sports_data": settings.use_mock_sports_data,
        "mock_llm": settings.use_mock_llm or not bool(settings.openai_api_key),
        "openai_model": settings.openai_model,
        "mock_player_ids": list_mock_player_ids() if settings.use_mock_sports_data else [],
        "prop_types": ["goals", "assists", "shots", "shots_on_target"],
    }
