"""PDF export functionality for business plans."""
import io
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger

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
    )
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("reportlab not installed, PDF export will use text fallback")


@dataclass
class PDFExportConfig:
    page_size: str = "A4"
    font_size: int = 12
    title_font_size: int = 20
    heading_font_size: int = 16
    margin: float = 0.75
    title: Optional[str] = None
    include_watermark: bool = False
    watermark_text: str = "BizGenesis"
    author: str = "BizGenesis AI"
    subject: Optional[str] = None


class PDFExporter:
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
        self._config = config or PDFExportConfig()

    def export(self, context: Dict[str, Any]) -> bytes:
        if HAS_REPORTLAB:
            return self._export_pdf(context)
        else:
            return self._export_text_fallback(context)

    def export_to_file(self, context: Dict[str, Any], filepath: Path | str) -> Path:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        pdf_content = self.export(context)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(pdf_content)
        logger.info(f"Exported PDF to {filepath}")
        return filepath

    def _export_pdf(self, context: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        page_size = LETTER if self._config.page_size == "Letter" else A4
        doc = SimpleDocTemplate(
            buffer, pagesize=page_size,
            topMargin=self._config.margin * inch,
            bottomMargin=self._config.margin * inch,
            leftMargin=self._config.margin * inch,
            rightMargin=self._config.margin * inch,
        )
        story = []
        styles = getSampleStyleSheet()

        if self._config.title:
            title_style = ParagraphStyle("CustomTitle", parent=styles["Normal"], fontName='STSong-Light', fontSize=self._config.title_font_size, spaceAfter=30, alignment=TA_CENTER)
            story.append(Paragraph(self._config.title, title_style))

        industry = context.get("industry", "商业计划书")
        main_title = ParagraphStyle("MainTitle", parent=styles["Normal"], fontName='STSong-Light', fontSize=24, spaceAfter=20, alignment=TA_CENTER)
        story.append(Paragraph(f"🚀 {industry}", main_title))
        story.append(Spacer(1, 0.3 * inch))

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        ts_style = ParagraphStyle("TS", parent=styles["Normal"], fontName='STSong-Light', fontSize=10, textColor=colors.grey)
        story.append(Paragraph(f"生成时间: {timestamp}", ts_style))
        story.append(Spacer(1, 0.5 * inch))

        for section_key, section_title in self.SECTION_TITLES.items():
            content = context.get(section_key)
            if content:
                heading_style = ParagraphStyle("SectionHeading", parent=styles["Normal"], fontName='STSong-Light', fontSize=self._config.heading_font_size, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor("#2c3e50"))
                story.append(Paragraph(f"📋 {section_title}", heading_style))

                content_style = ParagraphStyle("SectionContent", parent=styles["Normal"], fontName='STSong-Light', fontSize=self._config.font_size, spaceAfter=10, alignment=TA_LEFT, leading=self._config.font_size * 1.8)
                clean_content = self._clean_content(str(content))
                story.append(Paragraph(clean_content, content_style))
                story.append(Spacer(1, 0.2 * inch))

        if self._config.include_watermark:
            watermark_style = ParagraphStyle("Watermark", parent=styles["Normal"], fontName='STSong-Light', fontSize=40, textColor=colors.HexColor("#e0e0e0"), alignment=TA_CENTER)
            story.append(PageBreak())
            story.append(Paragraph(self._config.watermark_text, watermark_style))

        doc.build(story)
        return buffer.getvalue()

    def _export_text_fallback(self, context: Dict[str, Any]) -> bytes:
        lines = []
        industry = context.get("industry", "商业计划书")
        lines.append("=" * 60)
        lines.append(f"  🚀 {industry}")
        lines.append("=" * 60)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        for section_key, section_title in self.SECTION_TITLES.items():
            content = context.get(section_key)
            if content:
                lines.append("-" * 40)
                lines.append(f"📋 {section_title}")
                lines.append("-" * 40)
                lines.append(str(content))
                lines.append("")
        if self._config.include_watermark:
            lines.append(f"  *** {self._config.watermark_text} ***")
        return "\n".join(lines).encode("utf-8")

    def _clean_content(self, content: str) -> str:
        content = re.sub(r'\s+', ' ', content)
        content = content.replace('&', '&amp;')
        content = content.replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        return content


_exporter: Optional[PDFExporter] = None

def get_pdf_exporter(config: Optional[PDFExportConfig] = None) -> PDFExporter:
    global _exporter
    if _exporter is None:
        _exporter = PDFExporter(config)
    return _exporter
