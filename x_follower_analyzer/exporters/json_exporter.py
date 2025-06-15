"""JSON export functionality for follower analysis data."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..models.user import FollowerAnalysis, LikedTweet, Tweet, UserProfile


class JSONExporter:
    """Export follower analysis data to JSON format."""

    def __init__(self, output_file: str):
        """Initialize JSON exporter.

        Args:
            output_file: Path to output JSON file
        """
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def export(self, analyses: List[FollowerAnalysis]) -> None:
        """Export follower analyses to JSON.

        Args:
            analyses: List of FollowerAnalysis objects
        """
        if not analyses:
            print("⚠️ No data to export")
            return

        # Convert to JSON-serializable format
        data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_followers": len(analyses),
                "export_format": "json",
            },
            "followers": [self._serialize_analysis(analysis) for analysis in analyses],
        }

        # Write to JSON file
        with open(self.output_file, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

        print(f"✅ JSON exported to: {self.output_file}")
        print(f"   Followers: {len(analyses):,}")

        # Calculate file size
        file_size = self.output_file.stat().st_size
        if file_size > 1024 * 1024:
            print(f"   File size: {file_size / (1024 * 1024):.1f} MB")
        else:
            print(f"   File size: {file_size / 1024:.1f} KB")

    def _serialize_analysis(self, analysis: FollowerAnalysis) -> Dict[str, Any]:
        """Serialize a FollowerAnalysis object to JSON-compatible dict.

        Args:
            analysis: FollowerAnalysis object

        Returns:
            JSON-serializable dictionary
        """
        return {
            "profile": self._serialize_profile(analysis.profile),
            "recent_tweets": [
                self._serialize_tweet(tweet) for tweet in (analysis.recent_tweets or [])
            ],
            "liked_tweets": [
                self._serialize_liked_tweet(tweet)
                for tweet in (analysis.liked_tweets or [])
            ],
            "analysis": self._generate_analysis_summary(analysis),
        }

    def _serialize_profile(self, profile: UserProfile) -> Dict[str, Any]:
        """Serialize UserProfile to dict."""
        return {
            "user_id": profile.user_id,
            "username": profile.username,
            "display_name": profile.display_name,
            "description": profile.description,
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "tweets_count": profile.tweets_count,
            "location": profile.location,
            "profile_image_url": profile.profile_image_url,
            "verified": profile.verified,
            "created_at": (
                profile.created_at.isoformat() if profile.created_at else None
            ),
            "url": profile.url,
        }

    def _serialize_tweet(self, tweet: Tweet) -> Dict[str, Any]:
        """Serialize Tweet to dict."""
        return {
            "tweet_id": tweet.tweet_id,
            "user_id": tweet.user_id,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "retweet_count": tweet.retweet_count,
            "favorite_count": tweet.favorite_count,
            "reply_count": tweet.reply_count,
            "is_retweet": tweet.is_retweet,
            "reply_to_tweet_id": tweet.reply_to_tweet_id,
            "hashtags": tweet.hashtags or [],
            "mentions": tweet.mentions or [],
        }

    def _serialize_liked_tweet(self, liked_tweet: LikedTweet) -> Dict[str, Any]:
        """Serialize LikedTweet to dict."""
        return {
            "tweet_id": liked_tweet.tweet_id,
            "original_user_id": liked_tweet.original_user_id,
            "original_username": liked_tweet.original_username,
            "text": liked_tweet.text,
            "created_at": (
                liked_tweet.created_at.isoformat() if liked_tweet.created_at else None
            ),
            "liked_at": (
                liked_tweet.liked_at.isoformat() if liked_tweet.liked_at else None
            ),
        }

    def _generate_analysis_summary(self, analysis: FollowerAnalysis) -> Dict[str, Any]:
        """Generate analysis summary for a follower."""
        profile = analysis.profile
        recent_tweets = analysis.recent_tweets or []
        liked_tweets = analysis.liked_tweets or []

        # Calculate engagement metrics
        total_retweets = sum(tweet.retweet_count for tweet in recent_tweets)
        total_favorites = sum(tweet.favorite_count for tweet in recent_tweets)
        total_replies = sum(tweet.reply_count for tweet in recent_tweets)

        # Extract topics from liked tweets
        topics = self._extract_topics_from_liked_tweets(liked_tweets)

        # Calculate activity metrics
        retweet_ratio = (
            len([t for t in recent_tweets if t.is_retweet]) / len(recent_tweets)
            if recent_tweets
            else 0
        )

        return {
            "engagement_metrics": {
                "avg_retweets_per_tweet": (
                    round(total_retweets / len(recent_tweets), 2)
                    if recent_tweets
                    else 0
                ),
                "avg_favorites_per_tweet": (
                    round(total_favorites / len(recent_tweets), 2)
                    if recent_tweets
                    else 0
                ),
                "avg_replies_per_tweet": (
                    round(total_replies / len(recent_tweets), 2) if recent_tweets else 0
                ),
                "total_engagement": total_retweets + total_favorites + total_replies,
            },
            "activity_metrics": {
                "recent_tweets_count": len(recent_tweets),
                "liked_tweets_count": len(liked_tweets),
                "retweet_ratio": round(retweet_ratio, 2),
                "follower_to_following_ratio": round(
                    profile.followers_count / max(profile.following_count, 1), 2
                ),
            },
            "content_analysis": {
                "primary_hashtags": self._extract_hashtags(recent_tweets)[:5],
                "frequent_mentions": self._extract_mentions(recent_tweets)[:5],
                "liked_content_topics": topics[:5],
                "most_liked_authors": self._extract_liked_authors(liked_tweets)[:5],
            },
            "classification": {
                "account_type": self._classify_account_type(
                    profile, recent_tweets, liked_tweets
                ),
                "activity_level": self._classify_activity_level(profile, recent_tweets),
                "engagement_level": self._classify_engagement_level(
                    total_retweets + total_favorites + total_replies, len(recent_tweets)
                ),
            },
        }

    def _extract_topics_from_liked_tweets(
        self, liked_tweets: List[LikedTweet]
    ) -> List[str]:
        """Extract topics from liked tweets using keyword analysis."""
        if not liked_tweets:
            return []

        topic_keywords = {
            "医療・看護": [
                "医療",
                "看護",
                "病院",
                "医師",
                "ナース",
                "患者",
                "治療",
                "健康",
            ],
            "副業・転職": [
                "副業",
                "サイドビジネス",
                "在宅ワーク",
                "フリーランス",
                "転職",
                "求人",
            ],
            "教育・学習": ["教育", "学習", "勉強", "研修", "スキル", "資格", "講座"],
            "IT・テック": [
                "プログラミング",
                "AI",
                "DX",
                "システム",
                "アプリ",
                "データ",
            ],
            "ビジネス": ["ビジネス", "経営", "マーケティング", "営業", "起業"],
            "ライフスタイル": [
                "ライフスタイル",
                "趣味",
                "旅行",
                "グルメ",
                "ファッション",
            ],
        }

        topic_scores = {}
        for tweet in liked_tweets:
            text = tweet.text.lower()
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                topic_scores[topic] = topic_scores.get(topic, 0) + score

        # Return topics sorted by score
        return [
            topic
            for topic, score in sorted(
                topic_scores.items(), key=lambda x: x[1], reverse=True
            )
            if score > 0
        ]

    def _extract_hashtags(self, tweets: List[Tweet]) -> List[str]:
        """Extract most frequent hashtags."""
        hashtag_counts = {}
        for tweet in tweets:
            for hashtag in tweet.hashtags or []:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1

        return [
            hashtag
            for hashtag, count in sorted(
                hashtag_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _extract_mentions(self, tweets: List[Tweet]) -> List[str]:
        """Extract most frequent mentions."""
        mention_counts = {}
        for tweet in tweets:
            for mention in tweet.mentions or []:
                mention_counts[mention] = mention_counts.get(mention, 0) + 1

        return [
            mention
            for mention, count in sorted(
                mention_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _extract_liked_authors(
        self, liked_tweets: List[LikedTweet]
    ) -> List[Dict[str, Any]]:
        """Extract most liked authors with counts."""
        author_counts = {}
        for tweet in liked_tweets:
            author = tweet.original_username
            author_counts[author] = author_counts.get(author, 0) + 1

        return [
            {"username": author, "likes_count": count}
            for author, count in sorted(
                author_counts.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _classify_account_type(
        self,
        profile: UserProfile,
        recent_tweets: List[Tweet],
        liked_tweets: List[LikedTweet],
    ) -> str:
        """Classify account type based on profile and activity."""
        description = (profile.description or "").lower()

        # Check for professional keywords
        if any(word in description for word in ["看護師", "ナース", "医療", "病院"]):
            return "healthcare_professional"
        elif any(
            word in description
            for word in ["エンジニア", "プログラマ", "developer", "IT"]
        ):
            return "tech_professional"
        elif any(word in description for word in ["経営", "CEO", "代表", "社長"]):
            return "business_executive"
        elif any(word in description for word in ["学生", "大学生"]):
            return "student"
        elif any(word in description for word in ["フリーランス", "個人事業主"]):
            return "freelancer"
        else:
            return "general_user"

    def _classify_activity_level(
        self, profile: UserProfile, recent_tweets: List[Tweet]
    ) -> str:
        """Classify activity level."""
        tweets_per_day = (
            profile.tweets_count / max((datetime.now() - profile.created_at).days, 1)
            if profile.created_at
            else 0
        )

        if tweets_per_day > 5:
            return "very_active"
        elif tweets_per_day > 1:
            return "active"
        elif tweets_per_day > 0.1:
            return "moderate"
        else:
            return "low_activity"

    def _classify_engagement_level(
        self, total_engagement: int, tweet_count: int
    ) -> str:
        """Classify engagement level."""
        if tweet_count == 0:
            return "no_recent_tweets"

        avg_engagement = total_engagement / tweet_count

        if avg_engagement > 100:
            return "high_engagement"
        elif avg_engagement > 10:
            return "medium_engagement"
        elif avg_engagement > 1:
            return "low_engagement"
        else:
            return "minimal_engagement"
