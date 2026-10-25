import os


class Settings:
    APP_NAME = "Datheon FastAPI Backend"
    APP_VERSION = "1.0.0"

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./datheon.db")

    HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5.0"))
    RATE_LIMIT_TIMES = int(os.getenv("RATE_LIMIT_TIMES", "5"))
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


settings = Settings()
