from langchain.prompts import PromptTemplate
from src.agents.base import BaseAgent

# 这个 Agent 不直接画图（因为需要调 DALL-E 接口，我们可以先让它生成顶级的绘图提示词），你可以拿着提示词去 Midjourney 或 DALL-E 生成。
class ChiefDesigner(BaseAgent):
    def run(self, context: dict) -> dict:
        product_plan = context.get("product_plan")
        print(f"🎨 [Designer Agent] 正在构思品牌视觉与 Logo...")

        prompt = PromptTemplate(
            input_variables=["product_plan"],
            template="""
            基于以下产品方案：
            {product_plan}
            
            你是一名获得红点设计奖的视觉总监。请完成以下任务：
            1. 为该品牌构思 3 个不同的 Logo 设计概念（极简风、复古风、赛博朋克风）。
            2. **编写一个精确的 Midjourney/DALL-E 提示词**，用于直接生成该 Logo。提示词应包含：主体描述、艺术风格、配色方案、渲染引擎参数（如 unreal engine 5, vector art, minimalist）。
            
            输出格式：
            ## Logo 概念
            ...
            ## Midjourney Prompt (直接复制使用)
            /imagine prompt: ...
            """
        )
        
        response = self.llm.invoke(prompt.format(product_plan=product_plan))
        context["design_strategy"] = response.content
        return context