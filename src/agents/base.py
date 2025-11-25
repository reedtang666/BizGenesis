"""
智能体基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """
    智能体基类
    
    所有具体的智能体都应该继承此类并实现抽象方法
    """
    
    def __init__(self, config: Dict[str, Any], name: str = "BaseAgent"):
        """
        初始化智能体
        
        Args:
            config: 配置字典
            name: 智能体名称
        """
        self.config = config
        self.name = name
        self.history = []
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        处理输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            Any: 处理结果
        """
        pass
    
    def add_to_history(self, item: Dict[str, Any]):
        """
        添加记录到历史
        
        Args:
            item: 历史记录项
        """
        self.history.append(item)
    
    def get_history(self) -> list:
        """
        获取历史记录
        
        Returns:
            list: 历史记录列表
        """
        return self.history
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
