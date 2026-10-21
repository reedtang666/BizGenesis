"""
Streamlit Web UI for BizGenesis.
Run: streamlit run src/ui/app.py
"""
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from src.agents.market import MarketResearcher
from src.agents.product import ProductManager
from src.agents.marketing import ContentStrategist
from src.agents.seo import SEOExpert
from src.agents.designer import ChiefDesigner
from src.agents.business import BusinessModeler
from src.agents.finance import FinancePlanner
from src.agents.risk import RiskAnalyst
from src.config import Config
from src.utils.agent_parallel import get_parallel_executor
from src.utils.token_monitor import get_token_monitor
from src.utils.pdf_export import PDFExportConfig, get_pdf_exporter

CUSTOM_CSS = """
<style>
    /* === 1. Sci-Fi Cyber-Grid & Deep Space Commercial Background === */
    .stApp {
        background-color: #060913;
        background-image:
            radial-gradient(at 20% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
            radial-gradient(at 80% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            linear-gradient(rgba(56, 189, 248, 0.028) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 189, 248, 0.028) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    }
    .block-container {
        max-width: 1160px !important;
        padding-top: 1.8rem !important;
        padding-bottom: 4rem !important;
    }

    /* === 2. Sidebar Executive Telemetry Style === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080d1a 0%, #060913 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.16);
    }
    span[data-baseweb="tag"] {
        background: rgba(56, 189, 248, 0.15) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 6px !important;
        color: #e0f2fe !important;
    }
    span[data-baseweb="tag"] span {
        color: #e0f2fe !important;
    }

    /* === 3. Top Executive HUD Telemetry Bar === */
    .hud-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 1.5rem;
        padding: 10px 16px;
        background: rgba(11, 18, 34, 0.78);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        backdrop-filter: blur(12px);
    }
    .hud-item {
        display: flex;
        align-items: center;
        gap: 10px;
        border-right: 1px solid rgba(148, 163, 184, 0.12);
        padding-right: 10px;
    }
    .hud-item:last-child {
        border-right: none;
    }
    .hud-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00f5d4;
        box-shadow: 0 0 10px #00f5d4;
        flex-shrink: 0;
    }
    .hud-label {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.7rem;
        color: #64748b;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin: 0;
    }
    .hud-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.82rem;
        font-weight: 600;
        color: #e2e8f0;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* === 4. Hero Header === */
    .hero-wrap {
        text-align: center;
        padding: 0.6rem 0 1.5rem 0;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 4px 14px;
        border-radius: 999px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.35);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.12);
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 0.45rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #bae6fd 45%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 0.98rem;
        letter-spacing: 0.02em;
        margin: 0 auto;
    }

    /* === 5. Command Console Card (Bordered Container) === */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.82) 0%, rgba(9, 14, 26, 0.9) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.24) !important;
        border-radius: 14px !important;
        box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.6), inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
        padding: 1.25rem !important;
    }

    /* === 6. Inputs & Buttons (Strict Single-Line Uniform Height) === */
    .stTextInput div[data-baseweb="input"] {
        background: rgba(6, 10, 20, 0.9) !important;
        border: 1px solid rgba(56, 189, 248, 0.32) !important;
        border-radius: 10px !important;
        height: 46px !important;
        min-height: 46px !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease;
    }
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.25) !important;
    }
    .stTextInput div[data-baseweb="base-input"] {
        background: transparent !important;
        border: none !important;
        height: 100% !important;
    }
    .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        color: #f8fafc !important;
        height: 100% !important;
        padding: 0 1rem !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 55%, #7c3aed 100%) !important;
        border: 1px solid rgba(125, 211, 252, 0.4) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        border-radius: 10px !important;
        height: 46px !important;
        white-space: nowrap !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.28);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 28px rgba(56, 189, 248, 0.5);
        transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #cbd5e1 !important;
        border-radius: 8px !important;
        height: 38px !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.1) !important;
    }

    /* === 7. Section Title Bar === */
    .sec-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 1.6rem 0 0.9rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(56, 189, 248, 0.16);
    }
    .sec-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: 0.02em;
        margin: 0;
    }
    .sec-tag {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.72rem;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 2px 8px;
        border-radius: 4px;
    }

    /* === 8. Native CSS Grids (100% Equal Height & Strict Alignment) === */
    .bento-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        align-items: stretch;
    }
    @media (max-width: 900px) {
        .bento-grid-4, .hud-bar {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    /* Core Capability Card */
    .cyber-card {
        position: relative;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.78) 0%, rgba(10, 15, 29, 0.88) 100%);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-top: 2px solid rgba(56, 189, 248, 0.55);
        border-radius: 12px;
        padding: 1.2rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 165px;
        box-sizing: border-box;
        transition: all 0.22s ease;
    }
    .cyber-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 8px 24px -6px rgba(56, 189, 248, 0.22);
        transform: translateY(-2px);
    }
    .cyber-card-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.65rem;
    }
    .cyber-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .cyber-code {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 0.06em;
    }
    .cyber-title {
        color: #f8fafc;
        font-size: 0.96rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
    }
    .cyber-desc {
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.5;
        margin: 0;
    }

    /* 8-Agent Matrix Card & Live Status Animations */
    @keyframes pulseRunning {
        0% { box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.45), inset 0 0 12px rgba(56, 189, 248, 0.18); }
        50% { box-shadow: 0 0 18px 2px rgba(0, 245, 212, 0.3), inset 0 0 20px rgba(56, 189, 248, 0.28); }
        100% { box-shadow: 0 0 0 0 rgba(0, 245, 212, 0.45), inset 0 0 12px rgba(56, 189, 248, 0.18); }
    }
    .agent-node {
        background: rgba(11, 18, 34, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-left: 3px solid #38bdf8;
        border-radius: 10px;
        padding: 1rem 1.1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 124px;
        box-sizing: border-box;
        transition: all 0.2s ease;
    }
    .agent-node.status-running {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.35) 0%, rgba(15, 23, 42, 0.92) 100%);
        border: 1px solid #00f5d4 !important;
        border-left: 4px solid #00f5d4 !important;
        animation: pulseRunning 1.8s infinite ease-in-out;
    }
    .agent-node.status-done {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.22) 0%, rgba(11, 18, 34, 0.85) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-left: 4px solid #10b981 !important;
    }
    .agent-node.status-error {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.28) 0%, rgba(11, 18, 34, 0.85) 100%);
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
        border-left: 4px solid #ef4444 !important;
    }
    .agent-node.status-queued {
        opacity: 0.62;
    }
    .agent-node-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.35rem;
    }
    .agent-step-badge {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.68rem;
        font-weight: 600;
        color: #38bdf8;
        letter-spacing: 0.05em;
    }
    .agent-batch-badge {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.64rem;
        color: #a5b4fc;
        background: rgba(99, 102, 241, 0.14);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 1px 6px;
        border-radius: 4px;
    }
    .badge-running {
        color: #00f5d4 !important;
        background: rgba(0, 245, 212, 0.14) !important;
        border-color: rgba(0, 245, 212, 0.5) !important;
    }
    .badge-done {
        color: #34d399 !important;
        background: rgba(16, 185, 129, 0.14) !important;
        border-color: rgba(16, 185, 129, 0.4) !important;
    }
    .badge-error {
        color: #f87171 !important;
        background: rgba(239, 68, 68, 0.15) !important;
        border-color: rgba(239, 68, 68, 0.45) !important;
    }
    .agent-node-title {
        color: #f1f5f9;
        font-size: 0.94rem;
        font-weight: 600;
        margin: 0 0 0.3rem 0;
    }
    .agent-node-desc {
        color: #94a3b8;
        font-size: 0.79rem;
        line-height: 1.45;
        margin: 0;
    }

    /* Live Telemetry Terminal Box */
    .telemetry-console {
        background: rgba(5, 8, 17, 0.92);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 3px solid #00f5d4;
        border-radius: 10px;
        padding: 0.85rem 1.1rem;
        margin: 0.6rem 0 1rem 0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.8rem;
        color: #cbd5e1;
        line-height: 1.65;
    }
    .telemetry-line-active {
        color: #00f5d4;
        font-weight: 600;
    }

    /* Executive Report Formatting inside Tabs */
    .exec-field-block {
        background: rgba(15, 23, 42, 0.65);
        border-left: 3px solid #38bdf8;
        padding: 0.55rem 0.95rem;
        margin: 1rem 0 0.55rem 0;
        border-radius: 0 8px 8px 0;
        font-weight: 700;
        color: #e0f2fe;
        font-size: 0.96rem;
        letter-spacing: 0.02em;
    }
    .exec-score-banner {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(56, 189, 248, 0.18));
        border: 1px solid rgba(16, 185, 129, 0.45);
        padding: 0.55rem 1.1rem;
        border-radius: 10px;
        color: #34d399;
        font-weight: 700;
        font-size: 0.98rem;
        margin: 0.8rem 0;
    }
    .cyber-hashtag {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.32);
        color: #7dd3fc;
        padding: 2px 9px;
        border-radius: 999px;
        font-size: 0.82rem;
        margin: 2px 5px 2px 0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(11, 18, 34, 0.85);
        padding: 6px;
        border-radius: 10px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        padding: 0.48rem 0.95rem;
        font-weight: 500;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.35), rgba(79, 70, 229, 0.35)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56, 189, 248, 0.45);
    }

    /* Token progress bar */
    .token-bar {
        height: 6px;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.16);
        overflow: hidden;
    }
    .token-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #00f5d4, #38bdf8, #6366f1);
        transition: width 0.4s ease;
    }
</style>
"""

PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-3.8-flash",
    "deepseek": "deepseek-chat",
    "qwen": "qwen-turbo",
    "zhipu": "glm-4-flash",
}

SECTION_METADATA = [
    ("🕵️", "市场研究", "📊 市场定位", "market_analysis", "真实竞品检索与高潜细分蓝海定位", MarketResearcher, "BATCH 01", "#38bdf8"),
    ("📦", "产品定义", "📦 产品定义", "product_plan", "提炼核心 USP 与差异化产品矩阵", ProductManager, "BATCH 02", "#60a5fa"),
    ("💰", "商业模式", "💰 商业模式", "business_model", "设计定价模型、盈亏平衡点与变现漏斗", BusinessModeler, "BATCH 03", "#818cf8"),
    ("🎨", "品牌设计", "🎨 品牌设计", "design_strategy", "输出品牌主张、视觉规范与 AI 绘图指令", ChiefDesigner, "BATCH 03", "#a78bfa"),
    ("📈", "财务规划", "📈 财务规划", "finance_plan", "测算启动资金预算与首年季度现金流表", FinancePlanner, "BATCH 04", "#34d399"),
    ("🎬", "流量脚本", "🎬 流量脚本", "marketing_script", "定制抖音/TikTok 高转化短视频分镜脚本", ContentStrategist, "BATCH 04", "#f472b6"),
    ("⚠️", "风险评估", "⚠️ 风险评估", "risk_analysis", "识别市场/供应链/合规风险与风控预案", RiskAnalyst, "BATCH 05", "#fbbf24"),
    ("🔍", "SEO策略", "🔍 SEO 策略", "seo_strategy", "挖掘高商业意图长尾词与全域增长标签", SEOExpert, "BATCH 05", "#2dd4bf"),
]

