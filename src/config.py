"""
配置加载模块
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """
    加载配置文件和环境变量
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    # 加载 .env 文件
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"警告: 未找到 .env 文件，将使用默认配置")
    
    # 构建配置字典
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
    
    # 验证必要的配置
    if not config["openai_api_key"] and not config["anthropic_api_key"]:
        print("警告: 未设置 API Key，某些功能可能无法使用")
    
    return config


def get_config_value(key: str, default: Any = None) -> Any:
    """
    获取单个配置值
    
    Args:
        key: 配置键名
        default: 默认值
        
    Returns:
        Any: 配置值
    """
    return os.getenv(key, default)
