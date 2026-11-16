from pathlib import Path

from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # app
    app_env: str = "development"
    secret_key: str = "change-me-to-a-long-random-string"
    allowed_origins: str = "http://localhost:3000"

    # database
    postgres_user: str = "travel"
    postgres_password: str = "travel"
    postgres_db: str = "travel_db"
    postgres_test_db: str = "travel_test_db"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5433

    @property
    def resolved_host(self) -> str:
        # fallback to localhost when running outside docker
        if self.postgres_host == "db":
            import socket

            try:
                socket.gethostbyname("db")
            except socket.gaierror:
                return "127.0.0.1"
        return self.postgres_host

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.resolved_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def test_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.resolved_host}:{self.postgres_port}/{self.postgres_test_db}"
        )

    # jwt
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    model_config = {
        "env_file": (ROOT_DIR / ".env", ".env"),
        "extra": "ignore",
    }


settings = Settings()
