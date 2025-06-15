"""HTML dashboard generator for follower analysis visualization."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

from ..models.user import FollowerAnalysis
from .charts import ChartGenerator


class DashboardGenerator:
    """Generate interactive HTML dashboard for follower analysis."""

    def __init__(self):
        """Initialize dashboard generator."""
        self.chart_generator = ChartGenerator()

    def generate_dashboard(
        self, analyses: List[FollowerAnalysis], target_username: str, output_path: str
    ) -> str:
        """Generate complete HTML dashboard with all visualizations."""

        # Generate static charts
        follower_dist_chart = self.chart_generator.create_follower_distribution_chart(
            analyses
        )
        verification_chart = self.chart_generator.create_verification_pie_chart(
            analyses
        )
        location_chart = self.chart_generator.create_location_analysis_chart(analyses)
        engagement_chart = self.chart_generator.create_engagement_analysis_chart(
            analyses
        )
        hashtag_cloud = self.chart_generator.create_hashtag_wordcloud(analyses)
        activity_timeline = self.chart_generator.create_activity_timeline_chart(
            analyses
        )

        # Generate interactive charts
        interactive_charts = self._create_interactive_charts(analyses)

        # Generate summary statistics
        stats = self._generate_summary_stats(analyses)

        # Create HTML content
        html_content = self._generate_html_template(
            target_username=target_username,
            stats=stats,
            follower_dist_chart=follower_dist_chart,
            verification_chart=verification_chart,
            location_chart=location_chart,
            engagement_chart=engagement_chart,
            hashtag_cloud=hashtag_cloud,
            activity_timeline=activity_timeline,
            interactive_charts=interactive_charts,
        )

        # Save dashboard
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def _create_interactive_charts(self, analyses: List[FollowerAnalysis]) -> str:
        """Create interactive Plotly charts."""
        follower_data = self.chart_generator.create_interactive_dashboard_data(analyses)

        # Create subplot figure
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Follower vs Following Relationship",
                "Engagement Scatter Plot",
                "Location Distribution",
                "Activity Distribution",
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "histogram"}],
            ],
        )

        # Follower vs Following scatter plot
        fig.add_trace(
            go.Scatter(
                x=[d["followers_count"] for d in follower_data],
                y=[d["following_count"] for d in follower_data],
                mode="markers",
                marker=dict(
                    color=[d["avg_likes"] for d in follower_data],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Avg Likes"),
                    size=8,
                ),
                text=[
                    f"@{d['username']}<br>Followers: {d['followers_count']}<br>Following: {d['following_count']}"
                    for d in follower_data
                ],
                hovertemplate="%{text}<extra></extra>",
                name="Users",
            ),
            row=1,
            col=1,
        )

        # Engagement scatter plot
        fig.add_trace(
            go.Scatter(
                x=[d["avg_retweets"] for d in follower_data],
                y=[d["avg_likes"] for d in follower_data],
                mode="markers",
                marker=dict(
                    color=[d["followers_count"] for d in follower_data],
                    colorscale="Plasma",
                    showscale=True,
                    colorbar=dict(title="Followers"),
                    size=10,
                ),
                text=[
                    f"@{d['username']}<br>Avg RT: {d['avg_retweets']:.1f}<br>Avg Likes: {d['avg_likes']:.1f}"
                    for d in follower_data
                ],
                hovertemplate="%{text}<extra></extra>",
                name="Engagement",
            ),
            row=1,
            col=2,
        )

        # Location bar chart
        location_counts = {}
        for d in follower_data:
            loc = d["location"]
            location_counts[loc] = location_counts.get(loc, 0) + 1

        top_locations = sorted(
            location_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        fig.add_trace(
            go.Bar(
                x=[count for _, count in top_locations],
                y=[loc for loc, _ in top_locations],
                orientation="h",
                marker_color="lightblue",
                name="Locations",
            ),
            row=2,
            col=1,
        )

        # Activity histogram
        fig.add_trace(
            go.Histogram(
                x=[d["recent_tweets_count"] for d in follower_data],
                nbinsx=20,
                marker_color="coral",
                name="Tweet Activity",
            ),
            row=2,
            col=2,
        )

        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Interactive Follower Analysis Dashboard",
            title_x=0.5,
        )

        # Update axes labels
        fig.update_xaxes(title_text="Followers", row=1, col=1)
        fig.update_yaxes(title_text="Following", row=1, col=1)
        fig.update_xaxes(title_text="Avg Retweets", row=1, col=2)
        fig.update_yaxes(title_text="Avg Likes", row=1, col=2)
        fig.update_xaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="Location", row=2, col=1)
        fig.update_xaxes(title_text="Recent Tweets Count", row=2, col=2)
        fig.update_yaxes(title_text="Number of Users", row=2, col=2)

        return pyo.plot(fig, output_type="div", include_plotlyjs=True)

    def _generate_summary_stats(
        self, analyses: List[FollowerAnalysis]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the dashboard."""
        total_followers = len(analyses)
        verified_count = sum(1 for a in analyses if a.profile.verified)

        follower_counts = [a.profile.followers_count for a in analyses]
        avg_followers = (
            sum(follower_counts) / len(follower_counts) if follower_counts else 0
        )

        locations = [a.profile.location for a in analyses if a.profile.location]
        unique_locations = len(set(locations))

        total_tweets = sum(len(a.recent_tweets) for a in analyses if a.recent_tweets)

        hashtags = []
        for a in analyses:
            if a.recent_tweets:
                for tweet in a.recent_tweets:
                    if tweet.hashtags:
                        hashtags.extend(tweet.hashtags)

        unique_hashtags = len(set(hashtags))

        return {
            "total_followers": total_followers,
            "verified_count": verified_count,
            "verification_rate": (
                (verified_count / total_followers * 100) if total_followers > 0 else 0
            ),
            "avg_followers": int(avg_followers),
            "unique_locations": unique_locations,
            "total_tweets_analyzed": total_tweets,
            "unique_hashtags": unique_hashtags,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _generate_html_template(self, **kwargs) -> str:
        """Generate HTML template with all charts and data."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X Follower Analysis Dashboard - @{kwargs['target_username']}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #1DA1F2, #14171A);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #1DA1F2;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #1DA1F2;
        }}
        
        .stat-label {{
            color: #657786;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .chart-section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .chart-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #e1e8ed;
        }}
        
        .chart-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin: 0;
        }}
        
        .chart-content {{
            padding: 20px;
            text-align: center;
        }}
        
        .chart-image {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }}
        
        .footer {{
            text-align: center;
            color: #657786;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #e1e8ed;
        }}
        
        @media (max-width: 768px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 X Follower Analysis Dashboard</h1>
        <h2>@{kwargs['target_username']}</h2>
        <p>Generated on {kwargs['stats']['analysis_date']}</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['total_followers']:,}</div>
            <div class="stat-label">Total Followers Analyzed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['verification_rate']:.1f}%</div>
            <div class="stat-label">Verification Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['avg_followers']:,}</div>
            <div class="stat-label">Average Followers</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['unique_locations']}</div>
            <div class="stat-label">Unique Locations</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['total_tweets_analyzed']:,}</div>
            <div class="stat-label">Tweets Analyzed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{kwargs['stats']['unique_hashtags']}</div>
            <div class="stat-label">Unique Hashtags</div>
        </div>
    </div>

    <div class="chart-section">
        <div class="chart-header">
            <h3 class="chart-title">📈 Interactive Analysis Dashboard</h3>
        </div>
        <div class="chart-content">
            {kwargs['interactive_charts']}
        </div>
    </div>

    <div class="grid-2">
        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">👥 Follower Distribution</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['follower_dist_chart']}" alt="Follower Distribution" class="chart-image">
            </div>
        </div>

        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">✅ Verification Status</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['verification_chart']}" alt="Verification Status" class="chart-image">
            </div>
        </div>
    </div>

    <div class="grid-2">
        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">🌍 Geographic Distribution</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['location_chart']}" alt="Location Analysis" class="chart-image">
            </div>
        </div>

        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">💬 Engagement Analysis</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['engagement_chart']}" alt="Engagement Analysis" class="chart-image">
            </div>
        </div>
    </div>

    <div class="grid-2">
        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">#️⃣ Popular Hashtags</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['hashtag_cloud']}" alt="Hashtag Word Cloud" class="chart-image">
            </div>
        </div>

        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">⏰ Activity Timeline</h3>
            </div>
            <div class="chart-content">
                <img src="data:image/png;base64,{kwargs['activity_timeline']}" alt="Activity Timeline" class="chart-image">
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Generated by X Follower Analyzer | Analysis Date: {kwargs['stats']['analysis_date']}</p>
        <p>This dashboard provides insights into follower demographics, engagement patterns, and content preferences.</p>
    </div>
</body>
</html>
        """
