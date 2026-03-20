"""Chief Designer Agent."""
from loguru import logger
from src.agents.base import BaseAgent


class ChiefDesigner(BaseAgent):
    """Chief designer agent."""
    
    @property
    def name(self) -> str:
        return "Chief Designer"
    
    def run(self, context: dict) -> dict:
        product = context.get("product_plan", "")
        industry = context.get("industry", "")
        logger.info(f"Designing brand for {industry}...")
        
        prompt = f"""
你是一名资深品牌设计师。基于以下产品定义:

{product}

请为这个【{industry}】品牌设计视觉概念。

请按以下格式返回:
品牌名称: [有记忆点的品牌名]
Logo设计理念: [简洁描述Logo样式]
品牌色调: [建议的主色调]
Midjourney提示词: [用于生成Logo的英文Prompt]
"""
        
        response = self._call_llm(prompt)
        context["design_strategy"] = response
        logger.info("Design complete")
        return context
