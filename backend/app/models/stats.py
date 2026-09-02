from datetime import date

from pydantic import BaseModel, Field


class PlayerMatchStat(BaseModel):
    fixture_id: int | None = None
    match_date: date | None = None
    opponent: str | None = None
    minutes: int = 0
    goals: int = 0
    assists: int = 0
    shots: int = 0
    shots_on_target: int = 0


class SupportingStats(BaseModel):
    last_n: int
    average: float
    over_count: int
    under_count: int
    push_count: int = 0
    recent_values: list[float] = Field(default_factory=list)
