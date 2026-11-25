"""Runtime configuration for the FedCure API."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def _postgres_driver_url(url: str) -> str:
    """Use SQLAlchemy's psycopg v3 driver for Render Postgres URLs."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    jwt_secret: str | None
    registration_token: str | None
    allowed_origins: tuple[str, ...]
    required_hospitals: int
    access_token_minutes: int

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = tuple(
            origin.strip().rstrip("/")
            for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        )
        return cls(
            app_env=os.getenv("APP_ENV", "development").lower(),
            database_url=_postgres_driver_url(
                os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'fedcure.db'}")
            ),
            jwt_secret=os.getenv("JWT_SECRET"),
            registration_token=os.getenv("REGISTRATION_TOKEN"),
            allowed_origins=origins,
            required_hospitals=int(os.getenv("REQUIRED_HOSPITALS", "4")),
            access_token_minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "480")),
        )

    def validate_for_startup(self) -> None:
        if self.required_hospitals < 2:
            raise RuntimeError("REQUIRED_HOSPITALS must be at least 2.")
        if self.access_token_minutes < 1:
            raise RuntimeError("ACCESS_TOKEN_MINUTES must be positive.")
        if not self.jwt_secret or len(self.jwt_secret) < 32:
            raise RuntimeError("JWT_SECRET must be at least 32 characters.")
        if not self.registration_token or len(self.registration_token) < 32:
            raise RuntimeError("REGISTRATION_TOKEN must be at least 32 characters.")
        if self.app_env == "production" and (
            not self.allowed_origins or "*" in self.allowed_origins
        ):
            raise RuntimeError(
                "ALLOWED_ORIGINS must contain explicit HTTPS frontend origins in production."
            )


settings = Settings.from_environment()
