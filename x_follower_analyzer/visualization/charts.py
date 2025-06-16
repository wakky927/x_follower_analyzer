"""Chart generation utilities for follower analysis visualization."""

import io
import base64
from typing import List, Dict, Any, Tuple

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
import numpy as np

from ..models.user import FollowerAnalysis


class ChartGenerator:
    """Generate various charts and visualizations for follower analysis."""

    def __init__(self, style: str = "seaborn-v0_8", figsize: Tuple[int, int] = (12, 8)):
        """Initialize chart generator with style settings."""
        self.style = style
        self.figsize = figsize
        plt.style.use(style)
        sns.set_palette("husl")

    def create_follower_distribution_chart(
        self, analyses: List[FollowerAnalysis]
    ) -> str:
        """Create follower count distribution chart."""
        follower_counts = [analysis.profile.followers_count for analysis in analyses]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)

        # Histogram
        ax1.hist(
            follower_counts, bins=20, alpha=0.7, color="skyblue", edgecolor="black"
        )
        ax1.set_xlabel("Follower Count")
        ax1.set_ylabel("Number of Users")
        ax1.set_title("Distribution of Follower Counts")
        ax1.grid(True, alpha=0.3)

        # Box plot
        ax2.boxplot(follower_counts, vert=True)
        ax2.set_ylabel("Follower Count")
        ax2.set_title("Follower Count Statistics")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_verification_pie_chart(self, analyses: List[FollowerAnalysis]) -> str:
        """Create pie chart showing verified vs non-verified users."""
        verified_count = sum(1 for analysis in analyses if analysis.profile.verified)
        total_count = len(analyses)
        non_verified_count = total_count - verified_count

        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ["Verified", "Non-Verified"]
        sizes = [verified_count, non_verified_count]
        colors = ["#1DA1F2", "#657786"]

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
        )
        ax.set_title("Account Verification Status", fontsize=16, fontweight="bold")

        return self._save_plot_as_base64()

    def create_location_analysis_chart(self, analyses: List[FollowerAnalysis]) -> str:
        """Create horizontal bar chart for top locations."""
        locations = [
            analysis.profile.location
            for analysis in analyses
            if analysis.profile.location
        ]

        if not locations:
            return self._create_no_data_chart("No location data available")

        location_counts = pd.Series(locations).value_counts().head(10)

        fig, ax = plt.subplots(figsize=self.figsize)
        colors = plt.cm.Set3(np.linspace(0, 1, len(location_counts)))

        bars = ax.barh(
            range(len(location_counts)), location_counts.values, color=colors
        )
        ax.set_yticks(range(len(location_counts)))
        ax.set_yticklabels(location_counts.index)
        ax.set_xlabel("Number of Followers")
        ax.set_title("Top 10 Follower Locations", fontsize=16, fontweight="bold")

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(
                width + 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                ha="left",
                va="center",
            )

        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_engagement_analysis_chart(self, analyses: List[FollowerAnalysis]) -> str:
        """Create scatter plot for follower count vs tweet count analysis."""
        data = []
        for analysis in analyses:
            if analysis.recent_tweets:
                data.append(
                    {
                        "followers_count": analysis.profile.followers_count,
                        "tweets_count": len(analysis.recent_tweets),
                        "avg_retweets": np.mean(
                            [tweet.retweet_count for tweet in analysis.recent_tweets]
                        ),
                        "avg_likes": np.mean(
                            [tweet.favorite_count for tweet in analysis.recent_tweets]
                        ),
                    }
                )

        if not data:
            return self._create_no_data_chart(
                "No tweet data available for engagement analysis"
            )

        df = pd.DataFrame(data)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Followers vs Tweet Count
        ax1.scatter(df["followers_count"], df["tweets_count"], alpha=0.6, color="blue")
        ax1.set_xlabel("Follower Count")
        ax1.set_ylabel("Recent Tweet Count")
        ax1.set_title("Follower Count vs Tweet Activity")
        ax1.grid(True, alpha=0.3)

        # Average Retweets Distribution
        ax2.hist(
            df["avg_retweets"], bins=15, alpha=0.7, color="green", edgecolor="black"
        )
        ax2.set_xlabel("Average Retweets")
        ax2.set_ylabel("Number of Users")
        ax2.set_title("Distribution of Average Retweets")
        ax2.grid(True, alpha=0.3)

        # Average Likes Distribution
        ax3.hist(df["avg_likes"], bins=15, alpha=0.7, color="red", edgecolor="black")
        ax3.set_xlabel("Average Likes")
        ax3.set_ylabel("Number of Users")
        ax3.set_title("Distribution of Average Likes")
        ax3.grid(True, alpha=0.3)

        # Retweets vs Likes
        ax4.scatter(df["avg_retweets"], df["avg_likes"], alpha=0.6, color="purple")
        ax4.set_xlabel("Average Retweets")
        ax4.set_ylabel("Average Likes")
        ax4.set_title("Retweets vs Likes Correlation")
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_hashtag_wordcloud(self, analyses: List[FollowerAnalysis]) -> str:
        """Create word cloud from hashtags in recent tweets."""
        hashtags = []
        for analysis in analyses:
            if analysis.recent_tweets:
                for tweet in analysis.recent_tweets:
                    if tweet.hashtags:
                        hashtags.extend(tweet.hashtags)

        if not hashtags:
            return self._create_no_data_chart("No hashtag data available")

        hashtag_text = " ".join(hashtags)

        fig, ax = plt.subplots(figsize=self.figsize)

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=100,
            relative_scaling=0.5,
        ).generate(hashtag_text)

        ax.imshow(wordcloud, interpolation="bilinear")
        ax.set_title("Most Common Hashtags", fontsize=16, fontweight="bold")
        ax.axis("off")

        return self._save_plot_as_base64()

    def create_activity_timeline_chart(self, analyses: List[FollowerAnalysis]) -> str:
        """Create timeline chart showing tweet posting patterns."""
        tweet_times = []
        for analysis in analyses:
            if analysis.recent_tweets:
                for tweet in analysis.recent_tweets:
                    if tweet.created_at:
                        tweet_times.append(tweet.created_at.hour)

        if not tweet_times:
            return self._create_no_data_chart("No tweet timing data available")

        fig, ax = plt.subplots(figsize=self.figsize)

        # Create hourly distribution
        hour_counts = pd.Series(tweet_times).value_counts().sort_index()
        hours = range(24)
        counts = [hour_counts.get(hour, 0) for hour in hours]

        bars = ax.bar(hours, counts, color="lightcoral", alpha=0.7, edgecolor="black")
        ax.set_xlabel("Hour of Day (UTC)")
        ax.set_ylabel("Number of Tweets")
        ax.set_title("Tweet Activity by Hour of Day", fontsize=16, fontweight="bold")
        ax.set_xticks(range(0, 24, 2))
        ax.grid(True, alpha=0.3)

        # Highlight peak hours
        peak_hour = counts.index(max(counts))
        bars[peak_hour].set_color("red")
        bars[peak_hour].set_alpha(1.0)

        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_interactive_dashboard_data(
        self, analyses: List[FollowerAnalysis]
    ) -> Dict[str, Any]:
        """Create data structure for interactive Plotly dashboard."""
        # Prepare data for various charts
        follower_data = []
        for analysis in analyses:
            data = {
                "username": analysis.profile.username,
                "display_name": analysis.profile.display_name,
                "followers_count": analysis.profile.followers_count,
                "following_count": analysis.profile.following_count,
                "tweets_count": analysis.profile.tweets_count,
                "verified": analysis.profile.verified,
                "location": analysis.profile.location or "Unknown",
                "description": analysis.profile.description or "",
                "recent_tweets_count": (
                    len(analysis.recent_tweets) if analysis.recent_tweets else 0
                ),
                "liked_tweets_count": (
                    len(analysis.liked_tweets) if analysis.liked_tweets else 0
                ),
            }

            if analysis.recent_tweets:
                data["avg_retweets"] = np.mean(
                    [t.retweet_count for t in analysis.recent_tweets]
                )
                data["avg_likes"] = np.mean(
                    [t.favorite_count for t in analysis.recent_tweets]
                )
            else:
                data["avg_retweets"] = 0
                data["avg_likes"] = 0

            follower_data.append(data)

        return follower_data

    def _save_plot_as_base64(self) -> str:
        """Save current matplotlib plot as base64 encoded string."""
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return image_base64

    def _create_no_data_chart(self, message: str) -> str:
        """Create a simple chart indicating no data available."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(
            0.5,
            0.5,
            message,
            transform=ax.transAxes,
            fontsize=16,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"),
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        return self._save_plot_as_base64()
