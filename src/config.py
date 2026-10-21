"""Configuration management."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # LLM Provider: openai, zhipu, qwen, deepseek, gemini
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Google Gemini (OpenAI-compatible endpoint)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
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
        provider = cls.LLM_PROVIDER.lower()
        if provider == "zhipu":
            return {
                "api_key": cls.ZHIPU_API_KEY,
                "model": cls.ZHIPU_MODEL,
                "base_url": "https://open.bigmodel.cn/api/paas/v4"
            }
        elif provider == "qwen":
            return {
                "api_key": cls.QWEN_API_KEY,
                "model": cls.QWEN_MODEL,
                "base_url": cls.QWEN_BASE_URL
            }
        elif provider == "deepseek":
            return {
                "api_key": cls.DEEPSEEK_API_KEY,
                "model": cls.DEEPSEEK_MODEL,
                "base_url": "https://api.deepseek.com/v1"
            }
        elif provider in ("gemini", "google"):
            return {
                "api_key": cls.GEMINI_API_KEY,
                "model": cls.GEMINI_MODEL,
                "base_url": cls.GEMINI_BASE_URL
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
            if provider == "GOOGLE":
                provider = "GEMINI"
            raise ValueError(f"❌ {provider}_API_KEY not found. Please set it in .env file.")
    
    @classmethod
    def has_search_api(cls) -> bool:
        """Check if search API is configured."""
        return bool(cls.SERPER_API_KEY)


Config.validate()
