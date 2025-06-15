"""CSV export functionality for follower analysis data."""

import csv
from pathlib import Path
from typing import Any, Dict, List

from ..models.user import FollowerAnalysis, LikedTweet, Tweet


class CSVExporter:
    """Export follower analysis data to CSV format."""

    def __init__(self, output_file: str):
        """Initialize CSV exporter.

        Args:
            output_file: Path to output CSV file
        """
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def export(self, analyses: List[FollowerAnalysis]) -> None:
        """Export follower analyses to CSV.

        Args:
            analyses: List of FollowerAnalysis objects
        """
        if not analyses:
            print("⚠️ No data to export")
            return

        # Prepare flattened data for CSV
        rows = []
        for analysis in analyses:
            row = self._flatten_analysis(analysis)
            rows.append(row)

        # Write to CSV
        if rows:
            fieldnames = list(rows[0].keys())

            with open(self.output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"✅ CSV exported to: {self.output_file}")
            print(f"   Rows: {len(rows):,}")
            print(f"   Columns: {len(fieldnames)}")
        else:
            print("❌ No data rows to export")

    def _flatten_analysis(self, analysis: FollowerAnalysis) -> Dict[str, Any]:
        """Flatten a FollowerAnalysis object to a dictionary suitable for CSV.

        Args:
            analysis: FollowerAnalysis object

        Returns:
            Flattened dictionary
        """
        profile = analysis.profile

        # Basic profile information
        row = {
            "user_id": profile.user_id,
            "username": profile.username,
            "display_name": profile.display_name,
            "description": profile.description or "",
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "tweets_count": profile.tweets_count,
            "location": profile.location or "",
            "profile_image_url": profile.profile_image_url or "",
            "verified": profile.verified,
            "created_at": profile.created_at.isoformat() if profile.created_at else "",
            "url": profile.url or "",
        }

        # Recent tweets summary
        recent_tweets = analysis.recent_tweets or []
        row.update(
            {
                "recent_tweets_count": len(recent_tweets),
                "recent_tweets_text": self._serialize_tweets_text(recent_tweets),
                "recent_tweets_hashtags": self._extract_all_hashtags(recent_tweets),
                "recent_tweets_mentions": self._extract_all_mentions(recent_tweets),
                "avg_retweet_count": self._calculate_avg_metric(
                    recent_tweets, "retweet_count"
                ),
                "avg_favorite_count": self._calculate_avg_metric(
                    recent_tweets, "favorite_count"
                ),
                "retweet_ratio": self._calculate_retweet_ratio(recent_tweets),
            }
        )

        # Liked tweets summary
        liked_tweets = analysis.liked_tweets or []
        row.update(
            {
                "liked_tweets_count": len(liked_tweets),
                "liked_tweets_topics": self._extract_liked_topics(liked_tweets),
                "liked_tweets_authors": self._extract_liked_authors(liked_tweets),
            }
        )

        return row

    def _serialize_tweets_text(self, tweets: List[Tweet]) -> str:
        """Serialize tweet texts to a single string."""
        if not tweets:
            return ""

        # Get first 3 tweets, truncate each to 100 chars
        texts = []
        for tweet in tweets[:3]:
            text = tweet.text.replace("\n", " ").replace("\r", " ")
            if len(text) > 100:
                text = text[:97] + "..."
            texts.append(text)

        return " | ".join(texts)

    def _extract_all_hashtags(self, tweets: List[Tweet]) -> str:
        """Extract all unique hashtags from tweets."""
        hashtags = set()
        for tweet in tweets:
            hashtags.update(tweet.hashtags or [])

        return ", ".join(sorted(hashtags)[:10])  # Top 10 hashtags

    def _extract_all_mentions(self, tweets: List[Tweet]) -> str:
        """Extract all unique mentions from tweets."""
        mentions = set()
        for tweet in tweets:
            mentions.update(tweet.mentions or [])

        return ", ".join(sorted(mentions)[:10])  # Top 10 mentions

    def _calculate_avg_metric(self, tweets: List[Tweet], metric: str) -> float:
        """Calculate average metric value for tweets."""
        if not tweets:
            return 0.0

        total = sum(getattr(tweet, metric, 0) for tweet in tweets)
        return round(total / len(tweets), 2)

    def _calculate_retweet_ratio(self, tweets: List[Tweet]) -> float:
        """Calculate ratio of retweets to total tweets."""
        if not tweets:
            return 0.0

        retweet_count = sum(1 for tweet in tweets if tweet.is_retweet)
        return round(retweet_count / len(tweets), 2)

    def _extract_liked_topics(self, liked_tweets: List[LikedTweet]) -> str:
        """Extract topics from liked tweets based on keywords."""
        if not liked_tweets:
            return ""

        # Simple keyword-based topic extraction
        topics = set()
        keywords = {
            "医療": ["医療", "看護", "病院", "医師", "ナース", "患者"],
            "副業": ["副業", "サイドビジネス", "在宅ワーク", "フリーランス"],
            "教育": ["教育", "学習", "勉強", "研修", "スキル"],
            "IT": ["プログラミング", "AI", "DX", "システム", "アプリ"],
            "ビジネス": ["ビジネス", "経営", "マーケティング", "営業"],
        }

        for tweet in liked_tweets:
            text = tweet.text.lower()
            for topic, words in keywords.items():
                if any(word in text for word in words):
                    topics.add(topic)

        return ", ".join(sorted(topics))

    def _extract_liked_authors(self, liked_tweets: List[LikedTweet]) -> str:
        """Extract frequently liked authors."""
        if not liked_tweets:
            return ""

        # Count authors
        author_counts = {}
        for tweet in liked_tweets:
            author = tweet.original_username
            author_counts[author] = author_counts.get(author, 0) + 1

        # Get top 5 authors
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        return ", ".join([f"@{author}({count})" for author, count in top_authors])
