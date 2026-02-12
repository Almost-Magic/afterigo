"""Ripple CRM — Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/ripple"
    redis_url: str = "redis://localhost:6379/0"
    ollama_url: str = "http://localhost:11434"
    supervisor_url: str = "http://localhost:9000"
    app_name: str = "Ripple CRM"
    app_version: str = "3.0.0"
    app_port: int = 8100
    cors_origins: str = "http://localhost:3100"
    secret_key: str = "change-me-in-production"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
