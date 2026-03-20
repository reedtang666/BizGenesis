"""Base tool class."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base class for all tools."""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        pass
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
