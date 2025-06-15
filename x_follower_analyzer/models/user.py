"""User profile data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class UserProfile:
    """X user profile information."""

    user_id: str
    username: str
    display_name: str
    description: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    tweets_count: int = 0
    location: Optional[str] = None
    profile_image_url: Optional[str] = None
    verified: bool = False
    created_at: Optional[datetime] = None
    url: Optional[str] = None


@dataclass
class Tweet:
    """Tweet/Post information."""

    tweet_id: str
    user_id: str
    text: str
    created_at: datetime
    retweet_count: int = 0
    favorite_count: int = 0
    reply_count: int = 0
    is_retweet: bool = False
    reply_to_tweet_id: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []


@dataclass
class LikedTweet:
    """Information about tweets liked by a user."""

    tweet_id: str
    original_user_id: str
    original_username: str
    text: str
    created_at: datetime
    liked_at: Optional[datetime] = None


@dataclass
class FollowerAnalysis:
    """Complete analysis data for a follower."""

    profile: UserProfile
    recent_tweets: Optional[List[Tweet]] = None
    liked_tweets: Optional[List[LikedTweet]] = None

    def __post_init__(self) -> None:
        if self.recent_tweets is None:
            self.recent_tweets = []
        if self.liked_tweets is None:
            self.liked_tweets = []
