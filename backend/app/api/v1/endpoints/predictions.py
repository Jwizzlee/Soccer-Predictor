from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_prediction_service
from app.core.clerk_auth import ClerkUser, get_current_clerk_user
from app.core.exceptions import AppError
from app.models.prediction import (
    PredictionHistoryItem,
    PredictionRequest,
    PredictionResponse,
    PropType,
    Recommendation,
)
from app.services.prediction_service import PredictionService
from app.services.prediction_store import prediction_store
from app.services.sports.factory import init_sports_registry

router = APIRouter()


def _parse_created_at(value: str) -> datetime:
    normalized = value.replace(" ", "T", 1)
    if normalized.endswith("Z"):
        return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    if "+" not in normalized and normalized.count(":") >= 2:
        return datetime.fromisoformat(normalized)
    return datetime.fromisoformat(normalized)


@router.get("/history", response_model=list[PredictionHistoryItem])
async def prediction_history(
    user: ClerkUser = Depends(get_current_clerk_user),
):
    """Return the signed-in user's 10 most recent predictions."""
    rows = await prediction_store.list_recent(user.user_id)
    return [
        PredictionHistoryItem(
            id=row.id,
            player_id=row.player_id,
            league_id=row.league_id,
            player_name=row.player_name,
            team_name=row.team_name,
            prop_type=PropType(row.prop_type),
            line=row.line,
            recommendation=Recommendation(row.recommendation),
            confidence=row.confidence,
            hit_rate=row.hit_rate,
            created_at=_parse_created_at(row.created_at),
        )
        for row in rows
    ]


@router.post("", response_model=PredictionResponse)
async def create_prediction(
    body: PredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
):
    init_sports_registry()
    try:
        return await service.create_prediction(body)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
