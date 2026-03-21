"""Finance Planner Agent."""
from loguru import logger

from src.agents.base import BaseAgent


class FinancePlanner(BaseAgent):
    """Finance planning agent - focuses on startup budget and cash flow."""
    
    @property
    def name(self) -> str:
        return "Finance Planner"
    
    def run(self, context: dict) -> dict:
        product = context.get("product_plan", "")
        business = context.get("business_model", "")
        industry = context.get("industry", "")
        logger.info(f"Planning finance for {industry}...")
        
        prompt = f"""
你是一名资深财务顾问和创业财务专家。基于以下产品和商业模式:

【产品定义】
{product}

【商业模式】
{business}

请为这个【{industry}】创业项目制定详细的财务规划。

请按以下格式返回:
启动资金预算: [列出初期需要的各项投入，如设备/库存/租金/证照等]
月度固定成本: [房租/人工/水电/软件等月度支出预估]
首年现金流预测: [按季度预估收支情况]
资金来源建议: [适合的融资方式及建议]
成本控制要点: [哪些地方可以省钱]
关键财务指标: [需要关注的核心指标]
"""
        
        response = self._call_llm(prompt)
        context["finance_plan"] = response
        logger.info("Finance plan complete")
        return context