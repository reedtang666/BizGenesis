from langchain.prompts import PromptTemplate
from src.agents.base import BaseAgent

# SEO 专家 Agent
class SEOExpert(BaseAgent):
    def run(self, context: dict) -> dict:
        product_plan = context.get("product_plan")
        print(f"🔍 [SEO Agent] 正在挖掘高流量关键词...")

        prompt = PromptTemplate(
            input_variables=["product_plan"],
            template="""
            基于以下产品方案：
            {product_plan}
            
            你是一名 Google & TikTok SEO 专家。请提供：
            1. 5个高搜索量、低竞争的长尾关键词 (Long-tail Keywords)。
            2. 3个适合作为 Instagram/小红书 标签的 Hashtag。
            3. 一段适合作为网站 Meta Description 的简短描述（160字符以内），必须包含主关键词。
            
            请以清晰的列表格式输出。
            """
        )
        
        response = self.llm.invoke(prompt.format(product_plan=product_plan))
        context["seo_strategy"] = response.content
        return context