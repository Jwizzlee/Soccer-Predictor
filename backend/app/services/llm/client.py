from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.models.prediction import PropType
from app.models.stats import SupportingStats
from app.services.llm.fallback import generate_fallback_prediction
from app.services.llm.parser import LLMPredictionOutput, parse_llm_response
from app.services.llm.prompts import SYSTEM_PROMPT


class OpenAIClient:
    """OpenAI wrapper for GPT-4o-mini prop recommendations."""

    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.openai_model
        self._use_fallback = settings.use_mock_llm or not settings.openai_api_key
        self._client = (
            None if self._use_fallback else AsyncOpenAI(api_key=settings.openai_api_key)
        )

    @property
    def using_fallback(self) -> bool:
        return self._use_fallback

    async def generate_prediction(
        self,
        user_prompt: str,
        *,
        prop_type: PropType | None = None,
        line: float | None = None,
        supporting: SupportingStats | None = None,
        player_name: str = "Player",
    ) -> LLMPredictionOutput:
        if self._use_fallback:
            if prop_type is None or line is None or supporting is None:
                raise LLMError(
                    "Fallback analyst requires prop_type, line, and supporting stats"
                )
            return generate_fallback_prediction(
                prop_type, line, supporting, player_name
            )

        try:
            response = await self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._model,
                temperature=0.25,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Analyze this soccer player prop and return JSON per the schema.\n\n"
                            f"{user_prompt}"
                        ),
                    },
                ],
            )
        except Exception as exc:
            raise LLMError(f"OpenAI request failed: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMError("OpenAI returned empty response")

        return parse_llm_response(content)
