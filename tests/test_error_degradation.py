"""Tests for error degradation functionality."""
import pytest
from unittest.mock import Mock, patch
from src.agents.base import BaseAgent, AgentError, LLMError
from src.utils.error_degradation import (
    ErrorDegrader,
    DefaultValueProvider,
    get_degradation_strategy,
    AgentFallbackManager
)


class TestErrorDegrader:
    """Test cases for ErrorDegrader."""

    @pytest.fixture
    def degrader(self):
        """Create an ErrorDegrader instance."""
        return ErrorDegrader()

    def test_degrader_initialization(self, degrader):
        """Test ErrorDegrader initializes correctly."""
        assert degrader.max_retries == 3
        assert degrader.fallback_on_failure is True

    def test_degrader_with_custom_config(self):
        """Test ErrorDegrader with custom configuration."""
        degrader = ErrorDegrader(max_retries=5, fallback_on_failure=False)
        assert degrader.max_retries == 5
        assert degrader.fallback_on_failure is False

    def test_execute_with_success(self, degrader):
        """Test successful execution returns result."""
        def success_func():
            return {"status": "success", "data": "test"}

        result = degrader.execute(success_func)

        assert result == {"status": "success", "data": "test"}

    def test_execute_with_retry_then_success(self, degrader):
        """Test retry succeeds after initial failure."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise LLMError("Temporary failure")
            return {"status": "success"}

        with patch('src.utils.error_degradation.logger') as mock_logger:
            result = degrader.execute(flaky_func)

            assert result == {"status": "success"}
            assert call_count == 3
            assert mock_logger.warning.call_count == 2  # 2 retries before success

    def test_execute_fallback_on_exhausted_retries(self, degrader):
        """Test fallback is used when retries exhausted."""
        def always_fail():
            raise LLMError("Persistent failure")

        fallback_value = {"status": "fallback", "message": "Using default"}

        with patch('src.utils.error_degradation.logger') as mock_logger:
            result = degrader.execute(always_fail, fallback_value=fallback_value)

            assert result == fallback_value
            assert mock_logger.error.call_count >= 1

    def test_execute_raises_on_no_fallback(self, degrader):
        """Test exception raised when no fallback available."""
        def always_fail():
            raise AgentError("Critical failure")

        with pytest.raises(AgentError):
            degrader.execute(always_fail, fallback_on_failure=False)

    def test_execute_with_timeout(self, degrader):
        """Test execution respects timeout."""
        import time

        def slow_func():
            time.sleep(0.2)
            return {"status": "done"}

        # With timeout, should timeout
        with pytest.raises(Exception):  # TimeoutError or similar
            degrader.execute(slow_func, timeout=0.1)


class TestDefaultValueProvider:
    """Test cases for DefaultValueProvider."""

    def test_get_default_for_market_researcher(self):
        """Test getting default value for MarketResearcher."""
        provider = DefaultValueProvider()
        default = provider.get_default("MarketResearcher")

        assert default is not None
        assert "industry" in default
        assert "market_analysis" in default

    def test_get_default_for_product_manager(self):
        """Test getting default value for ProductManager."""
        provider = DefaultValueProvider()
        default = provider.get_default("ProductManager")

        assert default is not None
        assert "product_plan" in default

    def test_get_default_for_unknown_agent(self):
        """Test getting default for unknown agent returns generic fallback."""
        provider = DefaultValueProvider()
        default = provider.get_default("UnknownAgent")

        assert default is not None
        assert "error" in default or "fallback" in default

    def test_has_default_for_agent(self):
        """Test checking if default exists for agent."""
        provider = DefaultValueProvider()

        assert provider.has_default("MarketResearcher") is True
        assert provider.has_default("ProductManager") is True
        assert provider.has_default("UnknownAgent") is False


class TestAgentFallbackManager:
    """Test cases for AgentFallbackManager."""

    @pytest.fixture
    def manager(self):
        """Create an AgentFallbackManager instance."""
        return AgentFallbackManager()

    def test_manager_initialization(self, manager):
        """Test manager initializes with empty state."""
        assert len(manager.failed_agents) == 0
        assert len(manager.fallback_count) == 0

    def test_record_failure(self, manager):
        """Test recording agent failure."""
        manager.record_failure("MarketResearcher")

        assert "MarketResearcher" in manager.failed_agents
        assert manager.fallback_count["MarketResearcher"] == 1

    def test_record_multiple_failures(self, manager):
        """Test multiple failures increment counter."""
        manager.record_failure("MarketResearcher")
        manager.record_failure("MarketResearcher")
        manager.record_failure("ProductManager")

        assert manager.fallback_count["MarketResearcher"] == 2
        assert manager.fallback_count["ProductManager"] == 1

    def test_get_fallback_rate(self, manager):
        """Test calculating fallback rate."""
        manager.record_failure("Agent1")
        manager.record_failure("Agent2")
        manager.record_success("Agent3")

        rate = manager.get_fallback_rate()
        assert 0 <= rate <= 1

    def test_reset_stats(self, manager):
        """Test resetting statistics."""
        manager.record_failure("Agent1")
        manager.reset()

        assert len(manager.failed_agents) == 0
        assert len(manager.fallback_count) == 0

    def test_get_failure_report(self, manager):
        """Test getting failure report."""
        manager.record_failure("MarketResearcher")
        manager.record_failure("MarketResearcher")
        manager.record_failure("ProductManager")

        report = manager.get_failure_report()

        assert "MarketResearcher" in report
        assert report["MarketResearcher"] == 2
        assert "total_fallbacks" in report


class TestDegradationStrategy:
    """Test cases for degradation strategy configuration."""

    def test_get_degradation_strategy_default(self):
        """Test default degradation strategy."""
        strategy = get_degradation_strategy()

        assert strategy is not None
        assert strategy.max_retries == 3

    def test_get_degradation_strategy_custom(self):
        """Test custom degradation strategy."""
        strategy = get_degradation_strategy(
            max_retries=5,
            fallback_on_failure=True
        )

        assert strategy.max_retries == 5
        assert strategy.fallback_on_failure is True