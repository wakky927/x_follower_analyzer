"""Generate demo images based on initial requirements."""

import base64
from pathlib import Path

from demo_data_generator import generate_demo_data
from x_follower_analyzer.visualization.follower_charts import FollowerAnalysisCharts


def save_base64_image(base64_data: str, filename: str) -> None:
    """Save base64 image data to file."""
    image_data = base64.b64decode(base64_data)
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"✅ Saved: {filename}")


def main():
    """Generate requirement-based demo images for README."""
    print("🎯 Generating demo data based on initial requirements...")
    demo_analyses = generate_demo_data(100)

    print("📊 Creating follower analysis chart generator...")
    chart_generator = FollowerAnalysisCharts()

    # Create data directory
    data_dir = Path("data/demo_images")
    data_dir.mkdir(parents=True, exist_ok=True)

    print("📈 Generating requirement-based charts...")

    # Generate all chart types based on requirements
    charts = {
        "01_follower_profile_overview": (
            chart_generator.create_follower_profile_overview(demo_analyses)
        ),
        "02_bio_analysis": chart_generator.create_bio_analysis_chart(demo_analyses),
        "03_posting_behavior": chart_generator.create_posting_behavior_analysis(
            demo_analyses
        ),
        "04_likes_behavior": chart_generator.create_likes_behavior_analysis(
            demo_analyses
        ),
        "05_geographic_insights": chart_generator.create_geographic_insights(
            demo_analyses
        ),
        "06_comprehensive_summary": chart_generator.create_comprehensive_summary(
            demo_analyses, "elonmusk"
        ),
    }

    # Save all charts
    for chart_name, base64_data in charts.items():
        filename = data_dir / f"{chart_name}.png"
        save_base64_image(base64_data, str(filename))

    print(f"\n🎉 Generated {len(charts)} requirement-based demo images in {data_dir}/")
    print("📁 Files created:")
    for filename in sorted(data_dir.glob("0*.png")):
        print(f"   - {filename.name}")

    print("\n💡 These images showcase analysis based on initial requirements:")
    print("   1. フォロワー情報取得（プロフィール詳細）")
    print("   2. 自己紹介文分析")
    print("   3. 投稿行動分析（各フォロワーのポスト）")
    print("   4. いいね行動分析（いいね履歴）")
    print("   5. 地理的インサイト（位置情報）")
    print("   6. 総合分析レポート")


if __name__ == "__main__":
    main()