QUICK_IDEAS = [
    ("🐾 智能宠物项圈", "智能宠物健康监测项圈"),
    ("👓 近视防控配件", "儿童医疗级近视防控眼镜配件"),
    ("🏕️ 新能源露营套件", "新能源车主车尾露营套件"),
    ("🍵 东方草本气泡饮", "东方草本无糖功能性气泡饮"),
]

REPORT_FIELD_LABELS = (
    "细分领域名称", "目标受众", "痛点分析", "市场机会",
    "产品名称", "核心卖点", "差异化优势", "目标用户", "定价策略",
    "收入来源", "成本结构", "盈亏平衡点", "变现路径", "风险提示",
    "启动资金预算", "月度固定成本", "首年现金流预测", "资金来源建议", "成本控制要点", "关键财务指标",
    "市场风险", "竞争风险", "运营风险", "财务风险", "法律合规风险", "应对策略", "应急预案",
    "品牌名称", "Logo设计理念", "品牌色调", "Midjourney提示词",
    "开头3秒钩子", "脚本内容", "结尾CTA", "推荐BGM",
    "长尾关键词", "热门Hashtag", "内容优化建议",
)


def format_report_content(content: str) -> str:
    """Enhance plain-text LLM report fields into styled executive report blocks."""
    if not content:
        return ""

    lines = content.splitlines()
    formatted_lines = []
    label_pattern = re.compile(
        rf"^\s*(?:\*\*|#+\s*)?({'|'.join(REPORT_FIELD_LABELS)})(?:\*\*)?\s*[:：]\s*(.*)$"
    )
    score_pattern = re.compile(r"^\s*(?:\*\*|#+\s*)?推荐指数(?:\*\*)?\s*[:：]\s*(.+)$")

    for line in lines:
        score_match = score_pattern.match(line)
        if score_match:
            score_val = score_match.group(1).strip().strip("*").strip()
            formatted_lines.append(
                f'<div class="exec-score-banner">🎯 赛道推荐指数 // {score_val}</div>'
            )
            continue

        label_match = label_pattern.match(line)
        if label_match:
            field_name = label_match.group(1)
            rest_val = label_match.group(2).strip()
            if field_name == "热门Hashtag" and rest_val:
                tags_html = re.sub(
                    r"(#[^\s#]+)",
                    r'<span class="cyber-hashtag">\1</span>',
                    rest_val,
                )
                formatted_lines.append(f'<div class="exec-field-block">🔹 {field_name}</div>')
                formatted_lines.append(f"<div style='margin: 0.4rem 0 0.8rem 0;'>{tags_html}</div>")
            elif rest_val:
                formatted_lines.append(
                    f'<div class="exec-field-block">🔹 {field_name}</div>\n\n**{rest_val}**'
                )
            else:
                formatted_lines.append(f'<div class="exec-field-block">🔹 {field_name}</div>')
            continue

        # Convert inline #Hashtags on standalone hashtag lines
        if line.strip().startswith("#") and not line.strip().startswith("# "):
            tags_html = re.sub(
                r"(#[^\s#]+)",
                r'<span class="cyber-hashtag">\1</span>',
                line,
            )
            formatted_lines.append(tags_html)
        else:
            formatted_lines.append(line)

    return "\n".join(formatted_lines)


def get_agents(selected_names: List[str] | None = None):
    agents = []
    for emoji, name, _, key, _, cls, _, _ in SECTION_METADATA:
        if selected_names is None or name in selected_names:
            agents.append((emoji, name, cls(), key))
    return agents


