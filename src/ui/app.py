"""
Streamlit Web UI for BizGenesis.
Run with: streamlit run src/ui/app.py
"""
import streamlit as st
import sys
from pathlib import Path
# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from typing import Dict, Any

from src.agents.market import MarketResearcher
from src.agents.product import ProductManager
from src.agents.marketing import ContentStrategist
from src.agents.seo import SEOExpert
from src.agents.designer import ChiefDesigner
from src.agents.business import BusinessModeler
from src.agents.finance import FinancePlanner
from src.agents.risk import RiskAnalyst
from src.config import Config


def init_session_state():
    """Initialize session state variables."""
    if "context" not in st.session_state:
        st.session_state.context = {}
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "results" not in st.session_state:
        st.session_state.results = {}


def main():
    st.set_page_config(
        page_title="BizGenesis - AI 创业辅助系统",
        page_icon="🚀",
        layout="wide"
    )
    
    init_session_state()
    
    # Header
    st.title("🚀 BizGenesis - AI 创业辅助系统")
    st.markdown("**从想法到方案，让 AI 团队帮你完成商业策划**")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ 设置")
        llm_config = Config.get_llm_config()
        st.markdown(f"**模型**: {llm_config['model']}")
        
        if Config.has_search_api():
            st.success("✅ 搜索 API 已配置")
        else:
            st.info("ℹ️ 使用 DuckDuckGo 搜索")
        
        st.divider()
        st.markdown("### 使用说明")
        st.markdown("""
        1. 输入你的创业想法
        2. 点击「开始分析」
        3. 等待 AI 团队协同工作
        4. 获取完整商业方案
        """)
    
    # Main input
    st.header("💡 你的创业想法")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        idea = st.text_input(
            "输入你想尝试的创业领域或关键词",
            placeholder="例如：袜子、露营、猫粮、咖啡...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")
        st.write("")
        start_btn = st.button("🎯 开始分析", type="primary", use_container_width=True)
    
    # Process
    if start_btn and idea:
        st.session_state.context = {"industry": idea}
        st.session_state.results = {}
        st.session_state.current_step = 0
        
        # Initialize agents
        agents = [
            ("🕵️ 市场研究", MarketResearcher(), "market_analysis"),
            ("📦 产品定义", ProductManager(), "product_plan"),
            ("💰 商业模式", BusinessModeler(), "business_model"),
            ("📈 财务规划", FinancePlanner(), "finance_plan"),
            ("⚠️ 风险评估", RiskAnalyst(), "risk_analysis"),
            ("🎨 品牌设计", ChiefDesigner(), "design_strategy"),
            ("🎬 流量脚本", ContentStrategist(), "marketing_script"),
            ("🔍 SEO 策略", SEOExpert(), "seo_strategy"),
        ]
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run agents
        for i, (name, agent, key) in enumerate(agents):
            status_text.text(f"{name} 正在工作中...")
            st.session_state.context = agent.run(st.session_state.context)
            st.session_state.results[name] = st.session_state.context.get(key, "")
            progress_bar.progress((i + 1) / len(agents))
        
        status_text.text("✅ 所有 Agent 工作完成！")
        st.rerun()
    
    # Display results
    if st.session_state.results:
        st.divider()
        st.header("📊 分析结果")
        
        tabs = st.tabs([
            "🕵️ 市场研究",
            "📦 产品定义",
            "💰 商业模式",
            "📈 财务规划",
            "⚠️ 风险评估",
            "🎨 品牌设计",
            "🎬 流量脚本",
            "🔍 SEO 策略"
        ])
        
        tab_keys = [
            "market_analysis",
            "product_plan",
            "business_model",
            "finance_plan",
            "risk_analysis",
            "design_strategy",
            "marketing_script",
            "seo_strategy"
        ]
        
        for tab, key in zip(tabs, tab_keys):
            with tab:
                content = st.session_state.context.get(key, "")
                if content:
                    st.markdown(content)
                else:
                    st.info("暂无数据")
        
        # Export button
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("📋 复制完整方案", use_container_width=True):
                full_report = "\n\n---\n\n".join([
                    f"## {name}\n\n{content}"
                    for name, content in st.session_state.results.items()
                ])
                st.code(full_report, language="markdown")
                st.success("✅ 方案已生成，请复制上方内容")


if __name__ == "__main__":
    main()
