"""Test configuration and fixtures."""
import pytest
from unittest.mock import MagicMock, patch

from src.utils.token_monitor import TokenMonitor
from src.utils.error_degradation import ErrorDegrader, DefaultValueProvider, AgentFallbackManager
from src.utils.competitor_data import CompetitorDataCollector


@pytest.fixture
def mock_llm():
    """Create a mock LLM."""
    mock = MagicMock()
    response = MagicMock()
    response.content = "Test response"
    response.usage_metadata = {"total_tokens": 100}
    mock.invoke.return_value = response
    return mock


@pytest.fixture
def token_monitor():
    """Create a fresh token monitor."""
    return TokenMonitor()


@pytest.fixture
def token_monitor_with_budget():
    """Create a token monitor with budget."""
    return TokenMonitor(monthly_budget=100000)


@pytest.fixture
def error_degrader():
    """Create an error degrader."""
    return ErrorDegrader(max_retries=3, fallback_on_failure=True)


@pytest.fixture
def default_provider():
    """Create a default value provider."""
    return DefaultValueProvider()


@pytest.fixture
def fallback_manager():
    """Create a fallback manager."""
    return AgentFallbackManager()


@pytest.fixture
def mock_competitor_collector():
    """Create a mock competitor collector."""
    collector = MagicMock(spec=CompetitorDataCollector)
    collector.collect.return_value = []
    collector.get_industry_trends.return_value = []
    collector.get_market_keywords.return_value = []
    return collector


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    import src.utils.token_monitor as tm
    import src.utils.error_degradation as ed

    # Reset global instances
    tm._global_monitor = None
    ed._degrader = None
    ed._default_provider = None
    ed._fallback_manager = None

    yield