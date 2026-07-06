from pydantic import BaseModel
import os


class Settings(BaseModel):
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://app_user:x@localhost:5432/fin_lite",
    )


def get_settings():
    return Settings()


settings = get_settings()