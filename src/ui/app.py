"""
Streamlit Web UI for BizGenesis with modern design.
Run with: streamlit run src/ui/app.py
"""
import sys
import time
from pathlib import Path
from typing import Dict, Any

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


# Custom CSS for modern design
CUSTOM_CSS = """
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        color: white;
    }

    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }

    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* Card styling */
    .stCard {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Button styling */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #667eea;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255,255,255,0.05);
    }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Agent status indicators */
    .agent-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
    }

    .agent-status.running {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    .agent-status.completed {
        background: rgba(76, 175, 80, 0.1);
        color: #4caf50;
    }

    /* Result cards */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }

    .result-card h3 {
        color: #333;
        margin-bottom: 1rem;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Export buttons */
    .export-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* Token usage bar */
    .token-bar {
        height: 8px;
        border-radius: 4px;
        background: #e0e0e0;
        overflow: hidden;
    }

    .token-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transition: width 0.5s ease;
    }
</style>
"""


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "context": {},
        "current_step": 0,
        "results": {},
        "execution_time": 0,
        "use_parallel": True,
        "running": False,
        "completed_agents": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_header():
    """Render animated header."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("""
        <div class="main-header animate-in">
            <h1>🚀 BizGenesis</h1>
            <p>AI 驱动的创业辅助系统 · 从想法到完整商业方案</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render settings sidebar."""
    with st.sidebar:
        # Logo area
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #667eea;">⚙️ 设置</h2>
            </div>
        """, unsafe_allow_html=True)

        # Model info card
        llm_config = Config.get_llm_config()
        st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1rem; margin: 1rem 0;">
                <p style="color: #666; font-size: 0.9rem; margin: 0;">当前模型</p>
                <p style="font-weight: 600; color: #333; margin: 0.25rem 0 0 0;">{llm_config['model']}</p>
            </div>
        """, unsafe_allow_html=True)

        # Search API status
        if Config.has_search_api():
            st.success("✅ 搜索 API 已配置")
        else:
            st.info("ℹ️ 使用 DuckDuckGo 搜索")

        st.divider()

        # Execution mode toggle
        st.markdown("### ⚡ 执行模式")
        st.session_state.use_parallel = st.toggle(
            "启用并行执行",
            value=st.session_state.use_parallel,
            help="并行执行可加速 30-50%"
        )

        if st.session_state.use_parallel:
            st.caption("✓ 已启用并行优化")

        st.divider()

        # Token usage card
        render_token_usage()

        st.divider()

        # Help section
        with st.expander("💡 使用帮助"):
            st.markdown("""
                **如何使用：**
                1. 在输入框填写创业想法
                2. 点击「开始分析」按钮
                3. 等待 AI 团队协作完成
                4. 查看各模块分析结果
                5. 导出 PDF 或复制内容

                **提示：** 输入越具体，分析质量越高
            """)


def render_token_usage():
    """Render token usage statistics."""
    st.markdown("### 📊 Token 使用")

    token_monitor = get_token_monitor()
    summary = token_monitor.get_usage_summary()

    if summary["total_tokens"] > 0:
        # Usage bar
        usage_pct = min(100, (summary["total_tokens"] / 100000) * 100)
        st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #666;">已使用</span>
                    <span style="font-weight: 600;">{summary['total_tokens']:,} tokens</span>
                </div>
                <div class="token-bar">
                    <div class="token-bar-fill" style="width: {usage_pct}%;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Cost metric
        st.metric("预估成本", f"${summary['total_cost']:.4f}")

        # Agent breakdown
        with st.expander("查看详情"):
            for agent_name, usage in summary["by_agent"].items():
                st.caption(f"{agent_name}: {usage['tokens']:,} (${usage['cost']:.4f})")
    else:
        st.info("暂无使用数据")


def render_input_section():
    """Render main input section with aligned elements."""
    st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-bottom: 1.5rem; text-align: center;">💡 告诉我你的创业想法</h2>
        </div>
    """, unsafe_allow_html=True)

    # Create columns with vertical alignment
    col_input, col_button = st.columns([5, 1], vertical_alignment="center")

    with col_input:
        idea = st.text_input(
            "创业想法",
            placeholder="例如：智能宠物喂食器、环保包装材料、AI 健身教练...",
            label_visibility="collapsed"
        )

    with col_button:
        start_btn = st.button(
            "🚀 开始分析",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running
        )

    return idea, start_btn

    return idea, start_btn


