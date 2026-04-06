"""Prompt A/B testing functionality."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

from loguru import logger


@dataclass
class PromptVariant:
    """Represents a prompt variant for A/B testing."""

    name: str
    prompt: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestResult:
    """Results from a single A/B test run."""

    variant_name: str
    response: str
    success: bool
    tokens_used: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class PromptABTest:
    """
    A/B testing framework for prompt optimization.

    Supports:
    - Multiple prompt variants
    - Round-robin variant selection
    - Success rate tracking
    - Winner determination
    """

    def __init__(self, experiment_name: str):
        """
        Initialize A/B test.

        Args:
            experiment_name: Name of the experiment
        """
        self.experiment_name = experiment_name
        self._variants: Dict[str, PromptVariant] = {}
        self._results: Dict[str, List[ABTestResult]] = {}
        self._round_robin_index = 0

    def add_variant(self, variant: PromptVariant) -> None:
        """
        Add a prompt variant.

        Args:
            variant: PromptVariant to add
        """
        self._variants[variant.name] = variant
        self._results[variant.name] = []
        logger.info(f"Added variant '{variant.name}' to experiment '{self.experiment_name}'")

    def get_variants(self) -> List[PromptVariant]:
        """Get list of all variants."""
        return list(self._variants.values())

    def get_variant(self, name: str) -> Optional[PromptVariant]:
        """Get variant by name."""
        return self._variants.get(name)

    def select_variant(self) -> Optional[PromptVariant]:
        """
        Select a variant using round-robin.

        Returns:
            Selected variant or None if no variants
        """
        if not self._variants:
            return None

        variant_names = list(self._variants.keys())
        selected = variant_names[self._round_robin_index % len(variant_names)]
        self._round_robin_index += 1

        return self._variants[selected]

    def select_best_variant(self) -> Optional[str]:
        """
        Select the best performing variant based on historical data.

        Returns:
            Name of best variant or None
        """
        stats = self.get_statistics()
        if not stats:
            return None

        best_variant = None
        best_score = -1

        for variant_name, variant_stats in stats.items():
            if variant_stats["total_runs"] > 0:
                # Score = success_rate * 0.7 + (1 / avg_tokens) * 0.3
                success_score = variant_stats["success_rate"] * 0.7
                tokens_score = 0
                if variant_stats.get("avg_tokens", 0) > 0:
                    tokens_score = (1 / variant_stats["avg_tokens"]) * 0.3 * 10000

                score = success_score + tokens_score
                if score > best_score:
                    best_score = score
                    best_variant = variant_name

        return best_variant

    def record_result(self, variant_name: str, result: ABTestResult) -> None:
        """
        Record a test result.

        Args:
            variant_name: Name of the variant
            result: ABTestResult to record
        """
        if variant_name not in self._results:
            logger.warning(f"Recording result for unknown variant: {variant_name}")
            self._results[variant_name] = []

        self._results[variant_name].append(result)
        logger.info(f"Recorded result for variant '{variant_name}': success={result.success}")

    def get_results(self, variant_name: str) -> List[ABTestResult]:
        """Get all results for a variant."""
        return self._results.get(variant_name, [])

    def get_all_results(self) -> Dict[str, List[ABTestResult]]:
        """Get all results."""
        return self._results

    def get_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all variants.

        Returns:
            Dictionary of variant statistics
        """
        stats = {}

        for variant_name, results in self._results.items():
            if not results:
                stats[variant_name] = {
                    "total_runs": 0,
                    "success_rate": 0.0,
                    "avg_tokens": 0.0,
                    "avg_duration": 0.0
                }
                continue

            total_runs = len(results)
            successes = sum(1 for r in results if r.success)
            total_tokens = sum(r.tokens_used for r in results)
            total_duration = sum(r.duration for r in results)

            stats[variant_name] = {
                "total_runs": total_runs,
                "success_rate": successes / total_runs if total_runs > 0 else 0.0,
                "avg_tokens": total_tokens / total_runs if total_runs > 0 else 0.0,
                "avg_duration": total_duration / total_runs if total_runs > 0 else 0.0
            }

        return stats

    def get_winner(self) -> Optional[str]:
        """
        Get the winning variant based on success rate.

        Returns:
            Name of winning variant or None
        """
        stats = self.get_statistics()
        if not stats:
            return None

        best_variant = None
        best_rate = -1

        for variant_name, variant_stats in stats.items():
            if variant_stats["total_runs"] > 0:
                rate = variant_stats["success_rate"]
                if rate > best_rate:
                    best_rate = rate
                    best_variant = variant_name

        # If no successful runs, return None
        if best_rate == 0:
            return None

        return best_variant

    def reset(self) -> None:
        """Reset all results."""
        self._results = {name: [] for name in self._variants.keys()}
        self._round_robin_index = 0
        logger.info(f"Reset experiment '{self.experiment_name}'")


class ABTestManager:
    """
    Manager for multiple A/B tests.
    """

    def __init__(self):
        """Initialize manager."""
        self._experiments: Dict[str, PromptABTest] = {}

    def create_experiment(self, experiment_name: str) -> PromptABTest:
        """
        Create a new A/B test experiment.

        Args:
            experiment_name: Name of the experiment

        Returns:
            New PromptABTest instance
        """
        if experiment_name in self._experiments:
            logger.warning(f"Experiment '{experiment_name}' already exists, returning existing")
            return self._experiments[experiment_name]

        experiment = PromptABTest(experiment_name)
        self._experiments[experiment_name] = experiment
        logger.info(f"Created experiment '{experiment_name}'")
        return experiment

    def get_experiment(self, experiment_name: str) -> Optional[PromptABTest]:
        """Get experiment by name."""
        return self._experiments.get(experiment_name)

    def list_experiments(self) -> List[str]:
        """List all experiment names."""
        return list(self._experiments.keys())

    def delete_experiment(self, experiment_name: str) -> bool:
        """Delete an experiment."""
        if experiment_name in self._experiments:
            del self._experiments[experiment_name]
            return True
        return False


# Singleton instance
_manager: Optional[ABTestManager] = None


def get_ab_test_manager() -> ABTestManager:
    """Get singleton A/B test manager."""
    global _manager
    if _manager is None:
        _manager = ABTestManager()
    return _manager