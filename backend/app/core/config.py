from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Biply ERP"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://biply:biply@localhost:5432/biply"
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:8080,http://127.0.0.1:8080"
    admin_email: str = "admin@example.com"
    admin_password: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self) -> list[str]: return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

@lru_cache
def get_settings() -> Settings: return Settings()
settings = get_settings()
