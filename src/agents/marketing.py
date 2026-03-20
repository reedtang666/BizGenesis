"""Content Strategist Agent."""
from loguru import logger
from src.agents.base import BaseAgent


class ContentStrategist(BaseAgent):
    """Content strategist agent."""
    
    @property
    def name(self) -> str:
        return "Content Strategist"
    
    def run(self, context: dict) -> dict:
        design = context.get("design_strategy", "")
        industry = context.get("industry", "")
        logger.info(f"Creating content for {industry}...")
        
        prompt = f"""
你是一名资深短视频内容策划师。基于以下品牌设计:

{design}

请为这个【{industry}】项目创作一个TikTok/抖音爆款带货脚本。

请按以下格式返回:
开头3秒钩子: [抓住观众注意力的开场白]
脚本内容: [完整的30秒脚本]
结尾CTA: [引导用户行动的话术]
推荐BGM: [适合的背景音乐风格]
"""
        
        response = self._call_llm(prompt)
        context["marketing_script"] = response
        logger.info("Marketing script complete")
        return context
