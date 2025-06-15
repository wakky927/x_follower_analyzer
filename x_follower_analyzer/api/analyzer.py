"""Main analyzer class that coordinates follower analysis."""

import time
from typing import List, Optional

from tqdm import tqdm

from ..models.config import AnalysisConfig, APICredentials
from ..models.user import FollowerAnalysis, UserProfile
from .client import XAPIClient


class FollowerAnalyzer:
    """Main class for analyzing X followers."""

    def __init__(self, credentials: APICredentials, config: AnalysisConfig):
        """Initialize the analyzer.

        Args:
            credentials: API credentials
            config: Analysis configuration
        """
        self.credentials = credentials
        self.config = config
        self.client = XAPIClient(credentials, config.rate_limit_delay)

        # Statistics
        self.stats = {
            "target_user": None,
            "total_followers": 0,
            "analyzed_followers": 0,
            "failed_profiles": 0,
            "start_time": None,
            "end_time": None,
        }

    def analyze_followers(self) -> List[FollowerAnalysis]:
        """Main method to analyze followers.

        Returns:
            List of FollowerAnalysis objects
        """
        self.stats["start_time"] = time.time()

        print(f"🎯 Starting analysis for @{self.config.target_username}")

        # Step 1: Test API connection
        if not self._test_connection():
            raise ConnectionError("Failed to connect to X API")

        # Step 2: Get target user information
        target_user = self._get_target_user()
        if not target_user:
            raise ValueError(f"User @{self.config.target_username} not found")

        # Step 3: Get follower profiles
        followers = self._get_followers(target_user.user_id)
        if not followers:
            print("❌ No followers found or unable to access followers list")
            return []

        # Step 4: Analyze each follower (get tweets and likes)
        analyses = self._analyze_follower_data(followers)

        self.stats["end_time"] = time.time()
        self._print_summary()

        return analyses

    def _test_connection(self) -> bool:
        """Test API connection."""
        print("🔗 Testing API connection...")

        if self.client.test_connection():
            print("✅ API connection successful")
            return True
        else:
            print("❌ API connection failed")
            return False

    def _get_target_user(self) -> Optional[UserProfile]:
        """Get target user profile."""
        print(f"👤 Getting profile for @{self.config.target_username}...")

        target_user = self.client.get_user_by_username(self.config.target_username)

        if target_user:
            self.stats["target_user"] = target_user
            print(
                f"✅ Found user: {target_user.display_name} (@{target_user.username})"
            )
            print(f"   Followers: {target_user.followers_count:,}")
            print(f"   Following: {target_user.following_count:,}")
            print(f"   Tweets: {target_user.tweets_count:,}")
            return target_user
        else:
            print(f"❌ User @{self.config.target_username} not found")
            return None

    def _get_followers(self, user_id: str) -> List[UserProfile]:
        """Get follower profiles for the target user."""
        print(f"📋 Getting up to {self.config.max_followers:,} followers...")

        try:
            followers = self.client.get_followers(user_id, self.config.max_followers)

            if followers:
                self.stats["total_followers"] = len(followers)
                print(f"✅ Retrieved {len(followers):,} follower profiles")
                return followers
            else:
                print("❌ No followers retrieved")
                return []

        except Exception as e:
            print(f"❌ Error getting followers: {e}")
            return []

    def _analyze_follower_data(
        self, followers: List[UserProfile]
    ) -> List[FollowerAnalysis]:
        """Analyze each follower's tweets and likes data."""
        print(f"🔍 Collecting tweets and likes for {len(followers):,} followers...")

        analyses = []
        failed_count = 0

        with tqdm(total=len(followers), desc="Collecting follower data") as pbar:
            for i, follower in enumerate(followers):
                try:
                    analysis = self._analyze_single_follower(follower)

                    if analysis:
                        analyses.append(analysis)
                        self.stats["analyzed_followers"] += 1
                    else:
                        failed_count += 1
                        self.stats["failed_profiles"] += 1

                    pbar.update(1)
                    pbar.set_postfix(
                        {
                            "success": len(analyses),
                            "failed": failed_count,
                            "rate": f"{len(analyses) / (i + 1) * 100:.1f}%",
                        }
                    )

                except KeyboardInterrupt:
                    print("\\n⚠️ Analysis interrupted by user")
                    break
                except Exception:
                    failed_count += 1
                    self.stats["failed_profiles"] += 1
                    pbar.update(1)
                    continue

        return analyses

    def _analyze_single_follower(
        self, follower: UserProfile
    ) -> Optional[FollowerAnalysis]:
        """Analyze a single follower's tweets and likes.

        Args:
            follower: UserProfile object for the follower

        Returns:
            FollowerAnalysis object or None if failed
        """
        try:
            # Get recent tweets
            recent_tweets = []
            if self.config.max_tweets_per_user > 0:
                recent_tweets = self.client.get_user_tweets(
                    follower.user_id, self.config.max_tweets_per_user
                )

            # Get liked tweets
            liked_tweets = []
            if self.config.max_liked_tweets_per_user > 0:
                liked_tweets = self.client.get_user_liked_tweets(
                    follower.user_id, self.config.max_liked_tweets_per_user
                )

            return FollowerAnalysis(
                profile=follower,
                recent_tweets=recent_tweets,
                liked_tweets=liked_tweets,
            )

        except Exception:
            # Silently fail for individual users to continue processing
            return None

    def _print_summary(self) -> None:
        """Print analysis summary."""
        duration = self.stats["end_time"] - self.stats["start_time"]

        print("\\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)

        if self.stats["target_user"]:
            user = self.stats["target_user"]
            print(f"Target User: {user.display_name} (@{user.username})")

        print(f"Total Followers: {self.stats['total_followers']:,}")
        print(f"Successfully Analyzed: {self.stats['analyzed_followers']:,}")
        print(f"Failed to Analyze: {self.stats['failed_profiles']:,}")

        if self.stats["total_followers"] > 0:
            success_rate = (
                self.stats["analyzed_followers"] / self.stats["total_followers"] * 100
            )
            print(f"Success Rate: {success_rate:.1f}%")

        print(f"Analysis Duration: {duration:.1f} seconds")

        if self.stats["analyzed_followers"] > 0:
            avg_time = duration / self.stats["analyzed_followers"]
            print(f"Average Time per Follower: {avg_time:.2f} seconds")

        print("=" * 50)
