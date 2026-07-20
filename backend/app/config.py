"""
Curato Proposal Intelligence — Application Configuration

Centralized settings management using Pydantic BaseSettings.
All configuration is loaded from environment variables or .env file.
"""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq API ──────────────────────────────────────────
    groq_api_key: str = ""

    # ── AI Model ──────────────────────────────────────────────────────
    ai_provider: str = "groq"
    ai_model: str = "llama-3.3-70b-versatile"

    # ── Database ──────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./curato.db"

    # ── Upload Configuration ──────────────────────────────────────────
    upload_dir: str = "../uploads"
    max_file_size_mb: int = 25
    max_proposals_per_session: int = 5

    # ── Leads & Integrations ──────────────────────────────────────────
    turnstile_secret_key: str = ""
    google_sheets_credentials_json: str = ""
    google_sheets_spreadsheet_id: str = ""
    google_sheets_worksheet_name: str = ""
    valid_tools: str = "proposal-intelligence"
    session_cookie_name: str = "curato_session"
    session_expiry_days: int = 30

    # ── Server ────────────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def max_file_size_bytes(self) -> int:
        """Maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory path."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def valid_tools_list(self) -> list[str]:
        """List of valid tool identifiers."""
        return [t.strip() for t in self.valid_tools.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — created once per process."""
    return Settings()
