"""Tests for token monitoring functionality."""
import pytest
from unittest.mock import Mock, patch
from src.utils.token_monitor import TokenMonitor, TokenUsage, BudgetExceededError


class TestTokenMonitor:
    """Test cases for TokenMonitor."""

    @pytest.fixture
    def monitor(self):
        """Create a TokenMonitor instance."""
        return TokenMonitor()

    @pytest.fixture
    def monitor_with_budget(self):
        """Create a TokenMonitor with budget."""
        return TokenMonitor(monthly_budget=100000)

    def test_monitor_initialization(self, monitor):
        """Test TokenMonitor initializes with zero usage."""
        assert monitor.total_tokens == 0
        assert monitor.total_cost == 0.0
        assert monitor.get_usage_by_agent() == {}

    def test_monitor_with_budget_initialization(self, monitor_with_budget):
        """Test TokenMonitor with budget initializes correctly."""
        assert monitor_with_budget.monthly_budget == 100000
        assert monitor_with_budget.total_tokens == 0

    def test_record_usage(self, monitor):
        """Test recording token usage for an agent."""
        monitor.record_usage("MarketResearcher", 1000, 0.002)

        assert monitor.total_tokens == 1000
        assert monitor.total_cost == 0.002

        usage = monitor.get_usage_by_agent()
        assert "MarketResearcher" in usage
        assert usage["MarketResearcher"].tokens == 1000
        assert usage["MarketResearcher"].cost == 0.002

    def test_record_usage_accumulates(self, monitor):
        """Test that multiple recordings accumulate."""
        monitor.record_usage("MarketResearcher", 1000, 0.002)
        monitor.record_usage("MarketResearcher", 500, 0.001)
        monitor.record_usage("ProductManager", 2000, 0.004)

        usage = monitor.get_usage_by_agent()
        assert usage["MarketResearcher"].tokens == 1500
        assert usage["MarketResearcher"].cost == 0.003
        assert usage["ProductManager"].tokens == 2000
        assert monitor.total_tokens == 3500
        assert monitor.total_cost == 0.007

    def test_check_budget_within_limit(self, monitor_with_budget):
        """Test budget check passes when under limit."""
        monitor_with_budget.record_usage("Agent1", 50000, 0.1)
        # Should not raise
        result = monitor_with_budget.check_budget()
        assert result is True

    def test_check_budget_exceeds_limit(self, monitor_with_budget):
        """Test budget check raises when exceeded."""
        monitor_with_budget.record_usage("Agent1", 100001, 0.2)

        with pytest.raises(BudgetExceededError) as exc_info:
            monitor_with_budget.check_budget()

        assert "100001/100000" in str(exc_info.value)

    def test_get_remaining_budget(self, monitor_with_budget):
        """Test getting remaining budget."""
        monitor_with_budget.record_usage("Agent1", 30000, 0.06)

        remaining = monitor_with_budget.get_remaining_budget()
        assert remaining == 70000

    def test_reset_usage(self, monitor):
        """Test resetting usage."""
        monitor.record_usage("Agent1", 1000, 0.002)
        monitor.reset()

        assert monitor.total_tokens == 0
        assert monitor.total_cost == 0.0
        assert monitor.get_usage_by_agent() == {}

    def test_get_usage_summary(self, monitor):
        """Test getting usage summary."""
        monitor.record_usage("MarketResearcher", 1000, 0.002)
        monitor.record_usage("ProductManager", 2000, 0.004)

        summary = monitor.get_usage_summary()

        assert summary["total_tokens"] == 3000
        assert summary["total_cost"] == 0.006
        assert summary["agent_count"] == 2
        assert "MarketResearcher" in summary["by_agent"]

    def test_budget_warning_threshold(self, monitor_with_budget):
        """Test budget warning is triggered at 80%."""
        # At 80% (80000/100000), should trigger warning but not raise
        monitor_with_budget.record_usage("Agent1", 80000, 0.16)

        # Capture logs to verify warning
        import io
        from loguru import logger

        output = io.StringIO()
        logger.remove()
        logger.add(output, format="{message}")

        result = monitor_with_budget.check_budget()

        # Should return True (not exceeded)
        assert result is True
        # Check warning was logged
        assert "80%" in output.getvalue() or "Budget warning" in output.getvalue()


class TestTokenUsage:
    """Test cases for TokenUsage dataclass."""

    def test_token_usage_creation(self):
        """Test creating a TokenUsage instance."""
        usage = TokenUsage(agent_name="TestAgent", tokens=1000, cost=0.002)

        assert usage.agent_name == "TestAgent"
        assert usage.tokens == 1000
        assert usage.cost == 0.002