from fastapi import APIRouter

from app.models.common import SportType
from app.services.sports.factory import init_sports_registry
from app.services.sports.registry import get_registered_sports

router = APIRouter()


@router.get("")
async def list_sports():
    init_sports_registry()
    registered = get_registered_sports()
    all_sports = [s.value for s in SportType]
    return {
        "registered": [s.value for s in registered],
        "planned": [s for s in all_sports if SportType(s) not in registered],
    }
