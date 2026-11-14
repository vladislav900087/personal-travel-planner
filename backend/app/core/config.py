from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # app
    app_env: str = "development"
    secret_key: str = "change-me-to-a-long-random-string"
    allowed_origins: str = "http://localhost:3000"

    # database
    postgres_user: str = "travel"
    postgres_password: str = "travel"
    postgres_db: str = "travel_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # jwt
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
