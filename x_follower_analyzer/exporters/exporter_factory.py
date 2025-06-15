"""Factory for creating appropriate exporters based on output format."""

from typing import Union

from ..models.config import OutputFormat
from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .dashboard_exporter import DashboardExporter


class ExporterFactory:
    """Factory class for creating exporters."""

    @staticmethod
    def create_exporter(
        output_format: OutputFormat, output_file: str
    ) -> Union[CSVExporter, JSONExporter, DashboardExporter]:
        """Create appropriate exporter based on output format.

        Args:
            output_format: OutputFormat enum value
            output_file: Path to output file

        Returns:
            Exporter instance

        Raises:
            ValueError: If output format is not supported
        """
        if output_format == OutputFormat.CSV:
            return CSVExporter(output_file)
        elif output_format == OutputFormat.JSON:
            return JSONExporter(output_file)
        elif output_format == OutputFormat.DASHBOARD:
            return DashboardExporter(output_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @staticmethod
    def create_dashboard_exporter(output_file: str) -> DashboardExporter:
        """Create dashboard exporter specifically.
        
        Args:
            output_file: Path to output HTML file
            
        Returns:
            DashboardExporter instance
        """
        return DashboardExporter(output_file)

    @staticmethod
    def get_supported_formats() -> list:
        """Get list of supported output formats.

        Returns:
            List of supported format strings
        """
        return [format.value for format in OutputFormat]
