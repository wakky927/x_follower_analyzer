"""Dashboard exporter for generating HTML visualization dashboards."""

from pathlib import Path
from typing import List
from ..models.user import FollowerAnalysis
from ..visualization.dashboard import DashboardGenerator


class DashboardExporter:
    """Export follower analysis data as interactive HTML dashboard."""

    def __init__(self, output_file: str):
        """Initialize dashboard exporter."""
        self.output_file = output_file
        self.dashboard_generator = DashboardGenerator()

    def export(
        self, analyses: List[FollowerAnalysis], target_username: str = "unknown"
    ) -> None:
        """Export analyses as HTML dashboard."""
        if not analyses:
            print("⚠️  No analysis data to export to dashboard")
            return

        try:
            # Ensure output directory exists
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate dashboard
            dashboard_path = self.dashboard_generator.generate_dashboard(
                analyses=analyses,
                target_username=target_username,
                output_path=str(output_path),
            )

            print(f"✅ Dashboard exported successfully to: {dashboard_path}")
            print(
                f"📊 Generated interactive dashboard with "
                f"{len(analyses)} follower profiles"
            )
            print(
                f"🌐 Open {dashboard_path} in your web browser to view the analysis"
            )

        except Exception as e:
            print(f"❌ Error exporting dashboard: {e}")
            raise
