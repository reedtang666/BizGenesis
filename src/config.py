"""Configuration management."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # LLM Provider: openai, zhipu, qwen, deepseek
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # 智谱AI (GLM)
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
    ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    
    # 千问百炼 (通义千问)
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")
    QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    # DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Search API
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration based on provider."""
        if cls.LLM_PROVIDER == "zhipu":
            return {
                "api_key": cls.ZHIPU_API_KEY,
                "model": cls.ZHIPU_MODEL,
                "base_url": "https://open.bigmodel.cn/api/paas/v4"
            }
        elif cls.LLM_PROVIDER == "qwen":
            return {
                "api_key": cls.QWEN_API_KEY,
                "model": cls.QWEN_MODEL,
                "base_url": cls.QWEN_BASE_URL
            }
        elif cls.LLM_PROVIDER == "deepseek":
            return {
                "api_key": cls.DEEPSEEK_API_KEY,
                "model": cls.DEEPSEEK_MODEL,
                "base_url": "https://api.deepseek.com/v1"
            }
        else:  # openai
            return {
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "base_url": cls.OPENAI_BASE_URL
            }
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        config = cls.get_llm_config()
        if not config["api_key"]:
            provider = cls.LLM_PROVIDER.upper()
            if provider == "QWEN":
                provider = "QWEN"
            raise ValueError(f"❌ {provider}_API_KEY not found. Please set it in .env file.")
    
    @classmethod
    def has_search_api(cls) -> bool:
        """Check if search API is configured."""
        return bool(cls.SERPER_API_KEY)


Config.validate()
