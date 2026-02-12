"""KnowYourself — Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:peterman2026@localhost:5433/knowyourself"
    ollama_url: str = "http://localhost:11434"
    supervisor_url: str = "http://localhost:9000"
    ollama_model: str = "gemma2:27b"
    app_name: str = "KnowYourself"
    app_version: str = "1.0.0"
    app_port: int = 8300
    cors_origins: str = "http://localhost:3300"
    secret_key: str = "knowyourself-amtl-2026"
    knowyourself_testing: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
