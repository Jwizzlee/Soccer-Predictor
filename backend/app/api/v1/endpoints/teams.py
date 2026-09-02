from fastapi import APIRouter, HTTPException, Query

from app.core.exceptions import ExternalAPIError
from app.models.common import SportType
from app.services.sports.factory import get_sports_provider, init_sports_registry
from app.services.sports.soccer.provider import SoccerStatsProvider

router = APIRouter()


@router.get("")
async def list_teams(
    league_id: int = Query(..., description="API-Football league ID"),
    season: int | None = None,
    sport: SportType = Query(default=SportType.SOCCER),
):
    init_sports_registry()
    provider = get_sports_provider(sport)
    if not isinstance(provider, SoccerStatsProvider):
        raise HTTPException(status_code=400, detail="Teams endpoint is soccer-only for now")
    try:
        teams = await provider.list_teams(league_id, season=season)
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"league_id": league_id, "teams": teams}


@router.get("/{team_id}/roster")
async def get_roster(
    team_id: int,
    league_id: int = Query(...),
    sport: SportType = Query(default=SportType.SOCCER),
):
    init_sports_registry()
    provider = get_sports_provider(sport)
    if not isinstance(provider, SoccerStatsProvider):
        raise HTTPException(status_code=400, detail="Roster endpoint is soccer-only for now")
    try:
        players = await provider.get_team_roster(team_id, league_id=league_id)
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return {"team_id": team_id, "league_id": league_id, "players": players}
