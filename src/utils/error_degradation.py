"""Error degradation and fallback handling for agents."""
import time
from typing import Any, Callable, Dict, Optional
from loguru import logger

from src.exceptions import AgentError, LLMError


class ErrorDegrader:
    """Handle agent errors with graceful degradation."""

    def __init__(
        self,
        max_retries: int = 3,
        fallback_on_failure: bool = True,
        retry_delay: float = 1.0
    ):
        """
        Initialize ErrorDegrader.

        Args:
            max_retries: Maximum number of retry attempts
            fallback_on_failure: Whether to use fallback on exhaustion
            retry_delay: Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.fallback_on_failure = fallback_on_failure
        self.retry_delay = retry_delay

    def execute(
        self,
        func: Callable,
        fallback_value: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        fallback_on_failure: Optional[bool] = None
    ) -> Any:
        """
        Execute function with retry and fallback support.

        Args:
            func: Function to execute
            fallback_value: Default value if all retries fail
            timeout: Maximum execution time in seconds
            fallback_on_failure: Override fallback behavior

        Returns:
            Function result or fallback value

        Raises:
            Exception: If no fallback available and all retries fail
        """
        use_fallback = fallback_on_failure if fallback_on_failure is not None else self.fallback_on_failure
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Executing (attempt {attempt}/{self.max_retries})")

                # Execute with optional timeout
                if timeout:
                    result = self._execute_with_timeout(func, timeout)
                else:
                    result = func()

                if attempt > 1:
                    logger.info(f"Succeeded after {attempt} attempts")
                return result

            except (LLMError, TimeoutError, ConnectionError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed: {e}")

                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff

            except Exception as e:
                # Non-retryable error
                logger.error(f"Non-retryable error: {e}")
                raise

        # All retries exhausted
        logger.error(f"All {self.max_retries} attempts failed")

        if use_fallback and fallback_value is not None:
            logger.info(f"Using fallback value: {fallback_value}")
            return fallback_value

        if last_error:
            raise last_error

        raise AgentError("Execution failed with no fallback available")

    def _execute_with_timeout(self, func: Callable, timeout: float) -> Any:
        """Execute function with timeout using threading."""
        import threading

        result_container = [None]
        exception_container = [None]

        def target():
            try:
                result_container[0] = func()
            except Exception as e:
                exception_container[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise TimeoutError(f"Execution timed out after {timeout}s")

        if exception_container[0]:
            raise exception_container[0]

        return result_container[0]


class DefaultValueProvider:
    """Provide default values for different agent types."""

    _DEFAULTS: Dict[str, Dict[str, Any]] = {
        "MarketResearcher": {
            "industry": "general",
            "market_analysis": """# 市场分析 (默认/降级)

## 细分领域
通用市场

## 目标受众
待定 - 需要更多数据

## 痛点分析
暂无竞品数据支持

## 市场机会
使用默认分析框架

## 推荐指数
5/10 (数据不足)
"""
        },
        "ProductManager": {
            "product_plan": """# 产品规划 (默认/降级)

## 产品定位
待定

## 核心功能
- 基础功能一
- 基础功能二

## MVP范围
最小可行产品

## 竞争优势
待分析
"""
        },
        "BusinessModeler": {
            "business_model": """# 商业模式 (默认/降级)

## 收入来源
待确定

## 定价策略
待制定

## 成本结构
待分析

## 关键指标
待定义
"""
        },
        "FinancePlanner": {
            "finance_plan": """# 财务规划 (默认/降级)

## 初始投资
待估算

## 收入预测
待计算

## 盈利时间
待确定

## 财务风险
中等
"""
        },
        "RiskAnalyst": {
            "risk_analysis": """# 风险评估 (默认/降级)

## 市场风险
中等

## 技术风险
待评估

## 运营风险
中等

## 缓解措施
建议获取更多数据
"""
        },
        "ChiefDesigner": {
            "design_strategy": """# 品牌设计 (默认/降级)

## 品牌调性
专业、简洁

## 配色方案
待定

## 视觉风格
现代简约
"""
        },
        "ContentStrategist": {
            "marketing_script": """# 流量脚本 (默认/降级)

## 目标用户
待定位

## 内容策略
待制定

## 推广渠道
待选择
"""
        },
        "SEOExpert": {
            "seo_strategy": """# SEO策略 (默认/降级)

## 目标关键词
待定

## 内容优化
待执行

## 技术SEO
待改进
"""
        }
    }

    def get_default(self, agent_name: str) -> Dict[str, Any]:
        """
        Get default value for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Default context dictionary
        """
        if agent_name in self._DEFAULTS:
            return self._DEFAULTS[agent_name].copy()

        # Generic fallback
        return {
            "fallback": True,
            "message": f"No specific default for {agent_name}"
        }

    def has_default(self, agent_name: str) -> bool:
        """Check if default exists for agent."""
        return agent_name in self._DEFAULTS


class AgentFallbackManager:
    """Track agent failures and manage fallback statistics."""

    def __init__(self):
        """Initialize the fallback manager."""
        self.failed_agents: set = set()
        self.fallback_count: Dict[str, int] = {}
        self.total_executions = 0

    def record_failure(self, agent_name: str) -> None:
        """Record a failed execution."""
        self.failed_agents.add(agent_name)
        self.fallback_count[agent_name] = self.fallback_count.get(agent_name, 0) + 1
        self.total_executions += 1
        logger.warning(f"Agent {agent_name} failed, using fallback")

    def record_success(self, agent_name: str) -> None:
        """Record a successful execution."""
        self.total_executions += 1
        if agent_name in self.failed_agents:
            self.failed_agents.discard(agent_name)

    def get_fallback_rate(self) -> float:
        """Calculate fallback rate."""
        if self.total_executions == 0:
            return 0.0
        return len(self.failed_agents) / self.total_executions

    def get_failure_report(self) -> Dict[str, Any]:
        """Get detailed failure report."""
        return {
            **self.fallback_count,
            "total_fallbacks": sum(self.fallback_count.values()),
            "fallback_rate": self.get_fallback_rate()
        }

    def reset(self) -> None:
        """Reset all statistics."""
        self.failed_agents.clear()
        self.fallback_count.clear()
        self.total_executions = 0


# Global instances
_degrader: Optional[ErrorDegrader] = None
_default_provider: Optional[DefaultValueProvider] = None
_fallback_manager: Optional[AgentFallbackManager] = None


def get_degradation_strategy(
    max_retries: int = 3,
    fallback_on_failure: bool = True
) -> ErrorDegrader:
    """Get or create error degrader instance."""
    global _degrader
    # Always create a new instance with the specified parameters
    _degrader = ErrorDegrader(max_retries, fallback_on_failure)
    return _degrader


def get_default_provider() -> DefaultValueProvider:
    """Get or create default value provider."""
    global _default_provider
    if _default_provider is None:
        _default_provider = DefaultValueProvider()
    return _default_provider


def get_fallback_manager() -> AgentFallbackManager:
    """Get or create fallback manager."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = AgentFallbackManager()
    return _fallback_manager