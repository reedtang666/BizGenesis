"""Agent parallel execution utilities."""
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from loguru import logger


# Agent dependency map: which agents depend on which
# Format: {agent_name: [dependencies]}
AGENT_DEPENDENCIES = {
    "MarketResearcher": [],  # No dependencies - can run first
    "ProductManager": ["MarketResearcher"],  # Depends on market analysis
    "BusinessModeler": ["ProductManager"],  # Depends on product concept
    "FinancePlanner": ["BusinessModeler"],  # Depends on business model
    "RiskAnalyst": ["BusinessModeler", "FinancePlanner"],  # Depends on both
    "ChiefDesigner": [],  # No dependencies - can run in parallel with market
    "ContentStrategist": ["ChiefDesigner"],  # Depends on design
    "SEOExpert": [],  # No dependencies - can run in parallel
}


# Independent agents that can run in parallel
INDEPENDENT_AGENTS = ["MarketResearcher", "ChiefDesigner", "SEOExpert"]


@dataclass
class AgentGroup:
    """Represents a group of agents that can run in parallel."""

    name: str
    agents: List[Callable] = field(default_factory=list)
    depends_on: List["AgentGroup"] = field(default_factory=list)
    dependent_groups: List["AgentGroup"] = field(default_factory=list)

    def __post_init__(self):
        """Set up bidirectional dependencies."""
        for dep in self.depends_on:
            if self not in dep.dependent_groups:
                dep.dependent_groups.append(self)

    def add_agent(self, agent: Callable) -> None:
        """Add an agent to this group."""
        self.agents.append(agent)

    def has_dependencies_satisfied(self, completed_groups: set) -> bool:
        """Check if all dependencies are satisfied."""
        return all(group.name in completed_groups for group in self.depends_on)


