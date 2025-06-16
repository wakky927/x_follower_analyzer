"""Generate demo images for README documentation."""

import base64
from pathlib import Path

from demo_data_generator import generate_demo_data
from x_follower_analyzer.visualization.charts import ChartGenerator


def save_base64_image(base64_data: str, filename: str) -> None:
    """Save base64 image data to file."""
    image_data = base64.b64decode(base64_data)
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"✅ Saved: {filename}")


def main():
    """Generate and save demo images for README."""
    print("🎯 Generating demo data...")
    demo_analyses = generate_demo_data(100)

    print("📊 Creating chart generator...")
    chart_generator = ChartGenerator()

    # Create data directory
    data_dir = Path("data/demo_images")
    data_dir.mkdir(parents=True, exist_ok=True)

    print("📈 Generating demo charts...")

    # Generate all chart types
    charts = {
        "follower_distribution": chart_generator.create_follower_distribution_chart(
            demo_analyses
        ),
        "verification_status": chart_generator.create_verification_pie_chart(
            demo_analyses
        ),
        "location_analysis": chart_generator.create_location_analysis_chart(
            demo_analyses
        ),
        "engagement_analysis": chart_generator.create_engagement_analysis_chart(
            demo_analyses
        ),
        "hashtag_wordcloud": chart_generator.create_hashtag_wordcloud(demo_analyses),
        "activity_timeline": chart_generator.create_activity_timeline_chart(
            demo_analyses
        ),
    }

    # Save all charts
    for chart_name, base64_data in charts.items():
        filename = data_dir / f"{chart_name}.png"
        save_base64_image(base64_data, str(filename))

    print(f"\n🎉 Generated {len(charts)} demo images in {data_dir}/")
    print("📁 Files created:")
    for filename in data_dir.glob("*.png"):
        print(f"   - {filename.name}")

    print("\n💡 These images can now be referenced in README.md")


if __name__ == "__main__":
    main()
