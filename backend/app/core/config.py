from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    sports_api_key: str = ""
    sports_api_base_url: str = "https://v3.football.api-sports.io"
    sports_api_season: int | None = 2024
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "http://localhost:5173,http://localhost:5174"
    cache_ttl_seconds: int = 300
    default_sport: str = "soccer"
    use_mock_sports_data: bool = False
    use_mock_llm: bool = False
    stripe_secret_key: str = ""
    stripe_price_id: str = ""
    stripe_webhook_secret: str = ""
    clerk_jwt_issuer: str = "https://saved-catfish-91.clerk.accounts.dev"
    clerk_secret_key: str = ""
    frontend_url: str = "http://localhost:5173"
    admin_email_whitelist: str = "bombe"

    @field_validator("sports_api_key", mode="before")
    @classmethod
    def strip_api_key(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator(
        "stripe_secret_key",
        "stripe_price_id",
        "stripe_webhook_secret",
        "clerk_jwt_issuer",
        "clerk_secret_key",
        "frontend_url",
        "admin_email_whitelist",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_email_rules(self) -> list[str]:
        return [
            rule.strip().lower()
            for rule in self.admin_email_whitelist.split(",")
            if rule.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
