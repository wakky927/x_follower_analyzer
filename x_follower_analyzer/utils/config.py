"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from ..models.config import AnalysisConfig, APICredentials, OutputFormat


def load_environment_config(env_file: Optional[str] = None) -> None:
    """Load environment variables from .env file."""
    if env_file is None:
        # Look for .env file in config directory
        config_dir = Path(__file__).parent.parent.parent / "config"
        env_file = config_dir / ".env"

    if Path(env_file).exists():
        load_dotenv(env_file)
        print(f"Loaded configuration from {env_file}")
    else:
        print(f"No .env file found at {env_file}")


def get_api_credentials() -> APICredentials:
    """Get API credentials from environment variables."""
    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError(
            "X_BEARER_TOKEN environment variable is required. "
            "Please set it in your config/.env file."
        )

    return APICredentials(
        bearer_token=bearer_token,
        api_key=os.getenv("X_API_KEY"),
        api_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
    )


def create_analysis_config(
    target_username: str,
    max_followers: int = 1000,
    max_tweets_per_user: int = 10,
    max_liked_tweets_per_user: int = 20,
    output_format: str = "csv",
    output_file: Optional[str] = None,
    include_retweets: bool = True,
    rate_limit_delay: float = 1.0,
) -> AnalysisConfig:
    """Create analysis configuration with validation."""

    # Validate and convert output format
    try:
        output_format_enum = OutputFormat(output_format.lower())
    except ValueError:
        raise ValueError(
            f"Invalid output format: {output_format}. Must be 'csv' or 'json'"
        )

    # Validate numeric parameters
    if max_followers <= 0:
        raise ValueError("max_followers must be positive")
    if max_tweets_per_user < 0:
        raise ValueError("max_tweets_per_user must be non-negative")
    if max_liked_tweets_per_user < 0:
        raise ValueError("max_liked_tweets_per_user must be non-negative")
    if rate_limit_delay < 0:
        raise ValueError("rate_limit_delay must be non-negative")

    # Clean username (remove @ if present)
    clean_username = target_username.lstrip("@")
    if not clean_username:
        raise ValueError("target_username cannot be empty")

    return AnalysisConfig(
        target_username=clean_username,
        max_followers=max_followers,
        max_tweets_per_user=max_tweets_per_user,
        max_liked_tweets_per_user=max_liked_tweets_per_user,
        output_format=output_format_enum,
        output_file=output_file,
        include_retweets=include_retweets,
        rate_limit_delay=rate_limit_delay,
    )


def validate_output_directory(output_file: str) -> Path:
    """Validate and create output directory if needed."""
    output_path = Path(output_file)
    output_dir = output_path.parent

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if we can write to the directory
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Cannot write to directory: {output_dir}")

    return output_path
