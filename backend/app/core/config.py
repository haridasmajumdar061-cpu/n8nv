from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Life OS"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "ailifeos"
    postgres_host: str = "db"
    postgres_port: int = 5432

    redis_url: str = "redis://redis:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/api/integrations/google/callback"
    telegram_bot_token: str = ""
    youtube_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
