from langchain.prompts import PromptTemplate
from src.agents.base import BaseAgent

# 这就是“核心”部分，生成赚钱的文案。
class ContentStrategist(BaseAgent):
    def run(self, context: dict) -> dict:
        product_plan = context.get("product_plan")
        print(f"🎬 [Marketing Agent] 正在撰写吸金短视频脚本...")

        prompt = PromptTemplate(
            input_variables=["product_plan"],
            template="""
            你是一名带货转化率极高的短视频编剧。
            基于以下产品方案：
            {product_plan}
            
            请编写一个【45秒抖音/TikTok带货脚本】。
            要求：
            - 0-3秒：必须有视觉或听觉钩子（Hook），让人停下来。
            - 中段：展示痛点并给出解决方案。
            - 结尾：强力号召下单（Call to Action）。
            - 风格：真实、亲切、甚至带点反转。
            """
        )
        
        response = self.llm.invoke(prompt.format(product_plan=product_plan))
        context["marketing_script"] = response.content
        return context