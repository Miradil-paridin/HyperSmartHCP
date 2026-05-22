from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HyperLink Home"
    environment: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )
    home_assistant_url: str | None = None
    home_assistant_token: str | None = None
    mock_mode: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def use_home_assistant(self) -> bool:
        return bool(self.home_assistant_url and self.home_assistant_token and not self.mock_mode)


@lru_cache
def get_settings() -> Settings:
    return Settings()
