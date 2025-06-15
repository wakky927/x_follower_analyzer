"""Tests for data models."""

from datetime import datetime

import pytest

from x_follower_analyzer.models.config import (
    AnalysisConfig,
    APICredentials,
    OutputFormat,
)
from x_follower_analyzer.models.user import (
    FollowerAnalysis,
    LikedTweet,
    Tweet,
    UserProfile,
)


class TestUserProfile:
    """Test UserProfile model."""

    def test_user_profile_creation(self):
        """Test creating a user profile."""
        profile = UserProfile(
            user_id="123456789",
            username="testuser",
            display_name="Test User",
            description="Test description",
            followers_count=1000,
            following_count=500,
            tweets_count=2000,
        )

        assert profile.user_id == "123456789"
        assert profile.username == "testuser"
        assert profile.display_name == "Test User"
        assert profile.followers_count == 1000
        assert profile.following_count == 500
        assert profile.tweets_count == 2000

    def test_user_profile_optional_fields(self):
        """Test user profile with optional fields."""
        profile = UserProfile(
            user_id="123456789",
            username="testuser",
            display_name="Test User",
        )

        assert profile.description is None
        assert profile.location is None
        assert profile.verified is False
        assert profile.followers_count == 0


class TestTweet:
    """Test Tweet model."""

    def test_tweet_creation(self):
        """Test creating a tweet."""
        tweet = Tweet(
            tweet_id="1001",
            user_id="123456789",
            text="This is a test tweet",
            created_at=datetime(2023, 1, 1),
        )

        assert tweet.tweet_id == "1001"
        assert tweet.user_id == "123456789"
        assert tweet.text == "This is a test tweet"
        assert tweet.created_at == datetime(2023, 1, 1)
        assert tweet.hashtags == []
        assert tweet.mentions == []

    def test_tweet_with_hashtags_mentions(self):
        """Test tweet with hashtags and mentions."""
        tweet = Tweet(
            tweet_id="1001",
            user_id="123456789",
            text="Test tweet",
            created_at=datetime(2023, 1, 1),
            hashtags=["test", "python"],
            mentions=["friend1", "friend2"],
        )

        assert tweet.hashtags == ["test", "python"]
        assert tweet.mentions == ["friend1", "friend2"]


class TestLikedTweet:
    """Test LikedTweet model."""

    def test_liked_tweet_creation(self):
        """Test creating a liked tweet."""
        liked_tweet = LikedTweet(
            tweet_id="2001",
            original_user_id="987654321",
            original_username="original_user",
            text="This is a liked tweet",
            created_at=datetime(2023, 1, 1),
        )

        assert liked_tweet.tweet_id == "2001"
        assert liked_tweet.original_user_id == "987654321"
        assert liked_tweet.original_username == "original_user"
        assert liked_tweet.text == "This is a liked tweet"


class TestFollowerAnalysis:
    """Test FollowerAnalysis model."""

    def test_follower_analysis_creation(self):
        """Test creating a follower analysis."""
        profile = UserProfile(
            user_id="123456789",
            username="testuser",
            display_name="Test User",
        )

        analysis = FollowerAnalysis(profile=profile)

        assert analysis.profile == profile
        assert analysis.recent_tweets == []
        assert analysis.liked_tweets == []

    def test_follower_analysis_with_data(self):
        """Test follower analysis with tweets and likes."""
        profile = UserProfile(
            user_id="123456789",
            username="testuser",
            display_name="Test User",
        )

        tweets = [
            Tweet(
                tweet_id="1001",
                user_id="123456789",
                text="Test tweet",
                created_at=datetime(2023, 1, 1),
            )
        ]

        liked_tweets = [
            LikedTweet(
                tweet_id="2001",
                original_user_id="987654321",
                original_username="original_user",
                text="Liked tweet",
                created_at=datetime(2023, 1, 1),
            )
        ]

        analysis = FollowerAnalysis(
            profile=profile,
            recent_tweets=tweets,
            liked_tweets=liked_tweets,
        )

        assert len(analysis.recent_tweets) == 1
        assert len(analysis.liked_tweets) == 1


class TestAnalysisConfig:
    """Test AnalysisConfig model."""

    def test_analysis_config_creation(self):
        """Test creating analysis configuration."""
        config = AnalysisConfig(
            target_username="testuser",
            max_followers=500,
            output_format=OutputFormat.CSV,
        )

        assert config.target_username == "testuser"
        assert config.max_followers == 500
        assert config.output_format == OutputFormat.CSV
        assert config.output_file == "testuser_followers_analysis.csv"

    def test_analysis_config_json_format(self):
        """Test analysis configuration with JSON format."""
        config = AnalysisConfig(
            target_username="testuser",
            output_format=OutputFormat.JSON,
        )

        assert config.output_file == "testuser_followers_analysis.json"


class TestAPICredentials:
    """Test APICredentials model."""

    def test_api_credentials_creation(self):
        """Test creating API credentials."""
        credentials = APICredentials(
            bearer_token="test_bearer_token",
            api_key="test_api_key",
            api_secret="test_api_secret",
        )

        assert credentials.bearer_token == "test_bearer_token"
        assert credentials.api_key == "test_api_key"
        assert credentials.api_secret == "test_api_secret"

    def test_api_credentials_minimal(self):
        """Test API credentials with only bearer token."""
        credentials = APICredentials(bearer_token="test_bearer_token")

        assert credentials.bearer_token == "test_bearer_token"
        assert credentials.api_key is None
        assert credentials.api_secret is None
