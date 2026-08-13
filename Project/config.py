"""
Central configuration for the AI-Powered Code Review Pipeline.

Associates only edit the .env file (GEMINI_API_KEY, GEMINI_MODEL, and — only for the
optional GitHub-PR input path — GITHUB_TOKEN). Every other setting lives here.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class SystemConfig:
    """All system settings in one place."""

    # From .env — the model values every associate configures
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    # Optional — only needed for the GitHub-PR input path
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_api_url: str = os.getenv("GITHUB_API_URL", "https://api.github.com")

    # Project folders
    samples_dir: str = str(PROJECT_ROOT / "samples")

    # Persistence (SQLite)
    review_db_path: str = str(PROJECT_ROOT / "reviews.db")          # completed-review history
    checkpoint_db_path: str = str(PROJECT_ROOT / "checkpoints.db")  # durable HITL checkpointer

    # Quality-gate thresholds
    security_threshold: float = 8.0
    pylint_threshold: float = 7.0
    coverage_threshold: float = 80.0
    ai_confidence_threshold: float = 0.8
    documentation_threshold: float = 70.0


config = SystemConfig()


def validate_config() -> bool:
    """Check critical settings. Raises ValueError when something is wrong."""
    if not config.gemini_api_key or config.gemini_api_key.lower().startswith("your"):
        raise ValueError("GEMINI_API_KEY is missing. Paste your key into the .env file.")
    if not config.gemini_model:
        raise ValueError("GEMINI_MODEL is missing. Set it in the .env file.")
    return True
