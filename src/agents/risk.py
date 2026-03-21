"""Risk Analyst Agent."""
from loguru import logger

from src.agents.base import BaseAgent


class RiskAnalyst(BaseAgent):
    """Risk analysis agent - focuses on identifying and mitigating business risks."""
    
    @property
    def name(self) -> str:
        return "Risk Analyst"
    
    def run(self, context: dict) -> dict:
        product = context.get("product_plan", "")
        business = context.get("business_model", "")
        market = context.get("market_analysis", "")
        industry = context.get("industry", "")
        logger.info(f"Analyzing risks for {industry}...")
        
        prompt = f"""
你是一名资深商业风险分析师。基于以下市场、产品和商业模式:

【市场分析】
{market}

【产品定义】
{product}

【商业模式】
{business}

请为这个【{industry}】创业项目进行全面的风险评估。

请按以下格式返回:
市场风险: [市场规模不确定性、用户需求变化等风险]
竞争风险: [主要竞品威胁、护城河是否足够]
运营风险: [供应链、人员、流程可能出问题的地方]
财务风险: [现金流断裂风险、成本超支风险]
法律合规风险: [可能涉及的证照、法规、知识产权问题]
应对策略: [针对上述风险的预防和应对建议]
应急预案: [如果出问题，最坏情况下的退路]
"""
        
        response = self._call_llm(prompt)
        context["risk_analysis"] = response
        logger.info("Risk analysis complete")
        return context