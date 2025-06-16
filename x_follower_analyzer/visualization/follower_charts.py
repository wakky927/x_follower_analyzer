"""Specialized charts for follower analysis based on initial requirements."""

import io
import base64
from typing import List, Tuple
from collections import Counter
import re

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from ..models.user import FollowerAnalysis


class FollowerAnalysisCharts:
    """Generate specialized charts for follower analysis requirements.

    対応要件:
    1. プロフィール収集項目: ユーザーID、ユーザー名、自己紹介文、フォロー数、フォロワー数、位置情報など
    2. 投稿収集項目: 各フォロワーのポスト（最大n件）
    3. いいね履歴収集項目: 各フォロワーが「いいね」したポスト（最大n件）
    """

    def __init__(self, style: str = "seaborn-v0_8", figsize: Tuple[int, int] = (12, 8)):
        """Initialize chart generator with style settings."""
        self.style = style
        self.figsize = figsize
        plt.style.use(style)
        sns.set_palette("husl")

        # 日本語フォント設定
        try:
            import japanize_matplotlib
            japanize_matplotlib.japanize()
        except ImportError:
            pass

        # 直接フォント設定 - macOSで確実に利用可能
        plt.rcParams["font.family"] = [
            "Hiragino Sans",
            "Hiragino Maru Gothic Pro",
            "AppleGothic",
        ]
        plt.rcParams["font.sans-serif"] = [
            "Hiragino Sans",
            "Hiragino Maru Gothic Pro",
            "AppleGothic",
            "DejaVu Sans",
        ]

        # 文字化け対策
        plt.rcParams["axes.unicode_minus"] = False

        # フォントキャッシュクリア
        try:
            import matplotlib.font_manager
            matplotlib.font_manager._rebuild()
        except Exception:
            pass

    def create_profile_collection_analysis(
        self, analyses: List[FollowerAnalysis]
    ) -> str:
        """要件1: プロフィール収集項目の詳細分析 - ユーザーID、ユーザー名、自己紹介文、フォロー数、フォロワー数、位置情報など"""
        fig = plt.figure(figsize=(20, 16))

        # Extract profile data
        user_ids = [a.profile.user_id for a in analyses]
        usernames = [a.profile.username for a in analyses]
        descriptions = [
            a.profile.description for a in analyses if a.profile.description
        ]
        follower_counts = [a.profile.followers_count for a in analyses]
        following_counts = [a.profile.following_count for a in analyses]
        locations = [a.profile.location for a in analyses if a.profile.location]
        verified_status = [a.profile.verified for a in analyses]

        # Create subplot grid
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])

        # 1. ユーザーID分析 - ID長さ分布
        ax1 = fig.add_subplot(gs[0, 0])
        id_lengths = [len(uid) for uid in user_ids]
        ax1.hist(id_lengths, bins=15, alpha=0.7, color="#1DA1F2", edgecolor="black")
        ax1.set_xlabel("ユーザーID文字数")
        ax1.set_ylabel("ユーザー数")
        ax1.set_title("ユーザーID長さ分布", fontsize=12, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # 2. ユーザー名分析 - 名前長さ分布
        ax2 = fig.add_subplot(gs[0, 1])
        username_lengths = [len(un) for un in usernames]
        ax2.hist(
            username_lengths, bins=15, alpha=0.7, color="#17BF63", edgecolor="black"
        )
        ax2.set_xlabel("ユーザー名文字数")
        ax2.set_ylabel("ユーザー数")
        ax2.set_title("ユーザー名長さ分布", fontsize=12, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        # 3. 自己紹介文分析 - 設定率と長さ
        ax3 = fig.add_subplot(gs[0, 2])
        desc_ratio = len(descriptions) / len(analyses) * 100
        no_desc_ratio = 100 - desc_ratio
        ax3.pie(
            [desc_ratio, no_desc_ratio],
            labels=[
                f"自己紹介あり\n({desc_ratio:.1f}%)",
                f"自己紹介なし\n({no_desc_ratio:.1f}%)",
            ],
            colors=["#FF6B6B", "#BDC3C7"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax3.set_title("自己紹介文設定率", fontsize=12, fontweight="bold")

        # 4. フォロワー数分布（対数スケール）
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.hist(
            follower_counts, bins=30, alpha=0.7, color="#9B59B6", edgecolor="black"
        )
        ax4.set_xlabel("フォロワー数")
        ax4.set_ylabel("ユーザー数")
        ax4.set_title("フォロワー数分布", fontsize=12, fontweight="bold")
        ax4.set_xscale("log")
        ax4.grid(True, alpha=0.3)

        # 5. フォロー数分布
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.hist(
            following_counts, bins=30, alpha=0.7, color="#F39C12", edgecolor="black"
        )
        ax5.set_xlabel("フォロー数")
        ax5.set_ylabel("ユーザー数")
        ax5.set_title("フォロー数分布", fontsize=12, fontweight="bold")
        ax5.grid(True, alpha=0.3)

        # 6. 位置情報分析 - 設定率と上位地域
        ax6 = fig.add_subplot(gs[1, 2])
        location_ratio = len(locations) / len(analyses) * 100
        no_location_ratio = 100 - location_ratio
        ax6.pie(
            [location_ratio, no_location_ratio],
            labels=[
                f"位置情報あり\n({location_ratio:.1f}%)",
                f"位置情報なし\n({no_location_ratio:.1f}%)",
            ],
            colors=["#2ECC71", "#E74C3C"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax6.set_title("位置情報設定率", fontsize=12, fontweight="bold")

        # 7. 認証済みアカウント分析
        ax7 = fig.add_subplot(gs[2, 0])
        verified_count = sum(verified_status)
        unverified_count = len(analyses) - verified_count
        ax7.bar(
            ["認証済み", "未認証"],
            [verified_count, unverified_count],
            color=["#1DA1F2", "#95A5A6"],
            alpha=0.8,
            edgecolor="black",
        )
        ax7.set_ylabel("ユーザー数")
        ax7.set_title("アカウント認証状況", fontsize=12, fontweight="bold")
        ax7.grid(True, alpha=0.3)

        # 8. フォロー/フォロワー比率分析
        ax8 = fig.add_subplot(gs[2, 1])
        ratios = [
            following / max(1, followers)
            for followers, following in zip(follower_counts, following_counts)
        ]
        ax8.hist(ratios, bins=20, alpha=0.7, color="#E67E22", edgecolor="black")
        ax8.set_xlabel("フォロー/フォロワー比率")
        ax8.set_ylabel("ユーザー数")
        ax8.set_title("フォロー/フォロワー比率分布", fontsize=12, fontweight="bold")
        ax8.set_xscale("log")
        ax8.grid(True, alpha=0.3)

        # 9. プロフィール完成度分析
        ax9 = fig.add_subplot(gs[2, 2])
        profile_scores = []
        for analysis in analyses:
            score = 0
            if analysis.profile.description:
                score += 1
            if analysis.profile.location:
                score += 1
            if analysis.profile.verified:
                score += 1
            if analysis.profile.followers_count > 0:
                score += 1
            if analysis.profile.following_count > 0:
                score += 1
            profile_scores.append(score)

        score_counts = Counter(profile_scores)
        scores = list(range(6))
        counts = [score_counts.get(s, 0) for s in scores]

        ax9.bar(scores, counts, color="#3498DB", alpha=0.8, edgecolor="black")
        ax9.set_xlabel("プロフィール完成度スコア")
        ax9.set_ylabel("ユーザー数")
        ax9.set_title("プロフィール完成度分布", fontsize=12, fontweight="bold")
        ax9.set_xticks(scores)
        ax9.grid(True, alpha=0.3)

        plt.suptitle(
            "要件1: プロフィール収集項目の詳細分析",
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_bio_analysis_chart(self, analyses: List[FollowerAnalysis]) -> str:
        """Analyze follower bio/description text."""
        # Extract and analyze bio texts
        bios = [a.profile.description for a in analyses if a.profile.description]

        if not bios:
            return self._create_no_data_chart("自己紹介文データがありません")

        # Common keywords in bios
        bio_text = " ".join(bios).lower()
        # Remove common stop words and extract meaningful terms
        keywords = re.findall(r"\b[a-zA-Z日本語]{3,}\b", bio_text)
        keyword_counts = Counter(keywords).most_common(20)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Bio length distribution
        bio_lengths = [len(bio) for bio in bios]
        ax1.hist(bio_lengths, bins=20, alpha=0.7, color="#FF6B6B", edgecolor="black")
        ax1.set_xlabel("自己紹介文の文字数")
        ax1.set_ylabel("ユーザー数")
        ax1.set_title("自己紹介文の長さ分布", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # Top keywords
        if keyword_counts:
            words, counts = zip(*keyword_counts[:15])
            y_pos = np.arange(len(words))
            ax2.barh(y_pos, counts, color="#4ECDC4")
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(words)
            ax2.set_xlabel("出現回数")
            ax2.set_title("自己紹介文の頻出キーワード", fontsize=14, fontweight="bold")
            ax2.grid(True, alpha=0.3)

        plt.suptitle("フォロワー自己紹介文分析", fontsize=16, fontweight="bold")
        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_posts_collection_analysis(self, analyses: List[FollowerAnalysis]) -> str:
        """要件2: 投稿収集項目の詳細分析 - 各フォロワーのポスト（最大n件）"""
        fig = plt.figure(figsize=(20, 16))

        # Extract posting data
        all_tweets = []
        user_post_counts = []
        tweet_texts = []
        tweet_dates = []
        tweet_engagement = []

        for analysis in analyses:
            post_count = len(analysis.recent_tweets) if analysis.recent_tweets else 0
            user_post_counts.append(post_count)

            if analysis.recent_tweets:
                for tweet in analysis.recent_tweets:
                    all_tweets.append(tweet)
                    tweet_texts.append(tweet.text)
                    if hasattr(tweet, "created_at") and tweet.created_at:
                        tweet_dates.append(tweet.created_at)
                    engagement = tweet.retweet_count + tweet.favorite_count
                    tweet_engagement.append(engagement)

        # Create subplot grid
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])

        # 1. ユーザー別投稿数分布
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(
            user_post_counts, bins=20, alpha=0.7, color="#3498DB", edgecolor="black"
        )
        ax1.set_xlabel("収集投稿数")
        ax1.set_ylabel("フォロワー数")
        ax1.set_title("フォロワー別収集投稿数分布", fontsize=12, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # 2. 投稿収集状況
        ax2 = fig.add_subplot(gs[0, 1])
        users_with_posts = sum(1 for count in user_post_counts if count > 0)
        users_without_posts = len(analyses) - users_with_posts
        ax2.pie(
            [users_with_posts, users_without_posts],
            labels=[
                f"投稿収集済み\n({users_with_posts}人)",
                f"投稿未収集\n({users_without_posts}人)",
            ],
            colors=["#2ECC71", "#E74C3C"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax2.set_title("投稿収集状況", fontsize=12, fontweight="bold")

        # 3. 投稿文字数分布
        ax3 = fig.add_subplot(gs[0, 2])
        if tweet_texts:
            text_lengths = [len(text) for text in tweet_texts]
            ax3.hist(
                text_lengths, bins=20, alpha=0.7, color="#9B59B6", edgecolor="black"
            )
            ax3.set_xlabel("投稿文字数")
            ax3.set_ylabel("投稿数")
            ax3.set_title("収集投稿の文字数分布", fontsize=12, fontweight="bold")
            ax3.axvline(
                x=140, color="red", linestyle="--", alpha=0.7, label="旧Twitter制限"
            )
            ax3.axvline(x=280, color="orange", linestyle="--", alpha=0.7, label="X制限")
            ax3.legend()
            ax3.grid(True, alpha=0.3)

        # 4. エンゲージメント（RT+いいね）分布
        ax4 = fig.add_subplot(gs[1, 0])
        if tweet_engagement:
            ax4.hist(
                tweet_engagement, bins=30, alpha=0.7, color="#E67E22", edgecolor="black"
            )
            ax4.set_xlabel("エンゲージメント数（RT+いいね）")
            ax4.set_ylabel("投稿数")
            ax4.set_title(
                "収集投稿のエンゲージメント分布", fontsize=12, fontweight="bold"
            )
            ax4.set_xscale("log")
            ax4.grid(True, alpha=0.3)

        # 5. 時間帯別投稿分析
        ax5 = fig.add_subplot(gs[1, 1])
        if tweet_dates:
            hours = [date.hour for date in tweet_dates if hasattr(date, "hour")]
            if hours:
                ax5.hist(hours, bins=24, alpha=0.7, color="#F39C12", edgecolor="black")
                ax5.set_xlabel("時間（24時間制）")
                ax5.set_ylabel("投稿数")
                ax5.set_title("収集投稿の時間帯分布", fontsize=12, fontweight="bold")
                ax5.set_xticks(range(0, 24, 4))
                ax5.grid(True, alpha=0.3)

        # 6. 投稿タイプ分析（リプライ、リツイート、オリジナル）
        ax6 = fig.add_subplot(gs[1, 2])
        if tweet_texts:
            reply_count = sum(1 for text in tweet_texts if text.startswith("@"))
            rt_count = sum(1 for text in tweet_texts if text.startswith("RT @"))
            original_count = len(tweet_texts) - reply_count - rt_count

            ax6.pie(
                [original_count, reply_count, rt_count],
                labels=["オリジナル", "リプライ", "リツイート"],
                colors=["#1ABC9C", "#3498DB", "#E74C3C"],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax6.set_title("収集投稿のタイプ分布", fontsize=12, fontweight="bold")

        # 7. 高エンゲージメント投稿分析
        ax7 = fig.add_subplot(gs[2, 0])
        if tweet_engagement:
            high_engagement = [
                e for e in tweet_engagement if e > np.percentile(tweet_engagement, 90)
            ]
            medium_engagement = [
                e
                for e in tweet_engagement
                if np.percentile(tweet_engagement, 50)
                < e
                <= np.percentile(tweet_engagement, 90)
            ]
            low_engagement = [
                e for e in tweet_engagement if e <= np.percentile(tweet_engagement, 50)
            ]

            categories = [
                "高エンゲージメント\n(上位10%)",
                "中エンゲージメント\n(50-90%)",
                "低エンゲージメント\n(下位50%)",
            ]
            counts = [len(high_engagement), len(medium_engagement), len(low_engagement)]

            ax7.bar(
                categories,
                counts,
                color=["#E74C3C", "#F39C12", "#95A5A6"],
                alpha=0.8,
                edgecolor="black",
            )
            ax7.set_ylabel("投稿数")
            ax7.set_title(
                "エンゲージメントレベル別投稿数", fontsize=12, fontweight="bold"
            )
            ax7.grid(True, alpha=0.3)

        # 8. 投稿頻度vs品質分析
        ax8 = fig.add_subplot(gs[2, 1])
        if user_post_counts and tweet_engagement:
            user_avg_engagement = {}
            for analysis in analyses:
                if analysis.recent_tweets:
                    avg_eng = np.mean(
                        [
                            t.retweet_count + t.favorite_count
                            for t in analysis.recent_tweets
                        ]
                    )
                    user_avg_engagement[analysis.profile.username] = (
                        len(analysis.recent_tweets),
                        avg_eng,
                    )

            if user_avg_engagement:
                post_counts_plot = [data[0] for data in user_avg_engagement.values()]
                avg_engagements = [data[1] for data in user_avg_engagement.values()]

                ax8.scatter(
                    post_counts_plot, avg_engagements, alpha=0.6, color="#8E44AD", s=50
                )
                ax8.set_xlabel("収集投稿数")
                ax8.set_ylabel("平均エンゲージメント")
                ax8.set_title(
                    "投稿数vs平均エンゲージメント相関", fontsize=12, fontweight="bold"
                )
                ax8.grid(True, alpha=0.3)

        # 9. 収集効率統計
        ax9 = fig.add_subplot(gs[2, 2])
        total_users = len(analyses)
        total_posts = len(all_tweets)
        avg_posts_per_user = total_posts / max(1, total_users)
        successful_collections = users_with_posts
        collection_rate = successful_collections / total_users * 100

        stats_text = f"""収集統計:
・対象フォロワー数: {total_users:,}人
・総収集投稿数: {total_posts:,}件
・平均投稿数/人: {avg_posts_per_user:.1f}件
・収集成功率: {collection_rate:.1f}%
・最大投稿数: {max(user_post_counts):,}件
・最小投稿数: {min(user_post_counts):,}件"""

        ax9.text(
            0.05,
            0.95,
            stats_text,
            transform=ax9.transAxes,
            fontsize=11,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
        )
        ax9.set_xlim(0, 1)
        ax9.set_ylim(0, 1)
        ax9.axis("off")
        ax9.set_title("投稿収集統計サマリー", fontsize=12, fontweight="bold")

        plt.suptitle(
            "要件2: 投稿収集項目の詳細分析（各フォロワーのポスト最大n件）",
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_likes_collection_analysis(self, analyses: List[FollowerAnalysis]) -> str:
        """要件3: いいね履歴収集項目の詳細分析 - 各フォロワーが「いいね」したポスト（最大n件）"""
        fig = plt.figure(figsize=(20, 16))

        # Extract likes data
        all_liked_tweets = []
        user_like_counts = []
        liked_tweet_texts = []
        liked_tweet_authors = []
        liked_tweet_engagement = []

        for analysis in analyses:
            like_count = len(analysis.liked_tweets) if analysis.liked_tweets else 0
            user_like_counts.append(like_count)

            if analysis.liked_tweets:
                for liked_tweet in analysis.liked_tweets:
                    all_liked_tweets.append(liked_tweet)
                    liked_tweet_texts.append(liked_tweet.text)
                    liked_tweet_authors.append(liked_tweet.original_username)
                    engagement = liked_tweet.retweet_count + liked_tweet.favorite_count
                    liked_tweet_engagement.append(engagement)

        # Create subplot grid
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])

        # 1. ユーザー別いいね数分布
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(
            user_like_counts, bins=20, alpha=0.7, color="#E91E63", edgecolor="black"
        )
        ax1.set_xlabel("収集いいね数")
        ax1.set_ylabel("フォロワー数")
        ax1.set_title("フォロワー別収集いいね数分布", fontsize=12, fontweight="bold")
        ax1.grid(True, alpha=0.3)

        # 2. いいね収集状況
        ax2 = fig.add_subplot(gs[0, 1])
        users_with_likes = sum(1 for count in user_like_counts if count > 0)
        users_without_likes = len(analyses) - users_with_likes
        ax2.pie(
            [users_with_likes, users_without_likes],
            labels=[
                f"いいね収集済み\n({users_with_likes}人)",
                f"いいね未収集\n({users_without_likes}人)",
            ],
            colors=["#FF4081", "#607D8B"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax2.set_title("いいね収集状況", fontsize=12, fontweight="bold")

        # 3. いいね対象ツイート文字数分布
        ax3 = fig.add_subplot(gs[0, 2])
        if liked_tweet_texts:
            text_lengths = [len(text) for text in liked_tweet_texts]
            ax3.hist(
                text_lengths, bins=20, alpha=0.7, color="#795548", edgecolor="black"
            )
            ax3.set_xlabel("いいね対象ツイート文字数")
            ax3.set_ylabel("ツイート数")
            ax3.set_title(
                "いいね対象ツイートの文字数分布", fontsize=12, fontweight="bold"
            )
            ax3.axvline(
                x=140, color="red", linestyle="--", alpha=0.7, label="旧Twitter制限"
            )
            ax3.axvline(x=280, color="orange", linestyle="--", alpha=0.7, label="X制限")
            ax3.legend()
            ax3.grid(True, alpha=0.3)

        # 4. いいね対象ツイートのエンゲージメント分布
        ax4 = fig.add_subplot(gs[1, 0])
        if liked_tweet_engagement:
            ax4.hist(
                liked_tweet_engagement,
                bins=30,
                alpha=0.7,
                color="#009688",
                edgecolor="black",
            )
            ax4.set_xlabel("いいね対象ツイートのエンゲージメント")
            ax4.set_ylabel("ツイート数")
            ax4.set_title(
                "いいね対象ツイートのエンゲージメント分布",
                fontsize=12,
                fontweight="bold",
            )
            ax4.set_xscale("log")
            ax4.grid(True, alpha=0.3)

        # 5. 最もいいねされている投稿者TOP10
        ax5 = fig.add_subplot(gs[1, 1])
        if liked_tweet_authors:
            author_counts = Counter(liked_tweet_authors).most_common(10)
            if author_counts:
                authors, counts = zip(*author_counts)
                y_pos = np.arange(len(authors))
                ax5.barh(y_pos, counts, color="#4CAF50")
                ax5.set_yticks(y_pos)
                ax5.set_yticklabels([f"@{author}" for author in authors])
                ax5.set_xlabel("いいね回数")
                ax5.set_title(
                    "最もいいねされている投稿者TOP10", fontsize=12, fontweight="bold"
                )
                ax5.grid(True, alpha=0.3)

        # 6. いいね活動レベル分析
        ax6 = fig.add_subplot(gs[1, 2])
        if user_like_counts:
            inactive_users = sum(1 for count in user_like_counts if count == 0)
            low_activity = sum(1 for count in user_like_counts if 0 < count <= 5)
            medium_activity = sum(1 for count in user_like_counts if 5 < count <= 15)
            high_activity = sum(1 for count in user_like_counts if count > 15)

            categories = [
                "非アクティブ",
                "低活動\n(1-5)",
                "中活動\n(6-15)",
                "高活動\n(16+)",
            ]
            counts = [inactive_users, low_activity, medium_activity, high_activity]
            colors = ["#BDC3C7", "#F39C12", "#E67E22", "#E74C3C"]

            ax6.pie(
                counts,
                labels=categories,
                colors=colors,
                autopct="%1.1f%%",
                startangle=90,
            )
            ax6.set_title("いいね活動レベル分布", fontsize=12, fontweight="bold")

        # 7. いいね対象コンテンツタイプ分析
        ax7 = fig.add_subplot(gs[2, 0])
        if liked_tweet_texts:
            reply_count = sum(1 for text in liked_tweet_texts if text.startswith("@"))
            rt_count = sum(1 for text in liked_tweet_texts if text.startswith("RT @"))
            original_count = len(liked_tweet_texts) - reply_count - rt_count

            ax7.pie(
                [original_count, reply_count, rt_count],
                labels=["オリジナル投稿", "リプライ", "リツイート"],
                colors=["#2196F3", "#FF9800", "#9C27B0"],
                autopct="%1.1f%%",
                startangle=90,
            )
            ax7.set_title("いいね対象コンテンツタイプ", fontsize=12, fontweight="bold")

        # 8. いいね数vs対象投稿人気度相関
        ax8 = fig.add_subplot(gs[2, 1])
        if user_like_counts and liked_tweet_engagement:
            user_avg_liked_engagement = {}
            for analysis in analyses:
                if analysis.liked_tweets:
                    avg_eng = np.mean(
                        [
                            t.retweet_count + t.favorite_count
                            for t in analysis.liked_tweets
                        ]
                    )
                    user_avg_liked_engagement[analysis.profile.username] = (
                        len(analysis.liked_tweets),
                        avg_eng,
                    )

            if user_avg_liked_engagement:
                like_counts_plot = [
                    data[0] for data in user_avg_liked_engagement.values()
                ]
                avg_liked_engagements = [
                    data[1] for data in user_avg_liked_engagement.values()
                ]

                ax8.scatter(
                    like_counts_plot,
                    avg_liked_engagements,
                    alpha=0.6,
                    color="#FF5722",
                    s=50,
                )
                ax8.set_xlabel("いいね数")
                ax8.set_ylabel("いいね対象の平均エンゲージメント")
                ax8.set_title(
                    "いいね数vs対象投稿人気度相関", fontsize=12, fontweight="bold"
                )
                ax8.grid(True, alpha=0.3)

        # 9. いいね収集統計
        ax9 = fig.add_subplot(gs[2, 2])
        total_users = len(analyses)
        total_likes = len(all_liked_tweets)
        avg_likes_per_user = total_likes / max(1, total_users)
        successful_collections = users_with_likes
        collection_rate = successful_collections / total_users * 100
        unique_authors = len(set(liked_tweet_authors)) if liked_tweet_authors else 0

        stats_text = f"""いいね収集統計:
・対象フォロワー数: {total_users:,}人
・総収集いいね数: {total_likes:,}件
・平均いいね数/人: {avg_likes_per_user:.1f}件
・収集成功率: {collection_rate:.1f}%
・ユニーク投稿者数: {unique_authors:,}人
・最大いいね数: {max(user_like_counts):,}件
・最小いいね数: {min(user_like_counts):,}件"""

        ax9.text(
            0.05,
            0.95,
            stats_text,
            transform=ax9.transAxes,
            fontsize=11,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.7),
        )
        ax9.set_xlim(0, 1)
        ax9.set_ylim(0, 1)
        ax9.axis("off")
        ax9.set_title("いいね収集統計サマリー", fontsize=12, fontweight="bold")

        plt.suptitle(
            "要件3: いいね履歴収集項目の詳細分析（各フォロワーがいいねしたポスト最大n件）",
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )
        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_geographic_insights(self, analyses: List[FollowerAnalysis]) -> str:
        """Create geographic analysis of followers."""
        locations = [a.profile.location for a in analyses if a.profile.location]

        if not locations:
            return self._create_no_data_chart("位置情報データがありません")

        # Process locations
        location_counts = Counter(locations).most_common(15)

        # Categorize by country/region
        japan_locations = [
            loc
            for loc in locations
            if any(
                jp in loc.lower()
                for jp in ["japan", "日本", "tokyo", "東京", "osaka", "大阪"]
            )
        ]
        us_locations = [
            loc
            for loc in locations
            if any(
                us in loc.lower()
                for us in ["usa", "us", "america", "california", "new york", "texas"]
            )
        ]
        other_locations = [
            loc
            for loc in locations
            if loc not in japan_locations and loc not in us_locations
        ]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Top locations
        if location_counts:
            locs, counts = zip(*location_counts)
            y_pos = np.arange(len(locs))
            bars = ax1.barh(
                y_pos, counts, color=plt.cm.Set3(np.linspace(0, 1, len(locs)))
            )
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(locs)
            ax1.set_xlabel("フォロワー数")
            ax1.set_title("上位15地域のフォロワー分布", fontsize=14, fontweight="bold")
            ax1.grid(True, alpha=0.3)

            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax1.text(
                    width + 0.1,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(width)}",
                    ha="left",
                    va="center",
                )

        # 2. Regional distribution
        region_counts = [
            ("日本", len(japan_locations)),
            ("アメリカ", len(us_locations)),
            ("その他", len(other_locations)),
        ]
        regions, counts = zip(*region_counts)

        ax2.pie(
            counts,
            labels=regions,
            colors=["#FF6B6B", "#4ECDC4", "#45B7D1"],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax2.set_title("地域別フォロワー分布", fontsize=14, fontweight="bold")

        # 3. Location specificity analysis
        location_lengths = [len(loc) for loc in locations]
        ax3.hist(
            location_lengths, bins=15, alpha=0.7, color="#96CEB4", edgecolor="black"
        )
        ax3.set_xlabel("位置情報の文字数")
        ax3.set_ylabel("ユーザー数")
        ax3.set_title("位置情報の詳細度分布", fontsize=14, fontweight="bold")
        ax3.grid(True, alpha=0.3)

        # 4. Location vs Activity correlation
        location_activity = {}
        for analysis in analyses:
            if analysis.profile.location:
                activity_score = len(analysis.recent_tweets or []) + len(
                    analysis.liked_tweets or []
                )
                location_activity[analysis.profile.location] = location_activity.get(
                    analysis.profile.location, []
                ) + [activity_score]

        if location_activity:
            avg_activity_by_location = {
                loc: np.mean(scores)
                for loc, scores in location_activity.items()
                if len(scores) >= 2
            }
            if avg_activity_by_location:
                sorted_locations = sorted(
                    avg_activity_by_location.items(), key=lambda x: x[1], reverse=True
                )[:10]
                locs, activities = zip(*sorted_locations)

                y_pos = np.arange(len(locs))
                ax4.barh(y_pos, activities, color="#FFEAA7")
                ax4.set_yticks(y_pos)
                ax4.set_yticklabels(locs)
                ax4.set_xlabel("平均アクティビティスコア")
                ax4.set_title(
                    "地域別アクティビティレベル", fontsize=14, fontweight="bold"
                )
                ax4.grid(True, alpha=0.3)

        plt.suptitle("フォロワー地理的分析", fontsize=16, fontweight="bold")
        plt.tight_layout()
        return self._save_plot_as_base64()

    def create_comprehensive_summary(
        self, analyses: List[FollowerAnalysis], target_username: str
    ) -> str:
        """Create comprehensive summary visualization."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Calculate key metrics
        total_followers = len(analyses)
        verified_count = sum(1 for a in analyses if a.profile.verified)
        active_posters = sum(1 for a in analyses if a.recent_tweets)
        active_likers = sum(1 for a in analyses if a.liked_tweets)

        avg_followers = np.mean([a.profile.followers_count for a in analyses])
        avg_following = np.mean([a.profile.following_count for a in analyses])

        total_posts_collected = sum(len(a.recent_tweets or []) for a in analyses)
        total_likes_collected = sum(len(a.liked_tweets or []) for a in analyses)

        # 1. Overview metrics
        metrics = ["総フォロワー", "認証済み", "アクティブ投稿", "アクティブいいね"]
        values = [total_followers, verified_count, active_posters, active_likers]
        colors = ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12"]

        bars = ax1.bar(metrics, values, color=colors, alpha=0.8, edgecolor="black")
        ax1.set_ylabel("ユーザー数")
        ax1.set_title(
            f"@{target_username} フォロワー分析サマリー", fontsize=14, fontweight="bold"
        )
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(values) * 0.01,
                f"{value:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 2. Data collection summary
        collection_metrics = ["投稿収集数", "いいね収集数"]
        collection_values = [total_posts_collected, total_likes_collected]

        ax2.bar(
            collection_metrics,
            collection_values,
            color=["#9B59B6", "#E91E63"],
            alpha=0.8,
            edgecolor="black",
        )
        ax2.set_ylabel("データ件数")
        ax2.set_title("収集データ統計", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3)

        for i, value in enumerate(collection_values):
            ax2.text(
                i,
                value + max(collection_values) * 0.01,
                f"{value:,}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # 3. Profile characteristics
        profile_stats = [
            f"平均フォロワー数: {avg_followers:,.0f}",
            f"平均フォロー数: {avg_following:,.0f}",
            f"認証率: {verified_count / total_followers * 100:.1f}%",
            f"投稿アクティブ率: {active_posters / total_followers * 100:.1f}%",
            f"いいねアクティブ率: {active_likers / total_followers * 100:.1f}%",
        ]

        ax3.text(
            0.05,
            0.95,
            "\n".join(profile_stats),
            transform=ax3.transAxes,
            fontsize=12,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
        )
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis("off")
        ax3.set_title("プロフィール特性統計", fontsize=14, fontweight="bold")

        # 4. Activity distribution
        activity_levels = []
        for analysis in analyses:
            posts = len(analysis.recent_tweets or [])
            likes = len(analysis.liked_tweets or [])
            total_activity = posts + likes

            if total_activity == 0:
                activity_levels.append("非アクティブ")
            elif total_activity <= 5:
                activity_levels.append("低活動")
            elif total_activity <= 15:
                activity_levels.append("中活動")
            else:
                activity_levels.append("高活動")

        activity_counts = Counter(activity_levels)
        labels = list(activity_counts.keys())
        sizes = list(activity_counts.values())
        colors = ["#BDC3C7", "#F39C12", "#E67E22", "#E74C3C"]

        ax4.pie(
            sizes,
            labels=labels,
            colors=colors[: len(labels)],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax4.set_title("アクティビティレベル分布", fontsize=14, fontweight="bold")

        plt.suptitle(
            f"@{target_username} フォロワー総合分析レポート",
            fontsize=16,
            fontweight="bold",
        )
        plt.tight_layout()
        return self._save_plot_as_base64()

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
