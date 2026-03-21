"""Business Modeler Agent."""
from loguru import logger

from src.agents.base import BaseAgent


class BusinessModeler(BaseAgent):
    """Business model design agent - focuses on monetization strategy."""
    
    @property
    def name(self) -> str:
        return "Business Modeler"
    
    def run(self, context: dict) -> dict:
        product = context.get("product_plan", "")
        market = context.get("market_analysis", "")
        industry = context.get("industry", "")
        logger.info(f"Designing business model for {industry}...")
        
        prompt = f"""
你是一名资深商业顾问和创业导师。基于以下市场分析和产品定义:

【市场分析】
{market}

【产品定义】
{product}

请为这个【{industry}】创业项目设计一个可持续的商业模式。

请按以下格式返回:
收入来源: [列出主要收入来源，如：一次性销售/订阅/佣金/广告/增值服务等]
定价策略: [建议具体定价及理由]
成本结构: [主要固定成本和变动成本]
盈亏平衡点: [预估需要多少客户/销量才能收支平衡]
变现路径: [从0到1的具体变现步骤，分阶段说明]
风险提示: [可能的商业风险及应对建议]
"""
        
        response = self._call_llm(prompt)
        context["business_model"] = response
        logger.info("Business model complete")
        return context