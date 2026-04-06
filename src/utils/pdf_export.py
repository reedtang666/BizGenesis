"""PDF export functionality for business plans."""
import io
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger


# Try to import reportlab for PDF generation
# If not available, will use fallback text-based export
try:
    from reportlab.lib.pagesizes import A4, LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        PageBreak,
        Table,
        TableStyle,
        Image
    )
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("reportlab not installed, PDF export will use text fallback")


@dataclass
class PDFExportConfig:
    """Configuration for PDF export."""

    page_size: str = "A4"
    font_family: str = "Helvetica"
    font_size: int = 12
    title_font_size: int = 20
    heading_font_size: int = 16
    margin: float = 0.75  # inches
    title: Optional[str] = None
    include_watermark: bool = False
    watermark_text: str = "BizGenesis"
    author: str = "BizGenesis AI"
    subject: Optional[str] = None


class PDFExporter:
    """
    Exporter for generating PDF business plans.

    Supports:
    - Multiple page sizes (A4, Letter)
    - Custom styling and fonts
    - Watermarks
    - Section-based organization
    - Unicode content
    """

    SECTION_TITLES = {
        "industry": "创业领域",
        "market_analysis": "市场定位分析",
        "product_plan": "产品定义",
        "business_model": "商业模式",
        "finance_plan": "财务规划",
        "risk_analysis": "风险评估",
        "design_strategy": "品牌设计策略",
        "marketing_script": "流量营销脚本",
        "seo_strategy": "SEO策略",
    }

    def __init__(self, config: Optional[PDFExportConfig] = None):
        """
        Initialize PDF exporter.

        Args:
            config: PDF export configuration
        """
        self._config = config or PDFExportConfig()

    def export(self, context: Dict[str, Any]) -> bytes:
        """
        Export business plan context to PDF.

        Args:
            context: Business plan context dictionary

        Returns:
            PDF content as bytes
        """
        if HAS_REPORTLAB:
            return self._export_pdf(context)
        else:
            return self._export_text_fallback(context)

    def export_to_file(
        self,
        context: Dict[str, Any],
        filepath: Path | str
    ) -> Path:
        """
        Export business plan to PDF file.

        Args:
            context: Business plan context
            filepath: Output file path

        Returns:
            Path to created file
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        pdf_content = self.export(context)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(pdf_content)

        logger.info(f"Exported PDF to {filepath}")
        return filepath

    def _export_pdf(self, context: Dict[str, Any]) -> bytes:
        """Generate PDF using reportlab."""
        buffer = io.BytesIO()

        # Get page size
        if self._config.page_size == "Letter":
            page_size = LETTER
        else:
            page_size = A4

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=page_size,
            topMargin=self._config.margin * inch,
            bottomMargin=self._config.margin * inch,
            leftMargin=self._config.margin * inch,
            rightMargin=self._config.margin * inch
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Title
        if self._config.title:
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=self._config.title_font_size,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph(self._config.title, title_style))

        # Industry as main title
        industry = context.get("industry", "商业计划书")
        main_title = ParagraphStyle(
            "MainTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"🚀 {industry}", main_title))
        story.append(Spacer(1, 0.3 * inch))

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        story.append(Paragraph(f"生成时间: {timestamp}", styles["Normal"]))
        story.append(Spacer(1, 0.5 * inch))

        # Add sections
        for section_key, section_title in self.SECTION_TITLES.items():
            content = context.get(section_key)
            if content:
                # Section heading
                heading_style = ParagraphStyle(
                    "SectionHeading",
                    parent=styles["Heading2"],
                    fontSize=self._config.heading_font_size,
                    spaceBefore=20,
                    spaceAfter=10,
                    textColor=colors.HexColor("#2c3e50")
                )
                story.append(Paragraph(f"📋 {section_title}", heading_style))

                # Section content
                content_style = ParagraphStyle(
                    "SectionContent",
                    parent=styles["Normal"],
                    fontSize=self._config.font_size,
                    spaceAfter=10,
                    alignment=TA_LEFT
                )

                # Clean and wrap content
                clean_content = self._clean_content(str(content))
                story.append(Paragraph(clean_content, content_style))

        # Add watermark if enabled
        if self._config.include_watermark:
            watermark_style = ParagraphStyle(
                "Watermark",
                parent=styles["Normal"],
                fontSize=40,
                textColor=colors.HexColor("#e0e0e0"),
                alignment=TA_CENTER
            )
            story.append(PageBreak())
            story.append(Paragraph(self._config.watermark_text, watermark_style))

        # Build PDF
        doc.build(story)

        return buffer.getvalue()

    def _export_text_fallback(self, context: Dict[str, Any]) -> bytes:
        """Export as formatted text when reportlab is not available."""
        lines = []

        # Title
        industry = context.get("industry", "商业计划书")
        lines.append("=" * 60)
        lines.append(f"  🚀 {industry}")
        lines.append("=" * 60)

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines.append(f"生成时间: {timestamp}")
        lines.append("")

        # Sections
        for section_key, section_title in self.SECTION_TITLES.items():
            content = context.get(section_key)
            if content:
                lines.append("-" * 40)
                lines.append(f"📋 {section_title}")
                lines.append("-" * 40)
                lines.append(str(content))
                lines.append("")

        # Watermark
        if self._config.include_watermark:
            lines.append("")
            lines.append(f"  *** {self._config.watermark_text} ***")

        text_content = "\n".join(lines)
        return text_content.encode("utf-8")

    def _clean_content(self, content: str) -> str:
        """Clean content for PDF rendering."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove special characters that might cause issues
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        return content

    def _format_section(self, section_key: str, content: str) -> str:
        """Format a section for PDF."""
        title = self.SECTION_TITLES.get(section_key, section_key)
        return f"<b>{title}</b><br/><br/>{content}"

    def _generate_filename(self, industry: str) -> str:
        """Generate filename from industry name."""
        # Clean industry name
        safe_name = re.sub(r'[^\w\s-]', '', industry)
        safe_name = safe_name.strip().replace(' ', '_')[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"bizgenesis_{safe_name}_{timestamp}.pdf"

    def _add_watermark(self, content: str) -> str:
        """Add watermark to content."""
        if self._config.include_watermark:
            return f"{content}\n\n{self._config.watermark_text}"
        return content


# Singleton instance
_exporter: Optional[PDFExporter] = None


def get_pdf_exporter(config: Optional[PDFExportConfig] = None) -> PDFExporter:
    """Get singleton PDF exporter."""
    global _exporter
    if _exporter is None:
        _exporter = PDFExporter(config)
    return _exporter