def render_right_panel():
    """Render the right panel content (shown when not running)."""
    st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 1.5rem; margin-top: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-bottom: 1rem;">✨ 功能特性</h3>
        </div>
    """, unsafe_allow_html=True)

    # Feature cards
    features = [
        ("🤖", "8 个 AI Agent", "市场研究、产品设计、商业模式、财务规划、风险评估、品牌设计、营销策略、SEO 优化"),
        ("⚡", "并行执行", "智能识别可并行任务，执行速度提升 30-50%"),
        ("💰", "成本透明", "实时追踪 Token 消耗，精确计算 API 调用成本"),
        ("📄", "一键导出", "支持 Markdown 和 PDF 格式导出完整方案"),
        ("🔍", "竞品数据", "自动搜索真实竞品信息，提供数据支撑"),
        ("🛡️", "错误降级", "单个 Agent 失败不影响整体流程"),
    ]

    for emoji, title, desc in features:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        border-radius: 12px;
                        padding: 1rem;
                        margin: 0.75rem 0;
                        border-left: 4px solid #667eea;
                        transition: transform 0.2s;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">{emoji}</span>
                    <div>
                        <p style="font-weight: 600; color: #333; margin: 0;">{title}</p>
                        <p style="color: #666; font-size: 0.85rem; margin: 0.25rem 0 0 0;">{desc}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Workflow visualization
    st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h3 style="color: #333; margin-bottom: 1rem;">🔄 执行流程</h3>
        </div>
    """, unsafe_allow_html=True)

    # Flow steps
    steps = [
        ("1", "输入想法", "#667eea"),
        ("2", "AI 分析", "#764ba2"),
        ("3", "生成方案", "#f093fb"),
        ("4", "导出结果", "#4facfe"),
    ]

    # Build flow HTML without indentation to avoid code block rendering
    step_html_parts = ['<div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0;">']

    for i, (num, text, color) in enumerate(steps):
        step_html_parts.append(f'<div style="text-align: center; flex: 1;"><div style="width: 40px; height: 40px; background: {color}; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: 600; margin-bottom: 0.5rem;">{num}</div><p style="color: #666; font-size: 0.85rem; margin: 0;">{text}</p></div>')
        if i < len(steps) - 1:
            step_html_parts.append('<div style="flex: 0.5; text-align: center;"><span style="color: #ccc; font-size: 1.5rem;">→</span></div>')

    step_html_parts.append('</div>')
    step_html = ''.join(step_html_parts)
    st.markdown(step_html, unsafe_allow_html=True)

    # Tips section
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 16px;
                    padding: 1.25rem;
                    margin-top: 1.5rem;
                    color: white;">
            <h4 style="margin: 0 0 0.75rem 0;">💡 小贴士</h4>
            <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.9rem; line-height: 1.6;">
                <li>描述越具体，分析结果越精准</li>
                <li>可以输入行业关键词或完整想法</li>
                <li>启用并行执行可大幅缩短等待时间</li>
                <li>每个 Agent 都会基于前文内容分析</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


