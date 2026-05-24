from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = "local"
    DEBUG: bool = True
    APP_NAME: str = "OPEN Project Risk API"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = (
        "postgresql+psycopg://open_project_risk:change_me@localhost:5432/"
        "open_project_risk"
    )
    DEMO_AUTH_ENABLED: bool = False
    DEMO_AUTH_USERNAME: str = ""
    DEMO_AUTH_PASSWORD: str = ""
    SECRET_KEY: str = ""
    SESSION_COOKIE_NAME: str = "open_project_risk_session"
    SESSION_TTL_SECONDS: int = 86400

    @field_validator("DEBUG", "DEMO_AUTH_ENABLED", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
