"""Product Manager Agent."""
from loguru import logger
from src.agents.base import BaseAgent


class ProductManager(BaseAgent):
    """Product manager agent."""
    
    @property
    def name(self) -> str:
        return "Product Manager"
    
    def run(self, context: dict) -> dict:
        market = context.get("market_analysis", "")
        industry = context.get("industry", "")
        logger.info(f"Defining product for {industry}...")
        
        prompt = f"""
你是一名资深产品经理。基于以下市场分析:

{market}

请为这个【{industry}】创业项目定义一个差异化的产品概念。

请按以下格式返回:
产品名称: [有创意的名字]
核心卖点: [USP - 独特卖点]
差异化优势: [与竞品不同的地方]
目标用户: [具体用户画像]
定价策略: [建议定价]
"""
        
        response = self._call_llm(prompt)
        context["product_plan"] = response
        logger.info("Product plan complete")
        return context
