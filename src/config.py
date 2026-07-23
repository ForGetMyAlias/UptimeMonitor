from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Uptime Monitor"
    DATABASE_URL: str = "postgresql+asyncpg://uptime_user:uptime_password@localhost:5432/uptime_db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()