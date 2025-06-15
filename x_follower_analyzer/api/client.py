"""X API client with authentication and rate limiting."""

import time
from typing import List, Optional

import tweepy
from tqdm import tqdm

from ..models.config import APICredentials
from ..models.user import LikedTweet, Tweet, UserProfile


class XAPIClient:
    """X API client with rate limiting and error handling."""

    def __init__(self, credentials: APICredentials, rate_limit_delay: float = 1.0):
        """Initialize X API client.

        Args:
            credentials: API credentials
            rate_limit_delay: Delay between API calls in seconds
        """
        self.credentials = credentials
        self.rate_limit_delay = rate_limit_delay

        # Initialize Tweepy client
        self.client = tweepy.Client(
            bearer_token=credentials.bearer_token,
            consumer_key=credentials.api_key,
            consumer_secret=credentials.api_secret,
            access_token=credentials.access_token,
            access_token_secret=credentials.access_token_secret,
            wait_on_rate_limit=True,
        )

        self._last_request_time = 0.0

    def _rate_limit_wait(self) -> None:
        """Implement rate limiting between requests."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time

        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            time.sleep(sleep_time)

        self._last_request_time = time.time()

    def test_connection(self) -> bool:
        """Test API connection and credentials.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self._rate_limit_wait()
            # Try to get the authenticated user's information
            user = self.client.get_me()
            return user.data is not None
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username.

        Args:
            username: Username without @

        Returns:
            UserProfile object or None if user not found
        """
        try:
            self._rate_limit_wait()

            user = self.client.get_user(
                username=username,
                user_fields=[
                    "created_at",
                    "description",
                    "location",
                    "public_metrics",
                    "profile_image_url",
                    "url",
                    "verified",
                ],
            )

            if not user.data:
                return None

            user_data = user.data
            metrics = user_data.public_metrics or {}

            return UserProfile(
                user_id=str(user_data.id),
                username=user_data.username,
                display_name=user_data.name,
                description=user_data.description,
                followers_count=metrics.get("followers_count", 0),
                following_count=metrics.get("following_count", 0),
                tweets_count=metrics.get("tweet_count", 0),
                location=user_data.location,
                profile_image_url=user_data.profile_image_url,
                verified=user_data.verified or False,
                created_at=user_data.created_at,
                url=user_data.url,
            )

        except Exception as e:
            print(f"Error getting user {username}: {e}")
            return None

    def get_followers(self, user_id: str, max_results: int = 1000) -> List[UserProfile]:
        """Get follower profiles with full information.

        Args:
            user_id: Target user ID
            max_results: Maximum number of followers to retrieve

        Returns:
            List of UserProfile objects
        """
        followers = []

        try:
            with tqdm(desc="Getting followers", unit="followers") as pbar:
                # Use pagination to get all followers up to max_results
                paginator = tweepy.Paginator(
                    self.client.get_users_followers,
                    id=user_id,
                    max_results=min(1000, max_results),  # API limit is 1000 per request
                    limit=max(1, max_results // 1000),  # Number of pages
                    user_fields=[
                        "created_at",
                        "description",
                        "location",
                        "public_metrics",
                        "profile_image_url",
                        "url",
                        "verified",
                    ],
                )

                for page in paginator:
                    if not page.data:
                        break

                    for user_data in page.data:
                        if len(followers) >= max_results:
                            break

                        metrics = user_data.public_metrics or {}

                        profile = UserProfile(
                            user_id=str(user_data.id),
                            username=user_data.username,
                            display_name=user_data.name,
                            description=user_data.description,
                            followers_count=metrics.get("followers_count", 0),
                            following_count=metrics.get("following_count", 0),
                            tweets_count=metrics.get("tweet_count", 0),
                            location=user_data.location,
                            profile_image_url=user_data.profile_image_url,
                            verified=user_data.verified or False,
                            created_at=user_data.created_at,
                            url=user_data.url,
                        )

                        followers.append(profile)
                        pbar.update(1)

                    if len(followers) >= max_results:
                        break

                    self._rate_limit_wait()

        except Exception as e:
            print(f"Error getting followers: {e}")

        return followers[:max_results]

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> List[Tweet]:
        """Get recent tweets for a user.

        Args:
            user_id: User ID
            max_results: Maximum number of tweets to retrieve

        Returns:
            List of Tweet objects
        """
        tweets = []

        try:
            self._rate_limit_wait()

            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=[
                    "created_at",
                    "public_metrics",
                    "context_annotations",
                    "entities",
                    "referenced_tweets",
                ],
                exclude=["replies"],  # Exclude replies by default
            )

            if not response.data:
                return []

            for tweet_data in response.data:
                metrics = tweet_data.public_metrics or {}
                entities = tweet_data.entities or {}

                # Extract hashtags and mentions
                hashtags = [tag["tag"] for tag in entities.get("hashtags", [])]
                mentions = [
                    mention["username"] for mention in entities.get("mentions", [])
                ]

                # Check if it's a retweet
                is_retweet = False
                reply_to_tweet_id = None

                if tweet_data.referenced_tweets:
                    for ref in tweet_data.referenced_tweets:
                        if ref.type == "retweeted":
                            is_retweet = True
                        elif ref.type == "replied_to":
                            reply_to_tweet_id = str(ref.id)

                tweet = Tweet(
                    tweet_id=str(tweet_data.id),
                    user_id=user_id,
                    text=tweet_data.text,
                    created_at=tweet_data.created_at,
                    retweet_count=metrics.get("retweet_count", 0),
                    favorite_count=metrics.get("like_count", 0),
                    reply_count=metrics.get("reply_count", 0),
                    is_retweet=is_retweet,
                    reply_to_tweet_id=reply_to_tweet_id,
                    hashtags=hashtags,
                    mentions=mentions,
                )

                tweets.append(tweet)

        except Exception as e:
            print(f"Error getting tweets for user {user_id}: {e}")

        return tweets

    def get_user_liked_tweets(
        self, user_id: str, max_results: int = 20
    ) -> List[LikedTweet]:
        """Get tweets liked by a user.

        Args:
            user_id: User ID
            max_results: Maximum number of liked tweets to retrieve

        Returns:
            List of LikedTweet objects
        """
        liked_tweets = []

        try:
            self._rate_limit_wait()

            response = self.client.get_liked_tweets(
                id=user_id,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=["created_at", "author_id"],
                expansions=["author_id"],
                user_fields=["username"],
            )

            if not response.data:
                return []

            # Create a mapping of user IDs to usernames
            user_mapping = {}
            if (
                hasattr(response, "includes")
                and response.includes
                and "users" in response.includes
            ):
                for user in response.includes["users"]:
                    user_mapping[str(user.id)] = user.username

            for tweet_data in response.data:
                original_username = user_mapping.get(
                    str(tweet_data.author_id), "unknown"
                )

                liked_tweet = LikedTweet(
                    tweet_id=str(tweet_data.id),
                    original_user_id=str(tweet_data.author_id),
                    original_username=original_username,
                    text=tweet_data.text,
                    created_at=tweet_data.created_at,
                    liked_at=None,  # API doesn't provide when it was liked
                )

                liked_tweets.append(liked_tweet)

        except Exception as e:
            print(f"Error getting liked tweets for user {user_id}: {e}")

        return liked_tweets
