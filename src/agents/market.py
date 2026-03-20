"""Market Researcher Agent with web search integration."""
from langchain.prompts import PromptTemplate
from loguru import logger

from src.agents.base import BaseAgent
from src.tools.search import get_search_tool, MarketSearchTool
from src.config import Config


class MarketResearcher(BaseAgent):
    """
    Market Researcher Agent.
    Analyzes market trends and identifies niche opportunities.
    """
    
    @property
    def name(self) -> str:
        return "Market Researcher"
    
    def run(self, context: dict) -> dict:
        """
        Execute market research.
        
        Args:
            context: Must contain 'industry' key
            
        Returns:
            context with 'market_analysis' key added
        """
        industry = context.get("industry", "")
        logger.info(f"🕵️ Analyzing {industry} market...")
        
        # Step 1: Search for real market data
        search_data = self._search_market(industry)
        
        # Step 2: Analyze with LLM
        prompt = self._build_prompt(industry, search_data)
        response = self._call_llm(prompt)
        
        context["market_analysis"] = response
        context["market_search_data"] = search_data  # Keep raw data for reference
        
        logger.info(f"✅ Market analysis complete")
        return context
    
    def _search_market(self, industry: str) -> dict:
        """Search for market trends and competitors."""
        try:
            search_tool = MarketSearchTool(
                search_tool=get_search_tool(Config.SERPER_API_KEY)
            )
            
            # Multiple search queries for comprehensive data
            trends = search_tool.run(industry, "trends")
            competitors = search_tool.run(industry, "competitors")
            pain_points = search_tool.run(industry, "pain_points")
            
            return {
                "trends": trends.get("results", [])[:3],
                "competitors": competitors.get("results", [])[:3],
                "pain_points": pain_points.get("results", [])[:3],
                "source": trends.get("source", "unknown")
            }
        except Exception as e:
            logger.warning(f"Search failed, using LLM knowledge only: {e}")
            return {"error": str(e), "results": []}
    
    def _build_prompt(self, industry: str, search_data: dict) -> str:
        """Build the analysis prompt with search data."""
        search_context = ""
        
        if search_data.get("trends"):
            trends_text = "\n".join([
                f"- {r.get('title', '')}: {r.get('snippet', '')[:100]}"
                for r in search_data["trends"][:2]
            ])
            search_context += f"\n\n市场趋势数据:\n{trends_text}"
        
        if search_data.get("competitors"):
            comp_text = "\n".join([
                f"- {r.get('title', '')}"
                for r in search_data["competitors"][:2]
            ])
            search_context += f"\n\n主要竞品:\n{comp_text}"
        
        prompt = PromptTemplate(
            input_variables=["industry", "search_context"],
            template="""
你是一名拥有10年经验的市场分析师。
用户想在【{industry}】领域创业。

参考搜索数据:
{search_context}

请分析并找出 1 个最具潜力的细分利基市场（Niche）。

请按以下格式返回:
细分领域名称: [名称]
目标受众: [具体人群画像]
痛点分析: [客户核心痛点]
市场机会: [为什么这是个好机会]
推荐指数: [1-10分]
"""
        )
        
        return prompt.format(industry=industry, search_context=search_context or "暂无实时数据")
