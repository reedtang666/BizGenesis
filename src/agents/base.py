"""Base agent class with logging and retry support."""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class LLMError(AgentError):
    """LLM call failed."""
    pass


class BaseAgent(ABC):
    """Base class for all agents with logging and retry support."""
    
    def __init__(self, use_memory: bool = False):
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
            return response.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{self.name} failed after {elapsed:.2f}s: {e}")
            raise LLMError(f"LLM call failed: {e}") from e

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with context."""
        pass
