"""
Base agent class with logging, retry, and memory support.
"""
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
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
    """
    Base class for all agents with logging, retry, and memory support.
    """
    
    def __init__(self, use_memory: bool = False):
        """
        Initialize the agent.
        
        Args:
            use_memory: Whether to use conversation memory
        """
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name=Config.MODEL_NAME,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self._use_memory = use_memory
        self._memory: Optional[ConversationBufferMemory] = None
        self._conversation_history: List[Dict[str, str]] = []
        self._setup_logger()
        
        if use_memory:
            self._memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
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
        
        if self._memory:
            self._memory.save_context(
                {"input": human_input},
                {"output": ai_output}
            )

    def get_memory_context(self) -> str:
        """Get conversation history as context string."""
        if not self._conversation_history:
            return ""
        
        context_parts = []
        for turn in self._conversation_history[-3:]:  # Last 3 turns
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
        """
        Call LLM with retry logic.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM response content
        """
        start_time = time.time()
        try:
            logger.info(f"{self.name} calling LLM...")
            
            # Add memory context if available
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

    async def _call_llm_async(self, prompt: str) -> str:
        """
        Async version of LLM call.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM response content
        """
        # Run synchronous call in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._call_llm, prompt)

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with context.
        Must be implemented by subclasses.
        
        Args:
            context: Shared context dictionary
            
        Returns:
            Updated context dictionary
        """
        pass

    async def run_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async version of run.
        Default implementation wraps synchronous run.
        
        Args:
            context: Shared context dictionary
            
        Returns:
            Updated context dictionary
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, context)