def render_progress(agents_info, current_batch=None):
    """Render execution progress with agent status."""
    st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
            <h3 style="color: #333; margin-bottom: 1rem;">🤖 AI 团队工作中</h3>
    """, unsafe_allow_html=True)

    progress = len(st.session_state.completed_agents) / len(agents_info)
    st.progress(progress, text=f"进度: {int(progress * 100)}%")

    # Agent status grid
    cols = st.columns(4)
    for i, (emoji, name, key) in enumerate(agents_info):
        with cols[i % 4]:
            if name in st.session_state.completed_agents:
                st.success(f"{emoji} {name}")
            elif current_batch and name in current_batch:
                st.info(f"⏳ {emoji} {name}")
            else:
                st.caption(f"⏸️ {emoji} {name}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_results():
    """Render analysis results in tabs."""
    st.markdown("""
        <div style="margin-top: 2rem;">
            <h2 style="color: white; text-align: center; margin-bottom: 1rem;">📊 分析结果</h2>
        </div>
    """, unsafe_allow_html=True)

    # Success message
    if st.session_state.execution_time > 0:
        st.success(f"✅ 分析完成！耗时 {st.session_state.execution_time:.1f} 秒")

    # Results tabs
    tabs_data = [
        ("🕵️", "市场研究", "market_analysis", "#667eea"),
        ("📦", "产品定义", "product_plan", "#764ba2"),
        ("💰", "商业模式", "business_model", "#f093fb"),
        ("📈", "财务规划", "finance_plan", "#4facfe"),
        ("⚠️", "风险评估", "risk_analysis", "#fa709a"),
        ("🎨", "品牌设计", "design_strategy", "#43e97b"),
        ("🎬", "流量脚本", "marketing_script", "#fa709a"),
        ("🔍", "SEO策略", "seo_strategy", "#38f9d7"),
    ]

    tabs = st.tabs([f"{emoji} {name}" for emoji, name, _, _ in tabs_data])

    for tab, (_, name, key, color) in zip(tabs, tabs_data):
        with tab:
            content = st.session_state.context.get(key, "")
            if content:
                st.markdown(f"""
                    <div class="result-card" style="border-left-color: {color};">
                        <h3>{name}</h3>
                        <div style="color: #555; line-height: 1.6;">
                            {content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("暂无数据")


def render_export_section():
    """Render export buttons."""
    st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 1.5rem; margin: 2rem 0;">
            <h3 style="color: #333; margin-bottom: 1rem;">📥 导出方案</h3>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 复制 Markdown", use_container_width=True):
            full_report = "\n\n---\n\n".join([
                f"## {name}\n\n{content}"
                for name, content in st.session_state.results.items()
            ])
            st.code(full_report, language="markdown")
            st.toast("✅ 已复制到剪贴板！")

    with col2:
        try:
            config = PDFExportConfig(
                title=f"创业方案: {st.session_state.context.get('industry', '商业计划')}",
                include_watermark=True,
                watermark_text="BizGenesis AI"
            )
            exporter = get_pdf_exporter(config)
            pdf_bytes = exporter.export(st.session_state.context)

            st.download_button(
                label="📄 下载 PDF",
                data=pdf_bytes,
                file_name=f"bizgenesis_{st.session_state.context.get('industry', 'plan')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF 导出失败: {e}")

    with col3:
        # Stats
        if st.session_state.execution_time > 0:
            st.metric("⏱️ 执行时间", f"{st.session_state.execution_time:.1f}s")

    st.markdown("</div>", unsafe_allow_html=True)


def run_analysis(idea: str):
    """Run the analysis with agents."""
    start_time = time.time()
    st.session_state.running = True
    st.session_state.completed_agents = []

    st.session_state.context = {"industry": idea}
    st.session_state.results = {}

    agents_info = [
        ("🕵️", "市场研究", MarketResearcher(), "market_analysis"),
        ("📦", "产品定义", ProductManager(), "product_plan"),
        ("💰", "商业模式", BusinessModeler(), "business_model"),
        ("📈", "财务规划", FinancePlanner(), "finance_plan"),
        ("⚠️", "风险评估", RiskAnalyst(), "risk_analysis"),
        ("🎨", "品牌设计", ChiefDesigner(), "design_strategy"),
        ("🎬", "流量脚本", ContentStrategist(), "marketing_script"),
        ("🔍", "SEO策略", SEOExpert(), "seo_strategy"),
    ]

    if st.session_state.use_parallel:
        # Parallel execution
        executor = get_parallel_executor()
        agent_names = [agent.__class__.__name__ for _, _, agent, _ in agents_info]
        batches = executor.get_parallelization_plan(agent_names)

        for batch in batches:
            batch_agents = [
                (emoji, name, agent, key)
                for emoji, name, agent, key in agents_info
                if agent.__class__.__name__ in batch
            ]

            if len(batch_agents) == 1:
                emoji, name, agent, key = batch_agents[0]
                st.session_state.context = agent.run(st.session_state.context)
                st.session_state.results[name] = st.session_state.context.get(key, "")
                st.session_state.completed_agents.append(name)
            else:
                agent_instances = [agent for _, _, agent, _ in batch_agents]
                result = executor.execute_parallel(agent_instances, st.session_state.context)
                st.session_state.context = result.context
                for emoji, name, _, key in batch_agents:
                    st.session_state.results[name] = st.session_state.context.get(key, "")
                    st.session_state.completed_agents.append(name)

            # Rerun to update UI
            st.rerun()
    else:
        # Sequential execution
        for emoji, name, agent, key in agents_info:
            st.session_state.context = agent.run(st.session_state.context)
            st.session_state.results[name] = st.session_state.context.get(key, "")
            st.session_state.completed_agents.append(name)

    st.session_state.execution_time = time.time() - start_time
    st.session_state.running = False
    st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="BizGenesis - AI 创业辅助系统",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()
    render_header()
    render_sidebar()

    # Create two columns for main content
    if st.session_state.running or st.session_state.results:
        # When running or showing results, use full width
        main_col = st.container()
        with main_col:
            idea, start_btn = render_input_section()

            # Handle start
            if start_btn and idea and not st.session_state.running:
                run_analysis(idea)

            # Show progress if running
            if st.session_state.running:
                agents_info = [
                    ("🕵️", "市场研究", "market_analysis"),
                    ("📦", "产品定义", "product_plan"),
                    ("💰", "商业模式", "business_model"),
                    ("📈", "财务规划", "finance_plan"),
                    ("⚠️", "风险评估", "risk_analysis"),
                    ("🎨", "品牌设计", "design_strategy"),
                    ("🎬", "流量脚本", "marketing_script"),
                    ("🔍", "SEO策略", "seo_strategy"),
                ]
                render_progress(agents_info)

            # Show results
            if st.session_state.results:
                render_results()
                render_export_section()
    else:
        # When idle, show two columns: input + features
        left_col, right_col = st.columns([3, 2])

        with left_col:
            idea, start_btn = render_input_section()

            # Handle start
            if start_btn and idea and not st.session_state.running:
                run_analysis(idea)

        with right_col:
            render_right_panel()


if __name__ == "__main__":
    main()
