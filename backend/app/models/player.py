from app.models.common import SportType
from pydantic import BaseModel, Field


class PlayerSummary(BaseModel):
    id: int
    name: str
    team: str
    team_id: int | None = None
    position: str | None = None
    photo_url: str | None = None
    league_id: int | None = None
    league_name: str | None = None
    sport: SportType = SportType.SOCCER
