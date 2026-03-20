"""
Base agent class with logging and retry mechanism.
"""
import time
from abc import ABC, abstractmethod
from typing import Optional

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

    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name=Config.MODEL_NAME,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure logger for this agent."""
        logger.configure(extra={"agent": self.__class__.__name__})

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging."""
        pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMError, TimeoutError)),
        before_sleep=lambda retry_state: logger.warning(
            f"{self.name} retry {retry_state.attempt_number}/3"
        ),
    )
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with retry logic."""
        start_time = time.time()
        try:
            logger.info(f"{self.name} calling LLM...")
            response = self.llm.invoke(prompt)
            elapsed = time.time() - start_time
            logger.info(f"{self.name} completed in {elapsed:.2f}s")
            return response.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{self.name} failed after {elapsed:.2f}s: {e}")
            raise LLMError(f"{self.name} LLM call failed: {e}") from e

    @abstractmethod
    def run(self, context: dict) -> dict:
        """
        Execute agent task with context.
        Must be implemented by subclasses.
        """
        pass
