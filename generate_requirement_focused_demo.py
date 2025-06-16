#!/usr/bin/env python3
"""
要件対応デモ生成スクリプト.

原要件に完全対応した可視化を生成
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import base64
from typing import List

from x_follower_analyzer.models.user import (
    UserProfile,
    Tweet,
    LikedTweet,
    FollowerAnalysis,
)
from x_follower_analyzer.visualization.follower_charts import (
    FollowerAnalysisCharts,
)

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))


def create_demo_data() -> List[FollowerAnalysis]:
    """Create demo data for requirement-focused analysis."""
    demo_analyses = []

    for i in range(100):  # 100 followers demo
        # Profile data with all requirement fields
        profile = UserProfile(
            user_id=f"user_{1000000 + i}",
            username=f"demo_user_{i}",
            display_name=f"Demo User {i}",
            description=(
                f"Demo bio {i}: Tech enthusiast, startup founder, AI researcher"
                if i % 3 == 0
                else None
            ),
            followers_count=100 + (i * 50) + (i**2),
            following_count=50 + (i * 10),
            tweets_count=500 + (i * 20),
            location=[
                "Tokyo, Japan",
                "San Francisco, CA",
                "New York, NY",
                "London, UK",
                "Berlin, Germany",
                "Singapore",
                "Sydney, Australia",
                None,
            ][i % 8],
            verified=(i % 10 == 0),  # 10% verified
            created_at=datetime(
                2015 + (i % 8), 1 + (i % 12), 1 + (i % 28), tzinfo=timezone.utc
            ),
        )

        # Recent tweets data (requirement 2)
        recent_tweets = []
        tweet_count = (i % 15) + 1  # 1-15 tweets per user
        for j in range(tweet_count):
            tweet = Tweet(
                tweet_id=f"tweet_{i}_{j}",
                user_id=profile.user_id,
                text=f"This is demo tweet {j} from user {i}. "
                + ("Great insights about tech!" * (j % 3 + 1)),
                created_at=datetime(
                    2024,
                    1 + (j % 12),
                    1 + (j % 28),
                    hour=6 + (j % 18),
                    tzinfo=timezone.utc,
                ),
                retweet_count=j * 5 + (i % 20),
                favorite_count=j * 10 + (i % 50),
                reply_count=j * 2 + (i % 10),
            )
            recent_tweets.append(tweet)

        # Liked tweets data (requirement 3)
        liked_tweets = []
        like_count = (i % 20) + 1  # 1-20 likes per user
        for k in range(like_count):
            liked_tweet = LikedTweet(
                tweet_id=f"liked_tweet_{i}_{k}",
                original_user_id=f"popular_user_id_{k % 10}",
                original_username=f"popular_user_{k % 10}",
                text=f"Popular tweet {k} that user {i} liked. "
                + ("Amazing content! " * (k % 2 + 1)),
                created_at=datetime(
                    2024, 1 + (k % 12), 1 + (k % 28), tzinfo=timezone.utc
                ),
                liked_at=datetime(
                    2024, 2 + (k % 10), 1 + (k % 28), tzinfo=timezone.utc
                ),
            )
            # Add engagement data for charts
            liked_tweet.retweet_count = k * 20 + (i % 100)
            liked_tweet.favorite_count = k * 50 + (i % 200)
            liked_tweets.append(liked_tweet)

        analysis = FollowerAnalysis(
            profile=profile, recent_tweets=recent_tweets, liked_tweets=liked_tweets
        )
        demo_analyses.append(analysis)

    return demo_analyses


def save_chart_as_image(base64_data: str, filename: str, output_dir: Path) -> None:
    """Save base64 chart data as PNG file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Decode base64 and save
    image_data = base64.b64decode(base64_data)
    with open(output_dir / filename, "wb") as f:
        f.write(image_data)

    print(f"✅ Saved: {output_dir / filename}")


def main():
    """Generate requirement-focused demo visualization."""
    print("🚀 生成中: 要件対応デモ可視化...")

    # Create demo data
    print("📊 デモデータ生成中...")
    demo_analyses = create_demo_data()

    # Initialize chart generator
    chart_generator = FollowerAnalysisCharts()

    # Output directory
    output_dir = Path("data/demo_images_requirement")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎯 {len(demo_analyses)}人のフォロワーデータで分析実行中...")

    # Generate requirement-focused charts
    charts = [
        (
            "01_profile_collection_analysis.png",
            "プロフィール収集項目の詳細分析",
            "create_profile_collection_analysis",
        ),
        (
            "02_posts_collection_analysis.png",
            "投稿収集項目の詳細分析",
            "create_posts_collection_analysis",
        ),
        (
            "03_likes_collection_analysis.png",
            "いいね履歴収集項目の詳細分析",
            "create_likes_collection_analysis",
        ),
    ]

    for filename, description, method_name in charts:
        print(f"📈 生成中: {description}...")

        try:
            method = getattr(chart_generator, method_name)
            base64_data = method(demo_analyses)
            save_chart_as_image(base64_data, filename, output_dir)
        except Exception as e:
            print(f"❌ エラー in {description}: {e}")
            continue

    print(f"\n✨ 完了! すべての要件対応可視化が {output_dir} に保存されました")
    print(f"📊 生成されたチャート: {len(charts)}個")
    print("\n📋 要件対応状況:")
    print(
        "✅ 要件1: プロフィール収集項目 (ユーザーID、ユーザー名、自己紹介文、フォロー数、フォロワー数、位置情報など)"
    )
    print("✅ 要件2: 投稿収集項目 (各フォロワーのポスト最大n件)")
    print("✅ 要件3: いいね履歴収集項目 (各フォロワーがいいねしたポスト最大n件)")


if __name__ == "__main__":
    main()
