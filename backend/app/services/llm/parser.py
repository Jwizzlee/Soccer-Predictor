from pydantic import BaseModel, Field

from app.core.exceptions import LLMError
from app.models.prediction import Recommendation


class LLMPredictionOutput(BaseModel):
    recommendation: Recommendation
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    key_factors: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


def parse_llm_response(raw: str) -> LLMPredictionOutput:
    import json

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMError(f"LLM returned invalid JSON: {exc}") from exc

    try:
        return LLMPredictionOutput.model_validate(data)
    except Exception as exc:
        raise LLMError(f"LLM output failed validation: {exc}") from exc
