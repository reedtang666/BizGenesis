"""SEO Expert Agent."""
from loguru import logger
from src.agents.base import BaseAgent


class SEOExpert(BaseAgent):
    """SEO expert agent."""
    
    @property
    def name(self) -> str:
        return "SEO Expert"
    
    def run(self, context: dict) -> dict:
        marketing = context.get("marketing_script", "")
        industry = context.get("industry", "")
        logger.info(f"Optimizing SEO for {industry}...")
        
        prompt = f"""
你是一名资深SEO专家。基于以下营销内容:

{marketing}

请为这个【{industry}】项目提供SEO优化建议。

请按以下格式返回:
长尾关键词: [列出5个高转化长尾词]
热门Hashtag: [列出5个适合的标签]
内容优化建议: [提升搜索排名的建议]
"
"""
        
        response = self._call_llm(prompt)
        context["seo_strategy"] = response
        logger.info("SEO strategy complete")
        return context
