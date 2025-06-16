#!/usr/bin/env python3
"""
X Follower Analyzer - Main Entry Point

A tool to analyze X (Twitter) followers' profiles, posts, and likes history.
"""

import argparse
import sys

from x_follower_analyzer.models.config import AnalysisConfig, OutputFormat


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze X (Twitter) followers' profiles, posts, and likes"
    )

    parser.add_argument("username", help="Target X username (without @)")

    parser.add_argument(
        "--max-followers",
        type=int,
        default=1000,
        help="Maximum number of followers to analyze (default: 1000)",
    )

    parser.add_argument(
        "--max-tweets",
        type=int,
        default=10,
        help="Maximum number of recent tweets per user (default: 10)",
    )

    parser.add_argument(
        "--max-likes",
        type=int,
        default=20,
        help="Maximum number of liked tweets per user (default: 20)",
    )

    parser.add_argument(
        "--output-format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)",
    )

    parser.add_argument(
        "--output-file", help="Output file path (default: auto-generated)"
    )

    parser.add_argument(
        "--no-retweets", action="store_true", help="Exclude retweets from analysis"
    )

    parser.add_argument(
        "--rate-limit-delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)",
    )

    return parser.parse_args()


def main():
    """Main application entry point."""
    args = parse_arguments()

    # Create configuration
    config = AnalysisConfig(
        target_username=args.username,
        max_followers=args.max_followers,
        max_tweets_per_user=args.max_tweets,
        max_liked_tweets_per_user=args.max_likes,
        output_format=OutputFormat(args.output_format),
        output_file=args.output_file,
        include_retweets=not args.no_retweets,
        rate_limit_delay=args.rate_limit_delay,
    )

    print(f"Starting analysis for @{config.target_username}")
    print(f"Configuration: {config}")

    # TODO: Implement the actual analysis logic
    print("Analysis functionality will be implemented in the next steps.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
