"""Calculator tool for basic computations."""
from typing import Dict, Any
from .base import BaseTool


class CalculatorTool(BaseTool):
    """Calculator tool for basic math operations."""
    
    name = "calculator"
    description = "Perform basic mathematical calculations"
    
    def run(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        Safe evaluation with limited operations.
        """
        try:
            # Safe evaluation - only allow basic math
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Invalid characters in expression"}
            
            result = eval(expression)
            return {
                "expression": expression,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "status": "error"
            }
