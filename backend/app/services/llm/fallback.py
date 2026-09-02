"""Rule-based analyst used when OpenAI is unavailable (local testing)."""

from app.models.prediction import PropType, Recommendation
from app.models.stats import SupportingStats
from app.services.llm.parser import LLMPredictionOutput
from app.utils.prop_labels import get_prop_label


def generate_fallback_prediction(
    prop_type: PropType,
    line: float,
    supporting: SupportingStats,
    player_name: str,
) -> LLMPredictionOutput:
    label = get_prop_label(prop_type)
    total = supporting.over_count + supporting.under_count
    over_pct = supporting.over_count / total if total else 0.5
    edge = supporting.average - line

    if over_pct > 0.55 or (over_pct >= 0.5 and edge > 0.15):
        rec = Recommendation.OVER
        confidence = min(0.85, 0.5 + abs(over_pct - 0.5) + min(0.2, abs(edge) * 0.1))
    elif over_pct < 0.45 or (over_pct <= 0.5 and edge < -0.15):
        rec = Recommendation.UNDER
        confidence = min(0.85, 0.5 + abs(0.5 - over_pct) + min(0.2, abs(edge) * 0.1))
    else:
        rec = Recommendation.OVER if edge >= 0 else Recommendation.UNDER
        confidence = 0.52

    direction = "cleared" if rec == Recommendation.OVER else "stayed under"
    reasoning = (
        f"{player_name} has hit the {label} line ({line}) in "
        f"{supporting.over_count} of his last {supporting.last_n} matches "
        f"(avg {supporting.average:.2f}). Recent form {direction} the number "
        f"often enough to lean {rec.value}."
    )

    return LLMPredictionOutput(
        recommendation=rec,
        confidence=round(confidence, 2),
        reasoning=reasoning,
        key_factors=[
            f"L{supporting.last_n} hit rate: {supporting.over_count}/{supporting.last_n} overs",
            f"Average {label.lower()}: {supporting.average:.2f} vs line {line}",
            f"Last 5 values: {supporting.recent_values[:5]}",
        ],
        risk_flags=_risk_flags(supporting),
    )


def _risk_flags(supporting: SupportingStats) -> list[str]:
    flags: list[str] = []
    if supporting.last_n < 5:
        flags.append("Small sample size — fewer than 5 games in window")
    recent = supporting.recent_values[:3]
    if recent and max(recent) - min(recent) >= 3:
        flags.append("High game-to-game volatility in recent outings")
    if supporting.recent_values and supporting.recent_values[0] == 0:
        flags.append("Blanked in most recent match")
    return flags[:3]
