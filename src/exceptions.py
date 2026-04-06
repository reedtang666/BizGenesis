"""Shared exceptions for agents and utilities."""


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class LLMError(AgentError):
    """LLM call failed."""
    pass


class BudgetExceededError(Exception):
    """Raised when token budget is exceeded."""
    pass