from langchain.prompts import PromptTemplate
from src.agents.base import BaseAgent

# 它的任务是定义产品卖点。
class ProductManager(BaseAgent):
    def run(self, context: dict) -> dict:
        market_data = context.get("market_analysis")
        print(f"📦 [Product Agent] 正在规划产品形态...")

        prompt = PromptTemplate(
            input_variables=["market_data"],
            template="""
            根据以下市场分析：
            {market_data}
            
            请定义一款爆款产品。请提供：
            1. 产品名称（要有吸引力）
            2. 核心卖点（USP，列出3点）
            3. 给设计师的包装设计提示词（用于生成图片）
            """
        )
        
        response = self.llm.invoke(prompt.format(market_data=market_data))
        context["product_plan"] = response.content
        return context