def init_session_state():
    defaults = {
        "context": {},
        "results": {},
        "execution_time": 0,
        "completed_agents": [],
        "use_parallel": False,
        "enable_web_search": Config.has_search_api(),
        "selected_agents": [item[1] for item in SECTION_METADATA],
        "saved_filepath": None,
        "idea_input": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def parse_markdown_report(md_text: str) -> Dict[str, Any]:
    """Parse a saved markdown report into a context dictionary."""
    context: Dict[str, Any] = {}
    title_match = re.search(r"^#\s*🚀\s*创业方案:\s*(.+)$", md_text, re.MULTILINE)
    if title_match:
        context["industry"] = title_match.group(1).strip()

    header_positions = []
    for _, ui_name, md_header, key, _, _, _, _ in SECTION_METADATA:
        pattern = rf"^##\s*{re.escape(md_header)}\s*$"
        match = re.search(pattern, md_text, re.MULTILINE)
        if match:
            header_positions.append((match.start(), match.end(), key, ui_name))

    header_positions.sort(key=lambda x: x[0])
    for idx, (_, content_start, key, _) in enumerate(header_positions):
        content_end = header_positions[idx + 1][0] if idx + 1 < len(header_positions) else len(md_text)
        section_body = md_text[content_start:content_end].strip()
        section_body = re.sub(r"\n---\s*(\*Generated by.*)?$", "", section_body, flags=re.DOTALL).strip()
        context[key] = section_body

    return context


def list_history_files() -> List[Path]:
    """Return saved markdown files sorted by newest first."""
    output_dir = Path(__file__).parent.parent.parent / "output"
    if not output_dir.exists():
        return []
    return sorted(output_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)


def render_header():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    llm_cfg = Config.get_llm_config()
    active_model = llm_cfg.get("model", "gemini-3.8-flash").upper()
    mode_str = "DAG PARALLEL (5-STAGE)" if st.session_state.get("use_parallel") else "SEQUENTIAL SAFE"
    if not st.session_state.get("enable_web_search", False):
        search_str = "AI KNOWLEDGE BASE (FAST)"
    else:
        search_str = "SERPER PRO API" if Config.has_search_api() else "DUCKDUCKGO LIVE"
    selected_count = len(st.session_state.get("selected_agents", SECTION_METADATA))

    st.markdown(f"""
        <div class="hud-bar">
            <div class="hud-item">
                <span class="hud-dot"></span>
                <div>
                    <p class="hud-label">SYSTEM TELEMETRY</p>
                    <p class="hud-value">ONLINE · {selected_count}/8 AGENTS READY</p>
                </div>
            </div>
            <div class="hud-item">
                <div>
                    <p class="hud-label">NEURAL ENGINE</p>
                    <p class="hud-value">{active_model}</p>
                </div>
            </div>
            <div class="hud-item">
                <div>
                    <p class="hud-label">EXECUTION TOPOLOGY</p>
                    <p class="hud-value">{mode_str}</p>
                </div>
            </div>
            <div class="hud-item">
                <div>
                    <p class="hud-label">MARKET INTELLIGENCE</p>
                    <p class="hud-value">{search_str}</p>
                </div>
            </div>
        </div>
        <div class="hero-wrap">
            <div class="hero-badge">⚡ AUTONOMOUS VENTURE INTELLIGENCE OS // V2.5</div>
            <h1 class="hero-title">BizGenesis 商业决策矩阵</h1>
            <p class="hero-sub">多智能体协同商业推演系统 · 从赛道洞察、产品建模、财务精算到增长获客的一站式商业计划引擎</p>
        </div>
    """, unsafe_allow_html=True)


def apply_runtime_llm_settings(provider: str, model_name: str, api_key_override: str):
    """Apply user-selected LLM provider/model/key to Config at runtime."""
    Config.LLM_PROVIDER = provider
    model_attr_map = {
        "openai": ("OPENAI_MODEL", "OPENAI_API_KEY"),
        "gemini": ("GEMINI_MODEL", "GEMINI_API_KEY"),
        "deepseek": ("DEEPSEEK_MODEL", "DEEPSEEK_API_KEY"),
        "qwen": ("QWEN_MODEL", "QWEN_API_KEY"),
        "zhipu": ("ZHIPU_MODEL", "ZHIPU_API_KEY"),
    }
    if provider in model_attr_map:
        model_attr, key_attr = model_attr_map[provider]
        if model_name.strip():
            setattr(Config, model_attr, model_name.strip())
        if api_key_override.strip():
            setattr(Config, key_attr, api_key_override.strip())


def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ 核心引擎中枢")

        providers = list(PROVIDER_DEFAULT_MODELS.keys())
        current_provider = Config.LLM_PROVIDER if Config.LLM_PROVIDER in providers else "openai"
        selected_provider = st.selectbox(
            "模型服务商 (Provider)",
            options=providers,
            index=providers.index(current_provider),
            format_func=lambda p: {
                "openai": "OpenAI",
                "gemini": "Google Gemini",
                "deepseek": "DeepSeek",
                "qwen": "阿里通义千问 (Qwen)",
                "zhipu": "智谱 GLM (Zhipu)",
            }.get(p, p),
        )

        Config.LLM_PROVIDER = selected_provider
        llm_config = Config.get_llm_config()
        default_model = llm_config["model"] or PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
        model_name = st.text_input("模型标识 (Model ID)", value=default_model)
        api_key_override = st.text_input(
            "临时 API Key（可选）",
            value="",
            type="password",
            placeholder="留空则默认读取 .env 配置",
        )
        apply_runtime_llm_settings(selected_provider, model_name, api_key_override)

        st.session_state.use_parallel = st.toggle(
            "⚡ 启用 DAG 并行推演",
            value=st.session_state.get("use_parallel", False),
            help="开启后分 5 批次并发执行无依赖关系的 Agent，提速 30-50%",
        )

        st.session_state.enable_web_search = st.toggle(
            "📡 启用外部联网搜索",
            value=st.session_state.get("enable_web_search", Config.has_search_api()),
            help="默认使用大模型知识库极速推演；开启后将额外调用 DuckDuckGo/Serper 搜索竞品（国内无代理环境下建议关闭以免超时等待）。",
        )

        all_agent_names = [item[1] for item in SECTION_METADATA]
        curr_selected = st.session_state.get("selected_agents", all_agent_names)
        with st.expander(f"🧩 执行模块配置 ({len(curr_selected)}/8)", expanded=False):
            selected_agents = st.multiselect(
                "勾选需要运行的 Agent",
                options=all_agent_names,
                default=curr_selected,
                label_visibility="collapsed",
            )
            st.session_state.selected_agents = selected_agents or all_agent_names

        st.divider()
        render_history_section()
        st.divider()
        render_token_usage()


def render_history_section():
    st.markdown("### 📂 商业档案库")
    history_files = list_history_files()
    if not history_files:
        st.caption("暂无历史归档方案")
        return

    selected_file = st.selectbox(
        "选择历史方案",
        options=history_files,
        format_func=lambda p: p.stem,
        label_visibility="collapsed",
    )
    if st.button("📖 调取此商业档案", use_container_width=True):
        try:
            md_text = selected_file.read_text(encoding="utf-8")
            parsed_ctx = parse_markdown_report(md_text)
            st.session_state.context = parsed_ctx
            st.session_state.results = {
                ui_name: parsed_ctx.get(key, "")
                for _, ui_name, _, key, _, _, _, _ in SECTION_METADATA
                if parsed_ctx.get(key)
            }
            st.session_state.saved_filepath = selected_file
            st.session_state.execution_time = 0
            st.toast(f"✅ 已调取：{selected_file.name}")
            st.rerun()
        except Exception as e:
            st.error(f"加载失败: {e}")


def render_token_usage():
    st.markdown("### 📊 算力与成本遥测")
    token_monitor = get_token_monitor()
    summary = token_monitor.get_usage_summary()

    if summary["total_tokens"] > 0:
        limit = summary["budget"]["limit"] or 100000
        usage_pct = min(100, (summary["total_tokens"] / limit) * 100)
        st.markdown(f"""
            <div style="margin: 0.5rem 0 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem; font-size: 0.85rem;">
                    <span style="color: #94a3b8;">累计 Token</span>
                    <span style="font-weight: 600; color: #38bdf8;">{summary['total_tokens']:,}</span>
                </div>
                <div class="token-bar">
                    <div class="token-bar-fill" style="width: {usage_pct}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.metric("预估 API 成本", f"${summary['total_cost']:.4f}")
    else:
        st.caption("当前会话算力消耗：0 Tokens")


def render_input_section():
    with st.container(border=True):
        col_input, col_button = st.columns([4.5, 1.2], vertical_alignment="center")

        with col_input:
            idea = st.text_input(
                "创业想法",
                value=st.session_state.get("idea_input", ""),
                placeholder="输入目标创业赛道、新消费单品或 AI 商业概念（如：智能宠物健康监测项圈）",
                label_visibility="collapsed",
            )

        with col_button:
            start_btn = st.button(
                "🚀 启动商业推演",
                type="primary",
                use_container_width=True,
            )

        chip_cols = st.columns(4)
        for idx, (short_label, full_idea) in enumerate(QUICK_IDEAS):
            with chip_cols[idx]:
                if st.button(short_label, key=f"chip_{idx}", use_container_width=True):
                    st.session_state.idea_input = full_idea
                    st.rerun()

        with st.expander("🎯 商业要素与边界约束配置（启动资金 / 目标市场 / 团队基因）", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                budget_scale = st.selectbox(
                    "💰 启动资金规模",
                    options=[
                        "不限",
                        "< 5万元（个人/副业轻资产）",
                        "5~30万元（初创小团队）",
                        "30~100万元（标准创业项目）",
                        "100万元以上（融资/规模化扩张）",
                    ],
                )
            with c2:
                target_market = st.selectbox(
                    "🌍 目标市场区域",
                    options=[
                        "不限",
                        "国内市场（抖音/小红书/天猫/微信私域）",
                        "海外出海（TikTok/独立站/Amazon）",
                        "国内外双栖市场",
                    ],
                )
            with c3:
                team_type = st.selectbox(
                    "👥 团队形态",
                    options=[
                        "不限",
                        "一人公司 / 独立创客",
                        "2~5人互补小团队",
                        "成熟团队 / 供应链工厂转型",
                    ],
                )
            extra_requirements = st.text_input(
                "📝 战略补充要求（可选）",
                placeholder="例如：不做线下重资产门店、主打礼盒高溢价、优先通过短视频带货冷启动...",
            )

    constraints = {
        "budget_scale": budget_scale,
        "target_market": target_market,
        "team_type": team_type,
        "extra_requirements": extra_requirements.strip(),
        "enable_web_search": st.session_state.get("enable_web_search", False),
    }
    return idea, start_btn, constraints


def build_agent_matrix_html(agent_states: Dict[str, Dict[str, Any]] | None = None) -> str:
    """Build HTML for the 8-Agent matrix with optional live execution status."""
    nodes_html = []
    for idx, (emoji, name, _, _, desc, _, batch_tag, accent_color) in enumerate(SECTION_METADATA, start=1):
        state = (agent_states or {}).get(name, {})
        status = state.get("status", "idle")  # idle, queued, running, done, error
        duration = state.get("duration")

        node_cls = "agent-node"
        badge_cls = "agent-batch-badge"
        badge_text = batch_tag
        border_style = f"border-left-color: {accent_color};"

        if status == "running":
            node_cls += " status-running"
            badge_cls += " badge-running"
            badge_text = "⚡ RUNNING..."
            border_style = ""
        elif status == "done":
            node_cls += " status-done"
            badge_cls += " badge-done"
            badge_text = f"✓ DONE ({duration:.1f}s)" if duration else "✓ COMPLETED"
            border_style = ""
        elif status == "error":
            node_cls += " status-error"
            badge_cls += " badge-error"
            badge_text = "✗ ERROR"
            border_style = ""
        elif status == "queued":
            node_cls += " status-queued"
            badge_text = f"⏳ {batch_tag}"

        nodes_html.append(
            f'<div class="{node_cls}" style="{border_style}">'
            f'<div>'
            f'<div class="agent-node-head">'
            f'<span class="agent-step-badge">NODE 0{idx}</span>'
            f'<span class="{badge_cls}">{badge_text}</span>'
            f'</div>'
            f'<p class="agent-node-title">{emoji} {name}</p>'
            f'<p class="agent-node-desc">{desc}</p>'
            f'</div>'
            f'</div>'
        )

    return (
        '<div class="sec-header">'
        '<p class="sec-title">🧩 8-Agent 商业推演拓扑矩阵</p>'
        '<span class="sec-tag">PIPELINE TOPOLOGY // LIVE STATUS</span>'
        '</div>'
        f'<div class="bento-grid-4">{"".join(nodes_html)}</div>'
    )


def render_telemetry_logs(placeholder, logs: List[str]):
    """Render live telemetry logs inside a sci-fi terminal box."""
    lines_html = []
    for idx, log_line in enumerate(logs[-6:]):
        cls = "telemetry-line-active" if idx == len(logs[-6:]) - 1 else ""
        lines_html.append(f'<div class="{cls}">{log_line}</div>')
    placeholder.markdown(
        f'<div class="telemetry-console">{"".join(lines_html)}</div>',
        unsafe_allow_html=True,
    )


def run_analysis(idea: str, constraints: Dict[str, Any]) -> bool:
    llm_cfg = Config.get_llm_config()
    if not llm_cfg.get("api_key"):
        provider_upper = Config.LLM_PROVIDER.upper()
        st.error(
            f"❌ 未检测到 **{provider_upper}_API_KEY**！请在左侧边栏「临时 API Key」填入密钥，或在 `.env` 文件中配置后再启动。"
        )
        return False

    start_time = time.time()
    st.session_state.context = {"industry": idea, **constraints}
    st.session_state.results = {}
    st.session_state.completed_agents = []

    agents_info = get_agents(st.session_state.get("selected_agents"))
    total = len(agents_info)
    active_model = llm_cfg.get("model", "gemini-3.8-flash")

    progress_bar = st.progress(0, text="🤖 商业推演矩阵初始化中...")
    telemetry_slot = st.empty()
    matrix_slot = st.empty()
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    live_preview_slot = st.empty()

    # Initialize live state for all 8 agents
    selected_set = {name for _, name, _, _ in agents_info}
    agent_states: Dict[str, Dict[str, Any]] = {
        item[1]: {"status": "queued" if item[1] in selected_set else "idle"}
        for item in SECTION_METADATA
    }
    telemetry_logs: List[str] = [
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 商业推演引擎已点火 · 目标赛道: 【{idea}】 · 驱动内核: {active_model}"
    ]
    matrix_slot.markdown(build_agent_matrix_html(agent_states), unsafe_allow_html=True)
    render_telemetry_logs(telemetry_slot, telemetry_logs)

    if st.session_state.get("use_parallel", False) and total > 1:
        executor = get_parallel_executor()
        class_to_meta = {
            agent.__class__.__name__: (emoji, name, agent, key)
            for emoji, name, agent, key in agents_info
        }
        batches = executor.get_parallelization_plan(list(class_to_meta.keys()))
        completed = 0

        for batch_idx, batch in enumerate(batches, start=1):
            batch_labels = [class_to_meta[cls_name][1] for cls_name in batch]
            for label in batch_labels:
                agent_states[label]["status"] = "running"
            matrix_slot.markdown(build_agent_matrix_html(agent_states), unsafe_allow_html=True)

            telemetry_logs.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ 启动并行批次 0{batch_idx}/0{len(batches)} · 正在并发推演: [{', '.join(batch_labels)}]..."
            )
            render_telemetry_logs(telemetry_slot, telemetry_logs)
            progress_bar.progress(
                completed / total,
                text=f"⚡ DAG 并行批次 0{batch_idx}/0{len(batches)}: 正在同步推演 [{', '.join(batch_labels)}]..."
            )

            batch_start = time.time()
            batch_agents = [class_to_meta[cls_name][2] for cls_name in batch]
            result = executor.execute_parallel(batch_agents, st.session_state.context)
            batch_elapsed = time.time() - batch_start
            st.session_state.context = result.context

            for cls_name in batch:
                emoji, name, _, key = class_to_meta[cls_name]
                content = st.session_state.context.get(key, "")
                st.session_state.results[name] = content
                st.session_state.completed_agents.append(name)
                agent_states[name] = {
                    "status": "done" if content else "error",
                    "duration": batch_elapsed,
                }
                completed += 1

            matrix_slot.markdown(build_agent_matrix_html(agent_states), unsafe_allow_html=True)
            telemetry_logs.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 批次 0{batch_idx}/0{len(batches)} [{', '.join(batch_labels)}] 推演完毕 (耗时 {batch_elapsed:.1f}s)"
            )
            render_telemetry_logs(telemetry_slot, telemetry_logs)

            # Auto-display the latest completed section in live preview
            last_cls = batch[-1]
            last_emoji, last_name, _, last_key = class_to_meta[last_cls]
            last_content = st.session_state.context.get(last_key, "")
            if last_content:
                with live_preview_slot.container(border=True):
                    st.markdown(
                        f"#### 📡 实时生成预览 · {last_emoji} {last_name} "
                        f"<span class='sec-tag'>LIVE STREAM // {completed}/{total} DONE</span>",
                        unsafe_allow_html=True,
                    )
                    st.divider()
                    st.markdown(format_report_content(last_content), unsafe_allow_html=True)
    else:
        for idx, (emoji, name, agent, key) in enumerate(agents_info, start=1):
            agent_states[name]["status"] = "running"
            matrix_slot.markdown(build_agent_matrix_html(agent_states), unsafe_allow_html=True)
            telemetry_logs.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ 正在推演节点 (0{idx}/0{total}): [{emoji} {name}]..."
            )
            render_telemetry_logs(telemetry_slot, telemetry_logs)
            progress_bar.progress(
                (idx - 1) / total,
                text=f"{emoji} 正在推演 (0{idx}/0{total}): {name}..."
            )

            step_start = time.time()
            try:
                st.session_state.context = agent.run_with_degradation(
                    st.session_state.context,
                    fallback_key=key
                )
                step_elapsed = time.time() - step_start
                content = st.session_state.context.get(key, "")
                st.session_state.results[name] = content
                st.session_state.completed_agents.append(name)
                agent_states[name] = {"status": "done", "duration": step_elapsed}
                telemetry_logs.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 节点 [{name}] 推演完成 (耗时 {step_elapsed:.1f}s)"
                )
                if content:
                    with live_preview_slot.container(border=True):
                        st.markdown(
                            f"#### 📡 实时生成预览 · {emoji} {name} "
                            f"<span class='sec-tag'>LIVE STREAM // {idx}/{total} DONE</span>",
                            unsafe_allow_html=True,
                        )
                        st.divider()
                        st.markdown(format_report_content(content), unsafe_allow_html=True)
            except Exception as e:
                step_elapsed = time.time() - step_start
                st.session_state.results[name] = f"⚠️ 分析失败: {e}"
                st.session_state.completed_agents.append(name)
                agent_states[name] = {"status": "error", "duration": step_elapsed}
                telemetry_logs.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 节点 [{name}] 异常: {e}"
                )

            matrix_slot.markdown(build_agent_matrix_html(agent_states), unsafe_allow_html=True)
            render_telemetry_logs(telemetry_slot, telemetry_logs)

    progress_bar.progress(1.0, text="✅ 全链路商业推演已完成！")
    st.session_state.execution_time = time.time() - start_time
    filepath = save_to_markdown(st.session_state.context, idea)
    st.session_state.saved_filepath = filepath
    return True


def save_to_markdown(context, idea, existing_filepath: Path | None = None):
    output_dir = Path(__file__).parent.parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    if existing_filepath and existing_filepath.exists():
        filepath = existing_filepath
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_idea = idea.replace("/", "_").replace(" ", "_")[:15]
        filepath = output_dir / f"{safe_idea}_{timestamp}.md"
    sections = [
        (md_header, context.get(key, ""))
        for _, _, md_header, key, _, _, _, _ in SECTION_METADATA
    ]
    lines = [f"# 🚀 创业方案: {idea}", "", f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for title, body in sections:
        lines += ["---", "", f"## {title}", "", body, ""]
    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


def render_results():
    industry_title = st.session_state.context.get("industry", "商业方案")
    meta_right = (
        f"EXECUTION TIME // {st.session_state.execution_time:.1f}S"
        if st.session_state.execution_time > 0
        else f"ARCHIVE // {Path(st.session_state.saved_filepath).name}"
        if st.session_state.get("saved_filepath")
        else "STATUS // READY"
    )

    st.markdown(f"""
        <div class="sec-header">
            <p class="sec-title">📊 商业推演全景报告 · <span style="color:#38bdf8;">{industry_title}</span></p>
            <span class="sec-tag">{meta_right}</span>
        </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([f"{emoji} {name}" for emoji, name, _, _, _, _, _, _ in SECTION_METADATA])

    for tab, (emoji, name, _, key, desc, agent_cls, batch_tag, _) in zip(tabs, SECTION_METADATA):
        with tab:
            content = st.session_state.context.get(key, "")
            if content and not content.startswith("⚠️"):
                with st.container(border=True):
                    st.markdown(
                        f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                        f"<h4 style='margin:0;'>{emoji} {name} <span style='font-size:0.84rem;color:#94a3b8;font-weight:400;'>— {desc}</span></h4>"
                        f"<span class='sec-tag'>{batch_tag}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.divider()
                    st.markdown(format_report_content(content), unsafe_allow_html=True)
            else:
                st.info(content or "该模块未生成数据")

            with st.expander(f"🔄 针对「{name}」追加指令并单独重演"):
                feedback = st.text_input(
                    f"输入对 {name} 的修改要求",
                    key=f"refine_input_{key}",
                    placeholder=f"例如：请把 {name} 改得更聚焦于低预算冷启动，补充量化测算表格...",
                )
                if st.button(f"✨ 重新推演「{name}」", key=f"refine_btn_{key}"):
                    if not feedback.strip():
                        st.warning("请先输入修改要求")
                    else:
                        with st.spinner(f"正在重新推演「{name}」..."):
                            try:
                                agent = agent_cls(use_memory=True)
                                st.session_state.context = agent.refine(
                                    st.session_state.context,
                                    feedback.strip(),
                                    key,
                                )
                                st.session_state.results[name] = st.session_state.context.get(key, "")
                                idea = st.session_state.context.get("industry", "商业计划")
                                st.session_state.saved_filepath = save_to_markdown(
                                    st.session_state.context,
                                    idea,
                                    st.session_state.get("saved_filepath"),
                                )
                                st.toast(f"✅ 「{name}」已更新并归档！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"重新生成失败: {e}")


def build_markdown_string(context: Dict[str, Any]) -> str:
    """Build full markdown report string for download/copy."""
    idea = context.get("industry", "商业计划")
    lines = [f"# 🚀 创业方案: {idea}", "", f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for _, _, md_header, key, _, _, _, _ in SECTION_METADATA:
        body = context.get(key, "")
        if body:
            lines += ["---", "", f"## {md_header}", "", body, ""]
    return "\n".join(lines)


def render_export_section():
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### 📥 商业交付物导出")
        col1, col2, col3 = st.columns([2, 2, 1.5], vertical_alignment="center")
        industry_name = st.session_state.context.get("industry", "plan")
        md_report = build_markdown_string(st.session_state.context)

        with col1:
            st.download_button(
                label="📝 导出 Markdown 报告 (.md)",
                data=md_report.encode("utf-8"),
                file_name=f"bizgenesis_{industry_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:
            try:
                config = PDFExportConfig(
                    title=f"创业方案: {industry_name}",
                    include_watermark=True,
                    watermark_text="BizGenesis AI"
                )
                exporter = get_pdf_exporter(config)
                pdf_bytes = exporter.export(st.session_state.context)

                st.download_button(
                    label="📄 导出路演级 PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"bizgenesis_{industry_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF 导出失败: {e}")

        with col3:
            if st.button("🗑️ 重置工作台", use_container_width=True):
                st.session_state.results = {}
                st.session_state.context = {}
                st.rerun()

        with st.expander("📋 展开预览 / 一键复制 Markdown 源码"):
            st.code(md_report, language="markdown")


def render_right_panel():
    st.markdown("""
        <div class="sec-header">
            <p class="sec-title">✨ 核心商业引擎架构</p>
            <span class="sec-tag">CORE ARCHITECTURE // 04 MODULES</span>
        </div>
        <div class="bento-grid-4">
            <div class="cyber-card">
                <div>
                    <div class="cyber-card-top">
                        <div class="cyber-icon">🌐</div>
                        <span class="cyber-code">SYS.01 // MULTI-LLM</span>
                    </div>
                    <p class="cyber-title">多核大模型中枢</p>
                    <p class="cyber-desc">原生驱动 Gemini 3.8、OpenAI 与 DeepSeek，支持在线热切换与算力遥测。</p>
                </div>
            </div>
            <div class="cyber-card">
                <div>
                    <div class="cyber-card-top">
                        <div class="cyber-icon">⚡</div>
                        <span class="cyber-code">SYS.02 // DAG ENGINE</span>
                    </div>
                    <p class="cyber-title">5 阶段 DAG 并行推演</p>
                    <p class="cyber-desc">基于有向无环图调度 8 大职能 Agent，保障上下文严密衔接并提速 30%~50%。</p>
                </div>
            </div>
            <div class="cyber-card">
                <div>
                    <div class="cyber-card-top">
                        <div class="cyber-icon">📡</div>
                        <span class="cyber-code">SYS.03 // LIVE INTEL</span>
                    </div>
                    <p class="cyber-title">实时竞品情报检索</p>
                    <p class="cyber-desc">自动抓取赛道头部玩家、市场趋势与高转化词库，拒绝脱离实际的空洞臆测。</p>
                </div>
            </div>
            <div class="cyber-card">
                <div>
                    <div class="cyber-card-top">
                        <div class="cyber-icon">🔄</div>
                        <span class="cyber-code">SYS.04 // HOT REFINE</span>
                    </div>
                    <p class="cyber-title">单模块记忆级精修</p>
                    <p class="cyber-desc">内置多轮上下文记忆，可针对任意单一商业章节下达修改指令并导出 PDF。</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(build_agent_matrix_html(), unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="BizGenesis · 商业决策矩阵", page_icon="🚀", layout="wide")
    init_session_state()
    render_header()
    render_sidebar()

    idea, start_btn, constraints = render_input_section()

    if start_btn and idea:
        if run_analysis(idea, constraints):
            st.rerun()

    if st.session_state.results:
        render_results()
        render_export_section()
    else:
        render_right_panel()


if __name__ == "__main__":
    main()