@dataclass
class ExecutionResult:
    """Result from executing an agent or group."""

    agent_name: str
    success: bool
    context: Dict[str, Any]
    duration: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class AgentParallelExecutor:
    """
    Executor for running agents in parallel where possible.

    Supports:
    - Identifying independent agents
    - Running agents in parallel
    - Managing dependencies between agents
    - Execution tracking and statistics
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize executor.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self._execution_stats: Dict[str, Dict[str, Any]] = {}
        self._agent_history: List[ExecutionResult] = []

    def execute(self, agent: Any, context: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a single agent.

        Args:
            agent: Agent to execute (must have run method)
            context: Execution context

        Returns:
            ExecutionResult
        """
        agent_name = getattr(agent, "name", agent.__class__.__name__)
        start_time = datetime.now()

        try:
            result_context = agent.run(context)
            duration = (datetime.now() - start_time).total_seconds()

            # Track execution
            self._track_execution(agent_name, True, duration)

            return ExecutionResult(
                agent_name=agent_name,
                success=True,
                context=result_context,
                duration=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent {agent_name} failed: {e}")

            self._track_execution(agent_name, False, duration, str(e))

            return ExecutionResult(
                agent_name=agent_name,
                success=False,
                context=context,
                duration=duration,
                error=str(e)
            )

    def execute_all(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        Execute multiple agents sequentially.

        Args:
            agents: List of agents to execute
            context: Initial context

        Returns:
            List of ExecutionResults
        """
        results = []
        current_context = context.copy()

        for agent in agents:
            result = self.execute(agent, current_context)
            results.append(result)
            current_context = result.context
            if not result.success:
                logger.warning(f"Agent {result.agent_name} failed, continuing...")

        return results

    def execute_parallel(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute multiple agents in parallel.

        Args:
            agents: List of agents to execute
            context: Initial context (will be shared)

        Returns:
            ExecutionResult with merged context
        """
        start_time = datetime.now()

        # Use thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for agent in agents:
                # Each agent gets a copy of the context
                agent_context = context.copy()
                future = executor.submit(self.execute, agent, agent_context)
                futures.append((agent, future))

            # Collect results
            results = []
            for agent, future in futures:
                result = future.result()
                results.append(result)

        duration = (datetime.now() - start_time).total_seconds()
        successful = [r for r in results if r.success]

        # Merge contexts from successful agents
        merged_context = context.copy()
        for result in successful:
            merged_context.update(result.context)

        agent_names = ", ".join(r.agent_name for r in results)

        return ExecutionResult(
            agent_name=f"parallel:[{agent_names}]",
            success=len(successful) > 0,
            context=merged_context,
            duration=duration
        )

    def execute_groups(
        self,
        groups: List[AgentGroup],
        context: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        Execute groups respecting dependencies.

        Args:
            groups: List of AgentGroups to execute
            context: Initial context

        Returns:
            List of ExecutionResults
        """
        results = []
        completed_groups = set()
        current_context = context.copy()

        # Execute groups in order, respecting dependencies
        iterations = 0
        max_iterations = len(groups) * 2

        while len(completed_groups) < len(groups) and iterations < max_iterations:
            iterations += 1

            for group in groups:
                if group.name in completed_groups:
                    continue

                if group.has_dependencies_satisfied(completed_groups):
                    # Execute all agents in this group in parallel
                    if group.agents:
                        result = self.execute_parallel(group.agents, current_context)
                        results.append(result)
                        current_context = result.context
                    else:
                        # Empty group, mark as completed
                        pass

                    completed_groups.add(group.name)
                    logger.info(f"Completed group: {group.name}")

        return results

    def execute_independent_groups(
        self,
        agent_groups: List[List[Any]],
        context: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        Execute multiple independent groups in parallel.

        Args:
            agent_groups: List of agent lists (each list runs in parallel)
            context: Initial context

        Returns:
            List of ExecutionResults
        """
        results = []

        for group_agents in agent_groups:
            result = self.execute_parallel(group_agents, context)
            results.append(result)
            context = result.context

        return results

    def identify_independent_agents(self, agent_names: List[str]) -> List[str]:
        """
        Identify agents that have no dependencies and can run in parallel.

        Args:
            agent_names: List of agent names

        Returns:
            List of agent names that can run in parallel
        """
        independent = []
        for name in agent_names:
            deps = AGENT_DEPENDENCIES.get(name, [])
            if not deps:
                independent.append(name)

        return independent

    def identify_dependent_agents(
        self,
        agent_name: str,
        all_agents: List[str]
    ) -> List[str]:
        """
        Identify agents that the given agent depends on.

        Args:
            agent_name: Name of the agent
            all_agents: List of all agent names

        Returns:
            List of dependency agent names
        """
        deps = AGENT_DEPENDENCIES.get(agent_name, [])
        return [d for d in deps if d in all_agents]

    def get_parallelization_plan(
        self,
        agent_names: List[str]
    ) -> List[List[str]]:
        """
        Create an execution plan with parallelization.

        Args:
            agent_names: List of agent names in execution order

        Returns:
            List of batches where each batch can run in parallel
        """
        batches = []
        completed = set()

        while len(completed) < len(agent_names):
            # Find agents whose dependencies are satisfied
            current_batch = []
            for name in agent_names:
                if name in completed:
                    continue

                deps = AGENT_DEPENDENCIES.get(name, [])
                if all(d in completed for d in deps):
                    current_batch.append(name)

            if not current_batch:
                # Should not happen if dependencies are valid
                remaining = [n for n in agent_names if n not in completed]
                if remaining:
                    current_batch = [remaining[0]]
                else:
                    break

            batches.append(current_batch)
            completed.update(current_batch)

        return batches

    def _track_execution(
        self,
        agent_name: str,
        success: bool,
        duration: float,
        error: Optional[str] = None
    ) -> None:
        """Track execution statistics."""
        if agent_name not in self._execution_stats:
            self._execution_stats[agent_name] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "total_duration": 0.0,
                "errors": []
            }

        stats = self._execution_stats[agent_name]
        stats["total_runs"] += 1
        stats["total_duration"] += duration

        if success:
            stats["successful_runs"] += 1
        else:
            stats["failed_runs"] += 1
            if error:
                stats["errors"].append(error)

    def get_execution_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get execution summary statistics."""
        return self._execution_stats.copy()

    # Async execution methods

    async def execute_async(
        self,
        agent: Any,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute a single agent asynchronously."""
        agent_name = getattr(agent, "name", agent.__class__.__name__)
        start_time = datetime.now()

        try:
            result_context = await agent.run_async(context)
            duration = (datetime.now() - start_time).total_seconds()

            self._track_execution(agent_name, True, duration)

            return ExecutionResult(
                agent_name=agent_name,
                success=True,
                context=result_context,
                duration=duration
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent {agent_name} failed: {e}")

            self._track_execution(agent_name, False, duration, str(e))

            return ExecutionResult(
                agent_name=agent_name,
                success=False,
                context=context,
                duration=duration,
                error=str(e)
            )

    async def execute_all_async(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """Execute multiple agents sequentially with async."""
        results = []
        current_context = context.copy()

        for agent in agents:
            result = await self.execute_async(agent, current_context)
            results.append(result)
            current_context = result.context

        return results

    async def execute_parallel_async(
        self,
        agents: List[Any],
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute multiple agents in parallel with async."""
        start_time = datetime.now()

        # Execute all agents concurrently
        tasks = []
        for agent in agents:
            agent_context = context.copy()
            task = self.execute_async(agent, agent_context)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (datetime.now() - start_time).total_seconds()

        # Process results
        successful_results = []
        for r in results:
            if isinstance(r, ExecutionResult):
                if r.success:
                    successful_results.append(r)
            else:
                logger.error(f"Task failed with exception: {r}")

        # Merge contexts
        merged_context = context.copy()
        for result in successful_results:
            merged_context.update(result.context)

        agent_names = ", ".join(getattr(r, "agent_name", "unknown") for r in successful_results)

        return ExecutionResult(
            agent_name=f"parallel_async:[{agent_names}]",
            success=len(successful_results) > 0,
            context=merged_context,
            duration=duration
        )


# Singleton instance
_executor: Optional[AgentParallelExecutor] = None


def get_parallel_executor() -> AgentParallelExecutor:
    """Get singleton parallel executor."""
    global _executor
    if _executor is None:
        _executor = AgentParallelExecutor()
    return _executor