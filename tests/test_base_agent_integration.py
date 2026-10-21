"""Tests for BaseAgent integration with error degradation and token monitoring."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.base import BaseAgent, AgentError, LLMError
from src.utils.token_monitor import TokenMonitor
from src.utils.error_degradation import ErrorDegrader, DefaultValueProvider, AgentFallbackManager
from src.utils.competitor_data import CompetitorDataCollector, integrate_competitor_data


class TestBaseAgentIntegration:
    """Test cases for BaseAgent with integrated features."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        mock = MagicMock()
        mock.invoke.return_value = MagicMock(content="Test response")
        return mock

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_initialization(self, mock_chat):
        """Test agent initializes with token monitoring."""
        mock_chat.return_value = MagicMock()

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                return context

        agent = TestAgent()

        assert agent.name == "TestAgent"
        assert hasattr(agent, '_token_monitor')
        assert hasattr(agent, '_degrader')
        assert hasattr(agent, '_fallback_manager')

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_with_custom_token_monitor(self, mock_chat):
        """Test agent with custom token monitor."""
        mock_chat.return_value = MagicMock()

        custom_monitor = TokenMonitor(monthly_budget=50000)

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                return context

        agent = TestAgent(token_monitor=custom_monitor)

        assert agent._token_monitor.monthly_budget == 50000

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_run_with_error_degradation(self, mock_chat):
        """Test agent handles errors with degradation."""
        mock_chat.return_value = MagicMock()

        # Create degrader that will fail and use fallback
        degrader = ErrorDegrader(max_retries=1, fallback_on_failure=True)

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                # Simulate failure
                raise LLMError("Simulated failure")

        agent = TestAgent()
        agent._degrader = degrader
        agent._default_provider = DefaultValueProvider()

        # Should not raise, should use fallback
        result = agent.run_with_degradation({})

        # Result should contain fallback data
        assert result is not None
        assert "fallback" in result or "TestAgent" in str(result)

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_run_without_error(self, mock_chat):
        """Test agent runs normally without errors."""
        mock_chat.return_value = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Success"
        mock_chat.return_value.invoke = Mock(return_value=mock_response)

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                context["result"] = "Success"
                return context

        agent = TestAgent()
        result = agent.run({})

        assert result["result"] == "Success"

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_token_tracking(self, mock_chat):
        """Test agent tracks token usage."""
        mock_chat.return_value = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.usage_metadata = {"total_tokens": 100}
        mock_chat.return_value.invoke = Mock(return_value=mock_response)

        monitor = TokenMonitor()

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                # Simulate token usage
                self._token_monitor.record_usage(self.name, 100, 0.001)
                return context

        agent = TestAgent(token_monitor=monitor)
        agent.run({})

        assert monitor.total_tokens == 100


class TestMarketResearcherIntegration:
    """Test cases for MarketResearcher with competitor data."""

    @patch('src.agents.base.ChatOpenAI')
    @patch('src.utils.competitor_data.CompetitorDataCollector')
    def test_market_researcher_with_competitor_data(self, mock_collector_class, mock_chat):
        """Test MarketResearcher integrates competitor data."""
        mock_chat.return_value = MagicMock()

        # Mock competitor collector
        mock_collector = MagicMock()
        mock_collector.collect.return_value = [
            MagicMock(
                name="Competitor A",
                website="https://a.com",
                description="Leader in market",
                strengths=["Strong brand"],
                weaknesses=["High price"],
                market_position="Leader"
            )
        ]
        mock_collector_class.return_value = mock_collector

        from src.agents.market import MarketResearcher
        researcher = MarketResearcher()

        context = {"industry": "SaaS"}
        result = researcher.run(context)

        # Should have competitor data integrated
        assert "competitor_analysis" in result or result.get("market_analysis") is not None


class TestAgentConfig:
    """Test agent configuration options."""

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_config_enables_competitor_data(self, mock_chat):
        """Test agent config can enable competitor data collection."""
        mock_chat.return_value = MagicMock()

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                return context

        agent = TestAgent(enable_competitor_data=True)

        assert agent._enable_competitor_data is True

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_config_enables_token_tracking(self, mock_chat):
        """Test agent config can enable token tracking."""
        mock_chat.return_value = MagicMock()

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                return context

        agent = TestAgent(enable_token_tracking=True)

        assert agent._enable_token_tracking is True

    def test_gemini_provider_config(self, monkeypatch):
        """Test Config supports Google Gemini provider."""
        from src.config import Config

        monkeypatch.setattr(Config, "LLM_PROVIDER", "gemini")
        monkeypatch.setattr(Config, "GEMINI_API_KEY", "test-gemini-key")
        monkeypatch.setattr(Config, "GEMINI_MODEL", "gemini-3.8-flash")

        llm_cfg = Config.get_llm_config()
        assert llm_cfg["api_key"] == "test-gemini-key"
        assert llm_cfg["model"] == "gemini-3.8-flash"
        assert "generativelanguage.googleapis.com" in llm_cfg["base_url"]
        Config.validate()

    @patch('src.agents.base.ChatOpenAI')
    def test_agent_startup_constraints_and_refine(self, mock_chat):
        """Test startup constraint formatting and single-section refine."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Refined section output")
        mock_chat.return_value = mock_instance

        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"

            def run(self, context):
                context["test_key"] = "Initial output"
                return context

        agent = TestAgent(use_memory=True)
        ctx = {
            "industry": "猫粮",
            "budget_scale": "< 5万元（个人/副业轻资产）",
            "target_market": "国内市场（抖音/小红书/天猫/微信私域）",
            "team_type": "一人公司 / 独立创客",
            "extra_requirements": "主打冻干生骨肉",
            "test_key": "Initial output",
        }
        constraint_str = BaseAgent.format_startup_constraints(ctx)
        assert "启动资金规模" in constraint_str
        assert "主打冻干生骨肉" in constraint_str

        updated_ctx = agent.refine(ctx, "请把客单价调整到99元以内", "test_key")
        assert updated_ctx["test_key"] == "Refined section output"
        assert len(agent._conversation_history) >= 2

    def test_parse_markdown_report(self):
        """Test parsing historical markdown report into context."""
        from src.ui.app import parse_markdown_report

        sample_md = """# 🚀 创业方案: 智能猫砂盆

生成时间: 2026-10-21 10:00:00

---

## 📊 市场定位

细分领域名称: 静音杀菌猫砂盆

---

## 📦 产品定义

产品名称: 净喵Pro
"""
        parsed = parse_markdown_report(sample_md)
        assert parsed["industry"] == "智能猫砂盆"
        assert "静音杀菌猫砂盆" in parsed["market_analysis"]
        assert "净喵Pro" in parsed["product_plan"]

