from fastapi import APIRouter

from app.services.sports.factory import init_sports_registry
from app.services.sports.registry import get_registered_sports

router = APIRouter()


@router.get("/health")
async def health_check():
    init_sports_registry()
    return {
        "status": "ok",
        "supported_sports": [s.value for s in get_registered_sports()],
    }
