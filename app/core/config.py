from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]  # go 2 levels up

load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://app_user:x@localhost:5432/fin_lite",
    )

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")


def get_settings():
    return Settings()


settings = get_settings()