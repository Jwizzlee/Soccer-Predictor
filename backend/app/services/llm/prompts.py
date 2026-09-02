import json

from app.models.player import PlayerSummary
from app.models.prediction import PropType
from app.models.stats import SupportingStats
from app.utils.prop_labels import get_prop_label

SYSTEM_PROMPT = """You are an elite soccer player-prop betting analyst for daily fantasy platforms (PrizePicks-style Over/Under lines).

Your job: synthesize recent per-match data into ONE clear side — OVER or UNDER — with calibrated confidence.

Rules:
- Ground every claim in the supplied stats. Cite hit rate, average, and recent game logs.
- Weight last 3 games more than older games in the window.
- Flag minutes restrictions, blanks, or tiny samples as risk_flags.
- Confidence 0.50 = coin flip; 0.65 = lean; 0.75+ = strong only when hit rate AND average both align.
- Never promise a win. Never mention bankroll or unit sizing.
- Respond with valid JSON only — no markdown, no preamble.

Required JSON schema:
{
  "recommendation": "OVER" | "UNDER",
  "confidence": <float 0.0-1.0>,
  "reasoning": "<2-3 punchy sentences a bettor would scan in 10 seconds>",
  "key_factors": ["<bullet 1>", "<bullet 2>", "<bullet 3>"],
  "risk_flags": ["<optional risks>"]
}
"""


def build_prediction_prompt(
    player: PlayerSummary,
    prop_type: PropType,
    line: float,
    supporting: SupportingStats,
    match_stats: list[dict],
    sample_note: str | None = None,
) -> str:
    label = get_prop_label(prop_type)
    hit_rate = (
        round(supporting.over_count / supporting.last_n * 100, 1)
        if supporting.last_n
        else 0
    )

    payload = {
        "task": f"Recommend OVER or UNDER on {player.name} — {label} line {line}",
        "player": {
            "name": player.name,
            "team": player.team,
            "position": player.position,
            "league": player.league_name,
        },
        "prop": {
            "type": prop_type.value,
            "label": label,
            "line": line,
        },
        "summary": {
            "games_analyzed": supporting.last_n,
            "average": supporting.average,
            "over_count": supporting.over_count,
            "under_count": supporting.under_count,
            "push_count": supporting.push_count,
            "hit_rate_pct_over": hit_rate,
            "recent_values": supporting.recent_values,
        },
        "match_log_newest_first": match_stats,
        "analysis_checklist": [
            "Does the average comfortably clear or miss the line?",
            "What is the over hit rate over the full window?",
            "Are last 3 games trending up or down vs the line?",
            "Any minutes or role concerns?",
        ],
    }
    if sample_note:
        payload["sample_note"] = sample_note
    return json.dumps(payload, indent=2, default=str)
