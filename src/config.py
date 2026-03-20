"""Configuration management."""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Search API (optional)
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY not found. Please set it in .env file.")
    
    @classmethod
    def has_search_api(cls) -> bool:
        """Check if search API is configured."""
        return bool(cls.SERPER_API_KEY)


# Validate on import
Config.validate()
