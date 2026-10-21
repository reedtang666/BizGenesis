"""Base agent class with logging, retry, error degradation, and token monitoring."""
import asyncio
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
        self._active_constraints: str = ""
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
            self._competitor_collector = get_competitor_collector(
                search_api_key=Config.SERPER_API_KEY
            )

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

            if self._active_constraints:
                prompt = f"{prompt}\n\n{self._active_constraints}"

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
                        model_name = getattr(self.llm, 'model_name', '') or ''
                        model_lower = str(model_name).lower()
                        if any(k in model_lower for k in ('flash', 'mini', 'turbo', 'deepseek')):
                            rate_per_token = 0.0000003  # ~$0.30 / 1M tokens
                        elif 'pro' in model_lower or 'gpt-4' in model_lower:
                            rate_per_token = 0.000003   # ~$3.00 / 1M tokens
                        else:
                            rate_per_token = 0.000001   # ~$1.00 / 1M tokens
                        cost = tokens * rate_per_token
                        self._token_monitor.record_usage(self.name, tokens, cost)
                except Exception as e:
                    logger.debug(f"Could not track token usage: {e}")

            return response.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{self.name} failed after {elapsed:.2f}s: {e}")
            raise LLMError(f"LLM call failed: {e}") from e

    @staticmethod
    def format_startup_constraints(context: Dict[str, Any]) -> str:
        """Build startup constraint prompt block from context."""
        parts = []
        if context.get("budget_scale") and context["budget_scale"] != "不限":
            parts.append(f"- 启动资金规模: {context['budget_scale']}")
        if context.get("target_market") and context["target_market"] != "不限":
            parts.append(f"- 目标市场区域: {context['target_market']}")
        if context.get("team_type") and context["team_type"] != "不限":
            parts.append(f"- 团队形态: {context['team_type']}")
        if context.get("extra_requirements"):
            parts.append(f"- 补充要求: {context['extra_requirements']}")
        if not parts:
            return ""
        return "【创业背景与约束条件（请在分析时严格贴合以下实际情况）】\n" + "\n".join(parts)

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
        self._active_constraints = self.format_startup_constraints(context)

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

    def refine(
        self,
        context: Dict[str, Any],
        feedback: str,
        output_key: str
    ) -> Dict[str, Any]:
        """
        Refine a previously generated section based on user feedback.

        Args:
            context: Current execution context
            feedback: User's modification instructions
            output_key: Key in context to update

        Returns:
            Updated context
        """
        industry = context.get("industry", "")
        previous_output = context.get(output_key, "")
        self._active_constraints = self.format_startup_constraints(context)

        if previous_output:
            self.add_to_memory(f"生成【{industry}】方案", previous_output)

        refine_prompt = f"""你刚才为【{industry}】创业项目生成了以下方案内容：

{previous_output}

用户提出了以下修改/追问要求：
【{feedback}】

请在保留原有专业结构的基础上，根据用户的要求针对性地重新优化并输出完整的新版方案内容："""

        updated = self._call_llm(refine_prompt)
        self.add_to_memory(feedback, updated)
        context[output_key] = updated
        return context

    async def run_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task asynchronously in a worker thread."""
        return await asyncio.to_thread(self.run, context)