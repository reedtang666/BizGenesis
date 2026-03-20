"""Market Researcher Agent."""
from loguru import logger

from src.agents.base import BaseAgent


class MarketResearcher(BaseAgent):
    """Market research agent."""
    
    @property
    def name(self) -> str:
        return "Market Researcher"
    
    def run(self, context: dict) -> dict:
        industry = context.get("industry", "")
        logger.info(f"Analyzing {industry} market...")
        
        prompt = f"""
你是一名资深市场分析师。用户想在【{industry}】领域创业。

请分析并找出 1 个最具潜力的细分利基市场（Niche）。

请按以下格式返回:
细分领域名称: [名称]
目标受众: [具体人群画像]
痛点分析: [客户核心痛点]
市场机会: [为什么这是个好机会]
推荐指数: [1-10分]
"""
        
        response = self._call_llm(prompt)
        context["market_analysis"] = response
        logger.info("Market analysis complete")
        return context
