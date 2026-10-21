"""Calculator tool for basic computations."""
import ast
import operator
from typing import Dict, Any
from .base import BaseTool

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval_ast(node: ast.AST) -> float | int:
    """Safely evaluate an AST math node without using eval()."""
    if isinstance(node, ast.Expression):
        return _safe_eval_ast(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left = _safe_eval_ast(node.left)
        right = _safe_eval_ast(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_safe_eval_ast(node.operand))
    raise ValueError("Unsupported mathematical expression")


class CalculatorTool(BaseTool):
    """Calculator tool for basic math operations."""
    
    name = "calculator"
    description = "Perform basic mathematical calculations"
    
    def run(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        Safe AST evaluation with limited operations.
        """
        try:
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Invalid characters in expression"}
            
            parsed = ast.parse(expression.strip(), mode="eval")
            result = _safe_eval_ast(parsed)
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
