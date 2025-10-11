from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

# Explicitly load .env file from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(..., env="BOT_TOKEN")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str | None = Field(None, env="REDIS_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")


settings = Settings()

