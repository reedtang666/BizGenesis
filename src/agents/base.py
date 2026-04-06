"""Base agent class with logging, retry, error degradation, and token monitoring."""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from langchain_openai import ChatOpenAI
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config
from src.exceptions import AgentError, LLMError
from src.utils.token_monitor import TokenMonitor, get_token_monitor
from src.utils.error_degradation import (
    ErrorDegrader,
    DefaultValueProvider,
    AgentFallbackManager,
    get_degradation_strategy,
    get_default_provider,
    get_fallback_manager
)
from src.utils.competitor_data import CompetitorDataCollector, get_competitor_collector


class BaseAgent(ABC):
    """Base class for all agents with logging, retry, error degradation and token monitoring."""

    def __init__(
        self,
        use_memory: bool = False,
        token_monitor: Optional[TokenMonitor] = None,
        enable_competitor_data: bool = False,
        enable_token_tracking: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize BaseAgent.

        Args:
            use_memory: Whether to use conversation memory
            token_monitor: Custom token monitor instance
            enable_competitor_data: Enable competitor data collection
            enable_token_tracking: Enable token usage tracking
            max_retries: Maximum retry attempts for LLM calls
        """
        # Get LLM config from provider
        llm_config = Config.get_llm_config()

        self.llm = ChatOpenAI(
            temperature=0.7,
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"]
        )
        self._use_memory = use_memory
        self._conversation_history: List[Dict[str, str]] = []
        self._setup_logger()

        # Token monitoring
        self._enable_token_tracking = enable_token_tracking
        self._token_monitor = token_monitor or get_token_monitor()

        # Error degradation
        self._degrader = get_degradation_strategy(max_retries=max_retries)
        self._default_provider = get_default_provider()
        self._fallback_manager = get_fallback_manager()

        # Competitor data
        self._enable_competitor_data = enable_competitor_data
        if enable_competitor_data:
            self._competitor_collector = get_competitor_collector()

    def _setup_logger(self) -> None:
        """Configure logger for this agent."""
        logger.configure(extra={"agent": self.__class__.__name__})

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging."""
        pass

    def add_to_memory(self, human_input: str, ai_output: str) -> None:
        """Add a conversation turn to memory."""
        self._conversation_history.append({
            "human": human_input,
            "ai": ai_output
        })

    def get_memory_context(self) -> str:
        """Get conversation history as context string."""
        if not self._conversation_history:
            return ""
        context_parts = []
        for turn in self._conversation_history[-3:]:
            context_parts.append(f"Human: {turn['human']}")
            context_parts.append(f"AI: {turn['ai']}")
        return "\n".join(context_parts)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMError, TimeoutError)),
        before_sleep=lambda retry_state: logger.warning(
            f"Retry {retry_state.attempt_number}/3"
        ),
    )
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with retry logic."""
        start_time = time.time()
        try:
            logger.info(f"{self.name} calling LLM...")

            memory_context = self.get_memory_context()
            if memory_context:
                prompt = f"Previous context:\n{memory_context}\n\nCurrent request:\n{prompt}"

            response = self.llm.invoke(prompt)
            elapsed = time.time() - start_time
            logger.info(f"{self.name} completed in {elapsed:.2f}s")

            # Track token usage if enabled
            if self._enable_token_tracking:
                # Try to get usage from response metadata
                try:
                    usage = getattr(response, 'usage_metadata', None)
                    if usage:
                        tokens = usage.get('total_tokens', 0)
                        # Estimate cost (roughly $0.01 per 1K tokens for GPT-4)
                        cost = tokens * 0.00001
                        self._token_monitor.record_usage(self.name, tokens, cost)
                except Exception as e:
                    logger.debug(f"Could not track token usage: {e}")

            return response.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{self.name} failed after {elapsed:.2f}s: {e}")
            raise LLMError(f"LLM call failed: {e}") from e

    def run_with_degradation(
        self,
        context: Dict[str, Any],
        fallback_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run agent with error degradation and fallback support.

        Args:
            context: Context dictionary
            fallback_key: Optional key to store fallback value

        Returns:
            Context with agent result or fallback
        """
        def run_agent():
            return self.run(context)

        try:
            result = self._degrader.execute(
                run_agent,
                fallback_value=None  # Will use default provider if needed
            )

            # Record success
            self._fallback_manager.record_success(self.name)
            return result

        except Exception as e:
            # Record failure
            self._fallback_manager.record_failure(self.name)

            # Try to get default value
            default_context = self._default_provider.get_default(self.__class__.__name__)

            # Merge with existing context
            if fallback_key:
                context[fallback_key] = default_context.get(fallback_key, str(e))
            else:
                # Try to find the appropriate key
                for key in default_context:
                    if key not in context:
                        context[key] = default_context[key]
                        break
                else:
                    # No match found, add error info
                    context[f"error_{self.name}"] = str(e)
                    context["fallback"] = True

            logger.warning(f"{self.name} using fallback due to: {e}")
            return context

    def _collect_competitor_data(self, industry: str) -> Dict[str, Any]:
        """
        Collect competitor data for an industry.

        Args:
            industry: Industry to research

        Returns:
            Context with competitor data
        """
        try:
            competitors = self._competitor_collector.collect(industry)
            trends = self._competitor_collector.get_industry_trends(industry)

            context = {
                "competitor_count": len(competitors),
                "competitor_trends": [
                    {"title": t.title, "snippet": t.snippet}
                    for t in trends[:3]
                ]
            }

            # Integrate into context
            from src.utils.competitor_data import integrate_competitor_data
            return integrate_competitor_data(context, competitors)

        except Exception as e:
            logger.error(f"Failed to collect competitor data: {e}")
            return {"competitor_data_error": str(e)}

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with context."""
        pass