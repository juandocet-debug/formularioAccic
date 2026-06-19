from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Formulario ASIC"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_path: str = "./data/formulario_asic.sqlite3"
    database_url: str | None = None
    jwt_secret: str = "change-this-secret-before-deploy"
    jwt_expires_minutes: int = 480
    admin_username: str = "superadmin"
    admin_password: str = "change-this-password"
    cors_origins_raw: str = Field(default="http://localhost:5173", validation_alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    def validate_production_security(self) -> None:
        if self.environment != "production":
            return
        if self.jwt_secret == "change-this-secret-before-deploy":
            raise RuntimeError("JWT_SECRET debe cambiarse antes de desplegar en produccion.")
        if self.admin_password == "change-this-password":
            raise RuntimeError("ADMIN_PASSWORD debe cambiarse antes de desplegar en produccion.")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL debe apuntar a PostgreSQL en produccion.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
