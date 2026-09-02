from fastapi import APIRouter

from app.api.v1.endpoints import billing, health, leagues, players, predict, predictions, sports, teams

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(sports.router, prefix="/sports", tags=["sports"])
api_router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(predict.router, prefix="/predict", tags=["predict"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
