from fastapi import APIRouter, HTTPException, Query

from app.core.exceptions import ExternalAPIError
from app.models.common import SportType
from app.models.player import PlayerSummary
from app.models.stats import PlayerMatchStat
from app.services.sports.factory import get_sports_provider, init_sports_registry

router = APIRouter()


@router.get("/search", response_model=list[PlayerSummary])
async def search_players(
    q: str = Query(min_length=3, description="Player name search"),
    sport: SportType = Query(default=SportType.SOCCER),
    league_id: int | None = None,
    season: int | None = Query(default=None, description="API-Football season year"),
):
    init_sports_registry()
    provider = get_sports_provider(sport)
    try:
        return await provider.search_players(q, league_id=league_id, season=season)
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/{player_id}", response_model=PlayerSummary)
async def get_player(
    player_id: int,
    sport: SportType = Query(default=SportType.SOCCER),
    league_id: int | None = None,
    season: int | None = None,
):
    init_sports_registry()
    provider = get_sports_provider(sport)
    try:
        player = await provider.get_player(
            player_id, league_id=league_id, season=season
        )
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/{player_id}/stats", response_model=list[PlayerMatchStat])
async def get_player_stats(
    player_id: int,
    sport: SportType = Query(default=SportType.SOCCER),
    league_id: int | None = None,
    season: int | None = None,
    last_n: int = Query(default=10, ge=1, le=30),
):
    init_sports_registry()
    provider = get_sports_provider(sport)
    try:
        return await provider.get_player_recent_stats(
            player_id, last_n, league_id=league_id, season=season
        )
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
