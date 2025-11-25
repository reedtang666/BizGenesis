from langchain.prompts import PromptTemplate
from src.agents.base import BaseAgent

# 它的任务是把用户模糊的想法（如“袜子”）变成具体的商业机会。
class MarketResearcher(BaseAgent):
    def run(self, context: dict) -> dict:
        industry = context.get("industry")
        print(f"🕵️  [Market Agent] 正在扫描 {industry} 行业的细分蓝海...")

        prompt = PromptTemplate(
            input_variables=["industry"],
            template="""
            你是一名拥有10年经验的市场分析师。
            用户想在【{industry}】领域创业。
            请分析当前电商和社交媒体趋势，找出 1 个 最具潜力的细分利基市场（Niche）。
            
            请按以下格式返回（不要多余废话）：
            细分领域名称: [名称]
            目标受众: [人群]
            痛点分析: [一句话描述]
            """
        )
        
        response = self.llm.invoke(prompt.format(industry=industry))
        result = response.content
        
        # 简单解析返回结果 (在实际生产中可以使用 OutputParser)
        context["market_analysis"] = result
        return context