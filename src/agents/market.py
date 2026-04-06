"""Market Researcher Agent with competitor data integration."""
from loguru import logger

from src.agents.base import BaseAgent
from src.utils.competitor_data import CompetitorDataCollector, get_competitor_collector, integrate_competitor_data


class MarketResearcher(BaseAgent):
    """Market research agent with real competitor data support."""

    def __init__(self, enable_competitor_data: bool = True, **kwargs):
        """
        Initialize MarketResearcher.

        Args:
            enable_competitor_data: Whether to collect real competitor data
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            enable_competitor_data=enable_competitor_data,
            **kwargs
        )
        self._enable_competitor_data = enable_competitor_data

    @property
    def name(self) -> str:
        return "Market Researcher"

    def run(self, context: dict) -> dict:
        industry = context.get("industry", "")
        logger.info(f"Analyzing {industry} market...")

        # Collect competitor data if enabled
        if self._enable_competitor_data:
            logger.info(f"Collecting competitor data for {industry}")
            try:
                competitor_context = self._collect_competitor_data(industry)
                context.update(competitor_context)
            except Exception as e:
                logger.warning(f"Failed to collect competitor data: {e}")
                context["competitor_data_available"] = False
        else:
            context["competitor_data_available"] = False

        # Build research prompt with competitor context
        prompt = self._build_research_prompt(industry, context)

        response = self._call_llm(prompt)
        context["market_analysis"] = response
        logger.info("Market analysis complete")
        return context

    def _build_research_prompt(self, industry: str, context: dict) -> str:
        """Build research prompt with optional competitor data."""
        prompt_parts = [
            f"你是一名资深市场分析师。用户想在【{industry}】领域创业。"
        ]

        # Include competitor data if available
        if context.get("competitor_data_available", False) and "competitor_analysis" in context:
            prompt_parts.append("\n\n## 竞品分析数据")
            prompt_parts.append(context.get("competitor_analysis", ""))

        prompt_parts.append("\n\n请分析并找出 1 个最具潜力的细分利基市场（Niche）。")

        prompt_parts.append("""
请按以下格式返回:
细分领域名称: [名称]
目标受众: [具体人群画像]
痛点分析: [客户核心痛点]
市场机会: [为什么这是个好机会]
推荐指数: [1-10分]
""")

        return "\n".join(prompt_parts)