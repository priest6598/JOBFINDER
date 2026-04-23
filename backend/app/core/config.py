from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite+aiosqlite:///./pathai.db"
    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    JWT_ALGORITHM: str = "HS256"

    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-5"

    FRONTEND_URL: str = "http://localhost:3000"
    STORAGE_DIR: str = "./storage"

    FREE_TAILORED_RESUMES_PER_MONTH: int = 2
    FREE_COVER_LETTERS_PER_MONTH: int = 2
    FREE_MOCK_INTERVIEWS_PER_WEEK: int = 1
    FREE_DAILY_MATCH_LIMIT: int = 20

    STARTER_CREDITS: int = 3

    @property
    def storage_path(self) -> Path:
        p = Path(self.STORAGE_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
