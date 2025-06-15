"""Command line interface for X Follower Analyzer."""

import sys

import click

from .utils.config import (
    create_analysis_config,
    get_api_credentials,
    load_environment_config,
    validate_output_directory,
)


@click.command()
@click.argument("username", type=str)
@click.option(
    "--max-followers",
    default=1000,
    type=int,
    help="Maximum number of followers to analyze (default: 1000)",
)
@click.option(
    "--max-tweets",
    default=10,
    type=int,
    help="Maximum number of recent tweets per user (default: 10)",
)
@click.option(
    "--max-likes",
    default=20,
    type=int,
    help="Maximum number of liked tweets per user (default: 20)",
)
@click.option(
    "--output-format",
    type=click.Choice(["csv", "json", "html"], case_sensitive=False),
    default="csv",
    help="Output format: csv, json, or html (interactive dashboard)",
)
@click.option(
    "--output-file",
    type=str,
    help="Output file path (default: auto-generated)",
)
@click.option(
    "--no-retweets",
    is_flag=True,
    help="Exclude retweets from analysis",
)
@click.option(
    "--rate-limit-delay",
    default=1.0,
    type=float,
    help="Delay between API calls in seconds (default: 1.0)",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to configuration file (default: config/.env)",
)
@click.option(
    "--generate-dashboard",
    is_flag=True,
    help="Generate additional HTML dashboard alongside primary output",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show configuration and exit without running analysis",
)
def main(
    username: str,
    max_followers: int,
    max_tweets: int,
    max_likes: int,
    output_format: str,
    output_file: str,
    no_retweets: bool,
    rate_limit_delay: float,
    config_file: str,
    generate_dashboard: bool,
    dry_run: bool,
) -> None:
    """Analyze X (Twitter) followers' profiles, posts, and likes.

    USERNAME: Target X username (without @)
    """

    try:
        # Load environment configuration
        load_environment_config(config_file)

        # Validate API credentials
        try:
            credentials = get_api_credentials()
            click.echo("✓ API credentials loaded successfully")
        except ValueError as e:
            click.echo(f"❌ Error loading API credentials: {e}", err=True)
            click.echo(
                "Please check your config/.env file and ensure X_BEARER_TOKEN is set."
            )
            sys.exit(1)

        # Create analysis configuration
        try:
            config = create_analysis_config(
                target_username=username,
                max_followers=max_followers,
                max_tweets_per_user=max_tweets,
                max_liked_tweets_per_user=max_likes,
                output_format=output_format,
                output_file=output_file,
                include_retweets=not no_retweets,
                rate_limit_delay=rate_limit_delay,
            )
        except ValueError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            sys.exit(1)

        # Validate output directory
        try:
            output_path = validate_output_directory(config.output_file)
            click.echo(f"✓ Output will be saved to: {output_path}")
        except (PermissionError, OSError) as e:
            click.echo(f"❌ Output directory error: {e}", err=True)
            sys.exit(1)

        # Display configuration
        click.echo("\\n🎯 Analysis Configuration:")
        click.echo(f"  Target username: @{config.target_username}")
        click.echo(f"  Max followers: {config.max_followers:,}")
        click.echo(f"  Max tweets per user: {config.max_tweets_per_user}")
        click.echo(f"  Max likes per user: {config.max_liked_tweets_per_user}")
        click.echo(f"  Output format: {config.output_format.value.upper()}")
        click.echo(f"  Include retweets: {config.include_retweets}")
        click.echo(f"  Rate limit delay: {config.rate_limit_delay}s")

        if dry_run:
            click.echo("\\n🏃 Dry run mode - exiting without analysis")
            return

        # Run the analysis
        try:
            from .api.analyzer import FollowerAnalyzer
            from .exporters.exporter_factory import ExporterFactory

            analyzer = FollowerAnalyzer(credentials, config)
            analyses = analyzer.analyze_followers()

            if analyses:
                click.echo(
                    f"\\n✅ Analysis completed! Found {len(analyses)} follower profiles."
                )

                # Export data
                click.echo(
                    f"📤 Exporting data to "
                    f"{config.output_format.value.upper()} format..."
                )
                exporter = ExporterFactory.create_exporter(
                    config.output_format, config.output_file
                )
                
                # Export with target username for dashboard
                if hasattr(exporter, 'export') and hasattr(exporter.export, '__code__') and 'target_username' in exporter.export.__code__.co_varnames:
                    exporter.export(analyses, target_username=config.target_username)
                else:
                    exporter.export(analyses)

                click.echo("\\n🎉 Analysis and export completed successfully!")
                click.echo(f"📁 Output file: {config.output_file}")
                
                # Generate additional dashboard if requested
                if generate_dashboard and config.output_format.value != "html":
                    click.echo("\\n📊 Generating additional HTML dashboard...")
                    dashboard_file = f"{config.target_username}_dashboard.html"
                    dashboard_exporter = ExporterFactory.create_dashboard_exporter(dashboard_file)
                    dashboard_exporter.export(analyses, target_username=config.target_username)
                    click.echo(f"📁 Dashboard file: {dashboard_file}")
                
                if config.output_format.value == "html":
                    click.echo("\\n🌐 Open the HTML file in your web browser to view the interactive dashboard!")
            else:
                click.echo("\\n❌ No follower data collected.")

        except Exception as e:
            click.echo(f"\\n❌ Analysis failed: {e}", err=True)
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\\n❌ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
