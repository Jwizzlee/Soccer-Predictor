from datetime import datetime
from enum import Enum

from app.models.common import SportType
from app.models.stats import SupportingStats
from pydantic import BaseModel, Field


class PropType(str, Enum):
    GOALS = "goals"
    ASSISTS = "assists"
    SHOTS = "shots"
    SHOTS_ON_TARGET = "shots_on_target"


class Recommendation(str, Enum):
    OVER = "OVER"
    UNDER = "UNDER"


class PredictionRequest(BaseModel):
    player_id: int
    prop_type: PropType
    line: float = Field(gt=0)
    last_n_games: int = Field(default=5, ge=3, le=5)
    sport: SportType = SportType.SOCCER
    league_id: int | None = None
    season: int | None = None


class PredictionHistoryItem(BaseModel):
    id: int
    player_id: int | None = None
    league_id: int | None = None
    player_name: str
    team_name: str | None = None
    prop_type: PropType
    line: float
    recommendation: Recommendation
    confidence: int = Field(ge=0, le=100)
    hit_rate: float = Field(ge=0, le=100)
    created_at: datetime


class PredictionResponse(BaseModel):
    player_id: int
    player_name: str
    team_name: str | None = None
    sport: SportType
    prop_type: PropType
    line: float
    recommendation: Recommendation
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    key_factors: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    supporting_stats: SupportingStats
    generated_at: datetime
