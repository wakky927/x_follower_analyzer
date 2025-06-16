"""Generate demo data for visualization testing."""

import random
from datetime import datetime, timedelta
from typing import List

from x_follower_analyzer.models.user import (
    FollowerAnalysis,
    UserProfile,
    Tweet,
    LikedTweet,
)


def generate_demo_data(count: int = 50) -> List[FollowerAnalysis]:
    """Generate realistic demo data for testing visualizations."""

    # Sample data pools
    locations = [
        "San Francisco, CA",
        "New York, NY",
        "Los Angeles, CA",
        "Austin, TX",
        "Seattle, WA",
        "Boston, MA",
        "Chicago, IL",
        "Miami, FL",
        "Denver, CO",
        "Global",
        "United States",
        "Canada",
        "United Kingdom",
        "Germany",
        "Japan",
        "South Korea",
        "Australia",
        "India",
        "Brazil",
        "France",
        None,
        None,
        None,  # Some users don't have location
    ]

    tech_hashtags = [
        "Tesla",
        "SpaceX",
        "AI",
        "MachineLearning",
        "Crypto",
        "Bitcoin",
        "Ethereum",
        "Tech",
        "Innovation",
        "Future",
        "Mars",
        "ElectricCars",
        "Neuralink",
        "Starlink",
        "Programming",
        "Python",
        "JavaScript",
        "Blockchain",
        "Web3",
        "Metaverse",
    ]

    sample_tweets = [
        "Excited about the future of electric vehicles! #Tesla #CleanEnergy",
        "Mars here we come! #SpaceX #Mars #Exploration",
        "AI is transforming everything we know #AI #MachineLearning #Tech",
        "Just bought more Bitcoin! #Crypto #Bitcoin #HODL",
        "The next decade will be incredible for space exploration #SpaceX",
        "Working on something revolutionary #Innovation #Tech #Future",
        "Sustainable energy is the future #Tesla #SolarPower #CleanEnergy",
        "Neural interfaces will change humanity #Neuralink #BrainTech",
        "Global internet coverage coming soon #Starlink #Internet",
        "Love seeing technological progress! #Tech #Innovation #Progress",
    ]

    usernames = [
        "techfan2024",
        "spacelover88",
        "cryptohodler",
        "airesearcher",
        "marsexplorer",
        "cleanenergyadvocate",
        "futurist2024",
        "techentrepreneur",
        "spacenerd",
        "electriccarfan",
        "blockchain_dev",
        "ml_engineer",
        "crypto_trader",
        "tech_innovator",
        "space_enthusiast",
        "ai_researcher",
        "future_builder",
        "clean_tech_fan",
        "mars_colonist",
        "tech_visionary",
        "innovation_seeker",
        "digital_nomad",
        "startup_founder",
        "tech_investor",
        "space_fan",
    ]

    display_names = [
        "Tech Enthusiast",
        "Space Explorer",
        "Crypto Trader",
        "AI Researcher",
        "Mars Explorer",
        "Clean Energy Advocate",
        "Future Visionary",
        "Tech Entrepreneur",
        "Space Nerd",
        "Electric Car Fan",
        "Blockchain Developer",
        "ML Engineer",
        "Digital Asset Pro",
        "Innovation Expert",
        "Space Enthusiast",
        "AI Scientist",
        "Future Builder",
        "CleanTech Fan",
        "Mars Colonist",
        "Tech Visionary",
    ]

    analyses = []

    for i in range(count):
        # Generate realistic follower distribution (power law)
        if random.random() < 0.1:  # 10% high-follower accounts
            followers_count = random.randint(10000, 100000)
        elif random.random() < 0.3:  # 30% medium-follower accounts
            followers_count = random.randint(1000, 10000)
        else:  # 60% regular accounts
            followers_count = random.randint(10, 1000)

        # Generate profile
        profile = UserProfile(
            user_id=str(1000000 + i),
            username=f"{random.choice(usernames)}_{i}",
            display_name=f"{random.choice(display_names)} {i + 1}",
            description="Passionate about technology and innovation. "
            "Following @elonmusk for insights.",
            followers_count=followers_count,
            following_count=random.randint(50, 2000),
            tweets_count=random.randint(100, 5000),
            location=random.choice(locations),
            verified=random.random() < 0.23,  # ~23% verification rate like demo
            created_at=datetime.now() - timedelta(days=random.randint(30, 3650)),
        )

        # Generate recent tweets
        recent_tweets = []
        tweet_count = random.randint(5, 15)
        for j in range(tweet_count):
            # Select hashtags for this tweet
            tweet_hashtags = random.sample(tech_hashtags, random.randint(0, 3))

            tweet = Tweet(
                tweet_id=str(2000000 + i * 100 + j),
                user_id=profile.user_id,
                text=random.choice(sample_tweets),
                created_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                retweet_count=random.randint(0, 50),
                favorite_count=random.randint(0, 200),
                reply_count=random.randint(0, 20),
                is_retweet=random.random() < 0.3,
                hashtags=tweet_hashtags,
            )
            recent_tweets.append(tweet)

        # Generate liked tweets
        liked_tweets = []
        liked_count = random.randint(10, 30)
        for k in range(liked_count):
            liked_tweet = LikedTweet(
                tweet_id=str(3000000 + i * 100 + k),
                original_user_id="44196397",  # Elon's user ID
                original_username="elonmusk",
                text=random.choice(sample_tweets),
                created_at=datetime.now() - timedelta(hours=random.randint(1, 720)),
                liked_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
            )
            liked_tweets.append(liked_tweet)

        analysis = FollowerAnalysis(
            profile=profile, recent_tweets=recent_tweets, liked_tweets=liked_tweets
        )
        analyses.append(analysis)

    return analyses


if __name__ == "__main__":
    # Generate demo data and create dashboard
    from x_follower_analyzer.exporters.dashboard_exporter import DashboardExporter

    print("🎯 Generating demo data...")
    demo_analyses = generate_demo_data(100)

    print("📊 Creating demo dashboard...")
    dashboard_exporter = DashboardExporter("demo_dashboard.html")
    dashboard_exporter.export(demo_analyses, target_username="elonmusk")

    print("✅ Demo dashboard created: demo_dashboard.html")
    print("🌐 Open the file in your web browser to view the visualization!")
