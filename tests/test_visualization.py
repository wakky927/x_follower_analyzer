"""Tests for visualization functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from x_follower_analyzer.models.user import FollowerAnalysis, UserProfile, Tweet
from x_follower_analyzer.visualization.charts import ChartGenerator
from x_follower_analyzer.visualization.dashboard import DashboardGenerator
from x_follower_analyzer.exporters.dashboard_exporter import DashboardExporter


class TestChartGenerator:
    """Test chart generation functionality."""

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analysis data for testing."""
        analyses = []
        for i in range(5):
            profile = UserProfile(
                user_id=str(i),
                username=f"user_{i}",
                display_name=f"User {i}",
                followers_count=1000 + i * 100,
                following_count=500,
                tweets_count=100,
                verified=i % 2 == 0,
                location="San Francisco" if i < 3 else "New York"
            )
            
            from datetime import datetime
            tweets = [
                Tweet(
                    tweet_id=f"{i}_1",
                    user_id=str(i),
                    text=f"Sample tweet from user {i}",
                    created_at=datetime.now(),
                    hashtags=["tech", "ai"] if i % 2 == 0 else ["crypto"]
                )
            ]
            
            analyses.append(FollowerAnalysis(profile=profile, recent_tweets=tweets))
        
        return analyses

    def test_chart_generator_initialization(self):
        """Test chart generator can be initialized."""
        generator = ChartGenerator()
        assert generator.style == "seaborn-v0_8"
        assert generator.figsize == (12, 8)

    def test_follower_distribution_chart(self, sample_analyses):
        """Test follower distribution chart generation."""
        generator = ChartGenerator()
        chart_data = generator.create_follower_distribution_chart(sample_analyses)
        assert isinstance(chart_data, str)
        assert len(chart_data) > 0  # Should have base64 data

    def test_verification_pie_chart(self, sample_analyses):
        """Test verification pie chart generation."""
        generator = ChartGenerator()
        chart_data = generator.create_verification_pie_chart(sample_analyses)
        assert isinstance(chart_data, str)
        assert len(chart_data) > 0

    def test_location_analysis_chart(self, sample_analyses):
        """Test location analysis chart generation."""
        generator = ChartGenerator()
        chart_data = generator.create_location_analysis_chart(sample_analyses)
        assert isinstance(chart_data, str)
        assert len(chart_data) > 0

    def test_hashtag_wordcloud(self, sample_analyses):
        """Test hashtag word cloud generation."""
        generator = ChartGenerator()
        chart_data = generator.create_hashtag_wordcloud(sample_analyses)
        assert isinstance(chart_data, str)
        assert len(chart_data) > 0

    def test_interactive_dashboard_data(self, sample_analyses):
        """Test interactive dashboard data generation."""
        generator = ChartGenerator()
        data = generator.create_interactive_dashboard_data(sample_analyses)
        assert isinstance(data, list)
        assert len(data) == 5
        assert "username" in data[0]
        assert "followers_count" in data[0]


class TestDashboardGenerator:
    """Test dashboard generation functionality."""

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analysis data for testing."""
        profile = UserProfile(
            user_id="1",
            username="test_user",
            display_name="Test User",
            followers_count=1000,
            following_count=500,
            tweets_count=100,
            verified=True,
            location="Test City"
        )
        
        from datetime import datetime
        tweet = Tweet(
            tweet_id="1",
            user_id="1",
            text="Test tweet",
            created_at=datetime.now(),
            hashtags=["test"]
        )
        
        return [FollowerAnalysis(profile=profile, recent_tweets=[tweet])]

    def test_dashboard_generator_initialization(self):
        """Test dashboard generator can be initialized."""
        generator = DashboardGenerator()
        assert generator.chart_generator is not None

    def test_generate_dashboard(self, sample_analyses):
        """Test dashboard generation."""
        generator = DashboardGenerator()
        
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            output_path = generator.generate_dashboard(
                analyses=sample_analyses,
                target_username="test_user",
                output_path=tmp.name
            )
            
            assert Path(output_path).exists()
            content = Path(output_path).read_text()
            assert "X Follower Analysis Dashboard" in content
            assert "test_user" in content
            assert "Total Followers Analyzed" in content


class TestDashboardExporter:
    """Test dashboard exporter functionality."""

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analysis data for testing."""
        profile = UserProfile(
            user_id="1",
            username="test_user",
            display_name="Test User",
            followers_count=1000,
            following_count=500,
            tweets_count=100,
            verified=True
        )
        
        return [FollowerAnalysis(profile=profile)]

    def test_dashboard_exporter_initialization(self):
        """Test dashboard exporter can be initialized."""
        exporter = DashboardExporter("test.html")
        assert exporter.output_file == "test.html"
        assert exporter.dashboard_generator is not None

    def test_export_dashboard(self, sample_analyses):
        """Test dashboard export functionality."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            exporter = DashboardExporter(tmp.name)
            
            # Should not raise exception
            exporter.export(sample_analyses, target_username="test_user")
            
            # Check file was created and has content
            assert Path(tmp.name).exists()
            content = Path(tmp.name).read_text()
            assert len(content) > 1000  # Should be substantial HTML content

    def test_export_empty_analyses(self):
        """Test export with empty analyses list."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            exporter = DashboardExporter(tmp.name)
            
            # Should handle empty list gracefully
            exporter.export([], target_username="test_user")