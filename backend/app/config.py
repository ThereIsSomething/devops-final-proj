from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://labshelf:labshelf@localhost:5432/labshelf"
    app_version: str = "dev"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
