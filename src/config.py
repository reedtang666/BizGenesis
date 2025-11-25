import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    if not OPENAI_API_KEY:
        raise ValueError("❌ 未检测到 OPENAI_API_KEY，请在 .env 文件中配置。")