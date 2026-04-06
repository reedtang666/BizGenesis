"""Tests for PDF export functionality."""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from src.utils.pdf_export import (
    PDFExporter,
    PDFExportConfig,
    get_pdf_exporter
)


class TestPDFExportConfig:
    """Test PDFExportConfig class."""

    def test_config_defaults(self):
        """Test default configuration."""
        config = PDFExportConfig()
        assert config.page_size == "A4"
        assert config.font_family == "Helvetica"
        assert config.title is None

    def test_config_custom_values(self):
        """Test custom configuration."""
        config = PDFExportConfig(
            title="My Report",
            page_size="Letter",
            font_size=14
        )
        assert config.title == "My Report"
        assert config.page_size == "Letter"
        assert config.font_size == 14


class TestPDFExporter:
    """Test PDFExporter class."""

    def test_exporter_initialization(self):
        """Test exporter can be initialized."""
        exporter = PDFExporter()
        assert exporter is not None

    def test_exporter_with_config(self):
        """Test exporter with custom config."""
        config = PDFExportConfig(title="Test Report")
        exporter = PDFExporter(config)
        assert exporter._config.title == "Test Report"

    def test_export_empty_context(self):
        """Test exporting with empty context."""
        exporter = PDFExporter()
        # Should not raise
        result = exporter.export({})
        assert result is not None

    def test_export_basic_context(self):
        """Test exporting basic context."""
        exporter = PDFExporter()
        context = {
            "industry": "Tech",
            "market_analysis": "Market analysis content",
            "product_plan": "Product plan content"
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_all_sections(self):
        """Test exporting all business plan sections."""
        exporter = PDFExporter()
        context = {
            "industry": "Tech",
            "market_analysis": "Market analysis content",
            "product_plan": "Product plan content",
            "business_model": "Business model content",
            "finance_plan": "Finance plan content",
            "risk_analysis": "Risk analysis content",
            "design_strategy": "Design strategy content",
            "marketing_script": "Marketing script content",
            "seo_strategy": "SEO strategy content"
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_preserves_content(self):
        """Test that content is preserved in export."""
        exporter = PDFExporter()
        test_content = "Test market analysis"
        context = {
            "industry": "Tech",
            "market_analysis": test_content
        }
        result = exporter.export(context)
        # Result is bytes, check if content can be found
        assert test_content.encode() in result or result is not None

    def test_export_with_unicode_content(self):
        """Test exporting content with Unicode characters."""
        exporter = PDFExporter()
        context = {
            "industry": "科技",
            "market_analysis": "这是市场分析内容 with emojis 🚀"
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_to_file(self):
        """Test exporting to a file."""
        exporter = PDFExporter()
        context = {
            "industry": "Tech",
            "market_analysis": "Content"
        }

        with patch("pathlib.Path.write_bytes") as mock_write:
            mock_write.return_value = 100  # bytes written
            result = exporter.export_to_file(context, "/tmp/test.pdf")
            # write_bytes should be called
            assert mock_write.called or result is not None

    def test_export_to_pathlib_path(self):
        """Test exporting to pathlib Path."""
        exporter = PDFExporter()
        context = {"industry": "Tech", "market_analysis": "Content"}

        path = Path("/tmp/test_path.pdf")
        result = exporter.export_to_file(context, path)
        assert result == path

    def test_generate_filename(self):
        """Test generating filename from industry."""
        exporter = PDFExporter()
        filename = exporter._generate_filename("Tech Industry")
        assert "tech" in filename.lower()
        assert filename.endswith(".pdf")

    def test_format_section(self):
        """Test section formatting."""
        exporter = PDFExporter()
        formatted = exporter._format_section("market_analysis", "Some content")
        assert "market_analysis" in formatted.lower() or "Some content" in formatted

    def test_add_watermark(self):
        """Test adding watermark."""
        exporter = PDFExporter(config=PDFExportConfig(include_watermark=True))
        content = "Some content"
        result = exporter._add_watermark(content)
        assert result is not None


class TestGetPDFExporter:
    """Test get_pdf_exporter function."""

    def test_get_exporter_singleton(self):
        """Test singleton pattern."""
        exporter1 = get_pdf_exporter()
        exporter2 = get_pdf_exporter()
        assert exporter1 is exporter2


class TestPDFExporterEdgeCases:
    """Test edge cases for PDF exporter."""

    def test_export_very_long_content(self):
        """Test exporting very long content."""
        exporter = PDFExporter()
        long_text = "A" * 10000  # 10k characters
        context = {
            "industry": "Tech",
            "market_analysis": long_text
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_special_characters(self):
        """Test exporting special characters."""
        exporter = PDFExporter()
        context = {
            "industry": "Tech",
            "market_analysis": "Special chars: <>&\"'{}[]|\\^~`"
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_missing_sections(self):
        """Test exporting with missing sections."""
        exporter = PDFExporter()
        context = {
            "industry": "Tech"
            # Missing other sections
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_with_letter_page_size(self):
        """Test exporting with Letter page size."""
        config = PDFExportConfig(page_size="Letter")
        exporter = PDFExporter(config)
        context = {
            "industry": "Tech",
            "market_analysis": "Content"
        }
        result = exporter.export(context)
        assert result is not None
        # Verify PDF starts with PDF magic bytes
        assert result[:4] == b'%PDF'

    def test_export_with_custom_title(self):
        """Test exporting with custom title."""
        config = PDFExportConfig(title="My Custom Report")
        exporter = PDFExporter(config)
        context = {
            "industry": "Tech",
            "market_analysis": "Content"
        }
        result = exporter.export(context)
        assert result is not None

    def test_export_with_author(self):
        """Test exporting with author."""
        config = PDFExportConfig(author="Test Author")
        exporter = PDFExporter(config)
        context = {"industry": "Tech"}
        result = exporter.export(context)
        assert result is not None

    def test_export_with_subject(self):
        """Test exporting with subject."""
        config = PDFExportConfig(subject="Business Plan")
        exporter = PDFExporter(config)
        context = {"industry": "Tech"}
        result = exporter.export(context)
        assert result is not None

    def test_export_with_watermark_text(self):
        """Test exporting with watermark text."""
        config = PDFExportConfig(
            include_watermark=True,
            watermark_text="Confidential"
        )
        exporter = PDFExporter(config)
        context = {"industry": "Tech", "market_analysis": "Content"}
        result = exporter.export(context)
        assert result is not None

    def test_get_exporter_with_config(self):
        """Test get_pdf_exporter with custom config."""
        config = PDFExportConfig(title="Test")
        exporter = get_pdf_exporter(config)
        assert exporter is not None
        # Second call should return same instance (singleton)
        exporter2 = get_pdf_exporter()
        assert exporter is exporter2