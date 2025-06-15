"""Configuration data models."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OutputFormat(Enum):
    """Supported output formats."""

    CSV = "csv"
    JSON = "json"
    DASHBOARD = "html"


@dataclass
class APICredentials:
    """X API credentials."""

    bearer_token: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None


@dataclass
class AnalysisConfig:
    """Configuration for follower analysis."""

    target_username: str
    max_followers: int = 1000
    max_tweets_per_user: int = 10
    max_liked_tweets_per_user: int = 20
    output_format: OutputFormat = OutputFormat.CSV
    output_file: Optional[str] = None
    include_retweets: bool = True
    rate_limit_delay: float = 1.0  # seconds between API calls

    def __post_init__(self) -> None:
        if self.output_file is None:
            self.output_file = (
                f"{self.target_username}_followers_analysis.{self.output_format.value}"
            )
