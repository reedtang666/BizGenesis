"""Token monitoring and budget management."""
from dataclasses import dataclass, field
from typing import Dict, Optional
from loguru import logger

from src.exceptions import BudgetExceededError


@dataclass
class TokenUsage:
    """Represents token usage for a single agent."""
    agent_name: str
    tokens: int
    cost: float


class TokenMonitor:
    """Monitor token usage across all agents with budget support."""

    def __init__(self, monthly_budget: Optional[int] = None):
        """
        Initialize TokenMonitor.

        Args:
            monthly_budget: Maximum tokens allowed per month (optional)
        """
        self.monthly_budget: Optional[int] = monthly_budget
        self._usage_by_agent: Dict[str, TokenUsage] = {}
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self._warning_threshold: float = 0.8  # 80% of budget

    def record_usage(self, agent_name: str, tokens: int, cost: float) -> None:
        """
        Record token usage for an agent.

        Args:
            agent_name: Name of the agent
            tokens: Number of tokens used
            cost: Cost in USD
        """
        # Update totals
        self.total_tokens += tokens
        self.total_cost += cost

        # Update per-agent usage
        if agent_name in self._usage_by_agent:
            existing = self._usage_by_agent[agent_name]
            self._usage_by_agent[agent_name] = TokenUsage(
                agent_name=agent_name,
                tokens=existing.tokens + tokens,
                cost=existing.cost + cost
            )
        else:
            self._usage_by_agent[agent_name] = TokenUsage(
                agent_name=agent_name,
                tokens=tokens,
                cost=cost
            )

        logger.debug(
            f"Recorded {tokens} tokens for {agent_name}: "
            f"total={self.total_tokens}, cost=${self.total_cost:.4f}"
        )

    def get_usage_by_agent(self) -> Dict[str, TokenUsage]:
        """Get token usage breakdown by agent."""
        return self._usage_by_agent.copy()

    def check_budget(self) -> bool:
        """
        Check if current usage is within budget.

        Returns:
            True if within budget

        Raises:
            BudgetExceededError: If budget is exceeded
        """
        if self.monthly_budget is None:
            return True

        usage_ratio = self.total_tokens / self.monthly_budget

        # Log warning at 80% threshold
        if usage_ratio >= self._warning_threshold:
            logger.warning(
                f"Budget warning: {self.total_tokens}/{self.monthly_budget} "
                f"({usage_ratio*100:.1f}%)"
            )

        # Raise error at 100%
        if self.total_tokens > self.monthly_budget:
            raise BudgetExceededError(
                f"Token budget exceeded: {self.total_tokens}/{self.monthly_budget}"
            )

        return True

    def get_remaining_budget(self) -> Optional[int]:
        """Get remaining budget, or None if no budget set."""
        if self.monthly_budget is None:
            return None
        return max(0, self.monthly_budget - self.total_tokens)

    def reset(self) -> None:
        """Reset all usage statistics."""
        self._usage_by_agent.clear()
        self.total_tokens = 0
        self.total_cost = 0.0

    def get_usage_summary(self) -> Dict:
        """Get a summary of token usage."""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "agent_count": len(self._usage_by_agent),
            "by_agent": {
                name: {
                    "tokens": usage.tokens,
                    "cost": usage.cost
                }
                for name, usage in self._usage_by_agent.items()
            },
            "budget": {
                "limit": self.monthly_budget,
                "remaining": self.get_remaining_budget(),
                "usage_ratio": (
                    self.total_tokens / self.monthly_budget
                    if self.monthly_budget else None
                )
            }
        }


# Global token monitor instance
_global_monitor: Optional[TokenMonitor] = None


def get_token_monitor() -> TokenMonitor:
    """Get the global token monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = TokenMonitor()
    return _global_monitor


def set_token_monitor(monitor: TokenMonitor) -> None:
    """Set the global token monitor instance."""
    global _global_monitor
    _global_monitor = monitor