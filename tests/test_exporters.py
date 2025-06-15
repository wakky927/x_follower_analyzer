"""Tests for data exporters."""

import csv
import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from x_follower_analyzer.exporters.csv_exporter import CSVExporter
from x_follower_analyzer.exporters.exporter_factory import ExporterFactory
from x_follower_analyzer.exporters.json_exporter import JSONExporter
from x_follower_analyzer.models.config import OutputFormat
from x_follower_analyzer.models.user import (
    FollowerAnalysis,
    LikedTweet,
    Tweet,
    UserProfile,
)


@pytest.fixture
def sample_user_profile():
    """Create a sample user profile for testing."""
    return UserProfile(
        user_id="123456789",
        username="testuser",
        display_name="Test User",
        description="Test description",
        followers_count=1000,
        following_count=500,
        tweets_count=2000,
        location="Tokyo, Japan",
        verified=False,
        created_at=datetime(2020, 1, 1),
    )


@pytest.fixture
def sample_tweets():
    """Create sample tweets for testing."""
    return [
        Tweet(
            tweet_id="1001",
            user_id="123456789",
            text="This is a test tweet #test",
            created_at=datetime(2023, 1, 1),
            retweet_count=5,
            favorite_count=10,
            reply_count=2,
            hashtags=["test"],
            mentions=["friend"],
        ),
        Tweet(
            tweet_id="1002",
            user_id="123456789",
            text="Another tweet",
            created_at=datetime(2023, 1, 2),
            retweet_count=3,
            favorite_count=7,
            reply_count=1,
            is_retweet=True,
        ),
    ]


@pytest.fixture
def sample_liked_tweets():
    """Create sample liked tweets for testing."""
    return [
        LikedTweet(
            tweet_id="2001",
            original_user_id="987654321",
            original_username="original_user",
            text="Liked tweet about healthcare",
            created_at=datetime(2023, 1, 1),
        ),
        LikedTweet(
            tweet_id="2002",
            original_user_id="987654322",
            original_username="another_user",
            text="Another liked tweet",
            created_at=datetime(2023, 1, 2),
        ),
    ]


@pytest.fixture
def sample_analysis(sample_user_profile, sample_tweets, sample_liked_tweets):
    """Create a sample follower analysis for testing."""
    return FollowerAnalysis(
        profile=sample_user_profile,
        recent_tweets=sample_tweets,
        liked_tweets=sample_liked_tweets,
    )


class TestCSVExporter:
    """Test CSV export functionality."""

    def test_csv_export(self, sample_analysis):
        """Test basic CSV export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_output.csv"
            exporter = CSVExporter(str(output_file))

            exporter.export([sample_analysis])

            # Verify file was created
            assert output_file.exists()

            # Verify content
            with open(output_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 1
                row = rows[0]

                assert row["user_id"] == "123456789"
                assert row["username"] == "testuser"
                assert row["display_name"] == "Test User"
                assert row["followers_count"] == "1000"
                assert row["recent_tweets_count"] == "2"
                assert row["liked_tweets_count"] == "2"

    def test_empty_export(self):
        """Test export with empty data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "empty_output.csv"
            exporter = CSVExporter(str(output_file))

            exporter.export([])

            # File should not be created for empty data
            assert not output_file.exists()


class TestJSONExporter:
    """Test JSON export functionality."""

    def test_json_export(self, sample_analysis):
        """Test basic JSON export functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_output.json"
            exporter = JSONExporter(str(output_file))

            exporter.export([sample_analysis])

            # Verify file was created
            assert output_file.exists()

            # Verify content
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                assert "metadata" in data
                assert "followers" in data
                assert data["metadata"]["total_followers"] == 1

                follower = data["followers"][0]
                assert follower["profile"]["user_id"] == "123456789"
                assert follower["profile"]["username"] == "testuser"
                assert len(follower["recent_tweets"]) == 2
                assert len(follower["liked_tweets"]) == 2
                assert "analysis" in follower

    def test_analysis_summary_generation(self, sample_analysis):
        """Test analysis summary generation in JSON export."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_analysis.json"
            exporter = JSONExporter(str(output_file))

            exporter.export([sample_analysis])

            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                analysis = data["followers"][0]["analysis"]

                # Check engagement metrics
                assert "engagement_metrics" in analysis
                assert "avg_retweets_per_tweet" in analysis["engagement_metrics"]
                assert "avg_favorites_per_tweet" in analysis["engagement_metrics"]

                # Check activity metrics
                assert "activity_metrics" in analysis
                assert "recent_tweets_count" in analysis["activity_metrics"]
                assert "retweet_ratio" in analysis["activity_metrics"]

                # Check classification
                assert "classification" in analysis
                assert "account_type" in analysis["classification"]
                assert "activity_level" in analysis["classification"]


class TestExporterFactory:
    """Test exporter factory functionality."""

    def test_csv_factory(self):
        """Test CSV exporter creation."""
        exporter = ExporterFactory.create_exporter(OutputFormat.CSV, "test.csv")
        assert isinstance(exporter, CSVExporter)

    def test_json_factory(self):
        """Test JSON exporter creation."""
        exporter = ExporterFactory.create_exporter(OutputFormat.JSON, "test.json")
        assert isinstance(exporter, JSONExporter)

    def test_supported_formats(self):
        """Test getting supported formats."""
        formats = ExporterFactory.get_supported_formats()
        assert "csv" in formats
        assert "json" in formats
