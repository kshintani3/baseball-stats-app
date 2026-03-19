from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Database
    database_url: str = "sqlite+aiosqlite:////app/data/baseball.db"
    sqlite_database_path: str = "/app/data/baseball.db"

    # CORS — カンマ区切り文字列で受け取り、プロパティで list に変換する
    cors_origins_str: str = "http://localhost:3000,http://localhost:3001"
    cors_allow_credentials: bool = True
    cors_allow_methods_str: str = "*"
    cors_allow_headers_str: str = "*"

    # Application
    debug: bool = False
    app_name: str = "NPB Baseball Statistics API"
    app_version: str = "1.0.0"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_str.split(",") if o.strip()]

    @property
    def cors_allow_methods(self) -> list[str]:
        return [m.strip() for m in self.cors_allow_methods_str.split(",") if m.strip()]

    @property
    def cors_allow_headers(self) -> list[str]:
        return [h.strip() for h in self.cors_allow_headers_str.split(",") if h.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
