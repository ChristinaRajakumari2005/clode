from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AI Governance & Compliance Copilot API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Gemini AI Integration Settings
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    model_name: str = Field(default="gemini-2.5-flash", alias="MODEL_NAME")
    request_timeout: float = Field(default=30.0, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    max_output_tokens: int = Field(default=2048, alias="MAX_OUTPUT_TOKENS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
