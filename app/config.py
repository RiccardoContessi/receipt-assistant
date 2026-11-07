from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    app_env: Literal["local", "test", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    llm_base_url: str
    llm_model: str
    llm_temperature: float = Field(default=0, ge=0, le=2)
    openrouter_api_key: SecretStr = Field(min_length=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
