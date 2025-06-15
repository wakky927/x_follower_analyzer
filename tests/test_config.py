"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest

from x_follower_analyzer.models.config import AnalysisConfig, OutputFormat
from x_follower_analyzer.utils.config import (
    create_analysis_config,
    get_api_credentials,
    validate_output_directory,
)


class TestCreateAnalysisConfig:
    """Test analysis configuration creation."""

    def test_valid_config_creation(self):
        """Test creating a valid configuration."""
        config = create_analysis_config(
            target_username="testuser", max_followers=500, output_format="csv"
        )

        assert config.target_username == "testuser"
        assert config.max_followers == 500
        assert config.output_format == OutputFormat.CSV
        assert config.output_file == "testuser_followers_analysis.csv"

    def test_username_cleanup(self):
        """Test username cleanup (remove @)."""
        config = create_analysis_config("@testuser")
        assert config.target_username == "testuser"

    def test_invalid_output_format(self):
        """Test invalid output format raises error."""
        with pytest.raises(ValueError, match="Invalid output format"):
            create_analysis_config("testuser", output_format="invalid")

    def test_negative_max_followers(self):
        """Test negative max_followers raises error."""
        with pytest.raises(ValueError, match="max_followers must be positive"):
            create_analysis_config("testuser", max_followers=-1)

    def test_empty_username(self):
        """Test empty username raises error."""
        with pytest.raises(ValueError, match="target_username cannot be empty"):
            create_analysis_config("")

        with pytest.raises(ValueError, match="target_username cannot be empty"):
            create_analysis_config("@")


class TestValidateOutputDirectory:
    """Test output directory validation."""

    def test_valid_directory(self):
        """Test valid directory creation and validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "subdir" / "output.csv"
            result = validate_output_directory(str(output_file))

            assert result == output_file
            assert output_file.parent.exists()

    def test_existing_directory(self):
        """Test validation with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "output.csv"
            result = validate_output_directory(str(output_file))

            assert result == output_file


class TestAPICredentials:
    """Test API credentials loading."""

    def test_missing_bearer_token(self):
        """Test that missing bearer token raises error."""
        # Clear environment variable if it exists
        old_token = os.environ.pop("X_BEARER_TOKEN", None)

        try:
            with pytest.raises(
                ValueError, match="X_BEARER_TOKEN environment variable is required"
            ):
                get_api_credentials()
        finally:
            # Restore original value if it existed
            if old_token:
                os.environ["X_BEARER_TOKEN"] = old_token

    def test_valid_credentials(self):
        """Test valid credentials loading."""
        # Set test environment variable
        os.environ["X_BEARER_TOKEN"] = "test_token"
        os.environ["X_API_KEY"] = "test_key"

        try:
            credentials = get_api_credentials()
            assert credentials.bearer_token == "test_token"
            assert credentials.api_key == "test_key"
        finally:
            # Clean up
            os.environ.pop("X_BEARER_TOKEN", None)
            os.environ.pop("X_API_KEY", None)
