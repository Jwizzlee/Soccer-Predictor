from app.models.prediction import PropType

PROP_LABELS: dict[PropType, str] = {
    PropType.GOALS: "Goals",
    PropType.ASSISTS: "Assists",
    PropType.SHOTS: "Shots",
    PropType.SHOTS_ON_TARGET: "Shots on Target",
}


def get_prop_label(prop_type: PropType) -> str:
    return PROP_LABELS.get(prop_type, prop_type.value)
