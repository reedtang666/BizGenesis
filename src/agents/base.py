from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from src.config import Config

# 这是一个抽象类，规定了所有未来的 Agent 必须长什么样，方便开源协作。
class BaseAgent(ABC):
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name=Config.MODEL_NAME,
            openai_api_key=Config.OPENAI_API_KEY
        )

    @abstractmethod
    def run(self, context: dict) -> dict:
        """
        接收上下文信息，执行任务，返回更新后的上下文
        """
        pass