from fastapi import APIRouter, Query

from app.models.common import SportType
from app.services.sports.soccer.config import MVP_LEAGUES

router = APIRouter()


@router.get("")
async def list_leagues(sport: SportType = Query(default=SportType.SOCCER)):
    if sport != SportType.SOCCER:
        return {
            "sport": sport.value,
            "leagues": [],
            "message": "Leagues not configured for this sport yet",
        }

    leagues = [
        {
            "id": cfg.id,
            "name": cfg.name,
            "country": cfg.country,
            "season": cfg.season,
        }
        for cfg in MVP_LEAGUES.values()
    ]
    return {"sport": sport.value, "leagues": leagues}
