"""Tests for Prompt A/B testing functionality."""
import pytest
from unittest.mock import MagicMock, patch
from src.utils.prompt_ab_test import (
    PromptVariant,
    PromptABTest,
    ABTestResult,
    get_ab_test_manager
)


class TestPromptVariant:
    """Test PromptVariant class."""

    def test_variant_creation(self):
        """Test creating a prompt variant."""
        variant = PromptVariant(
            name="variant_a",
            prompt="分析市场 A"
        )
        assert variant.name == "variant_a"
        assert variant.prompt == "分析市场 A"

    def test_variant_with_metadata(self):
        """Test variant with metadata."""
        variant = PromptVariant(
            name="variant_b",
            prompt="分析市场 B",
            metadata={"temperature": 0.8}
        )
        assert variant.metadata["temperature"] == 0.8


class TestABTestResult:
    """Test ABTestResult class."""

    def test_result_creation(self):
        """Test creating A/B test result."""
        result = ABTestResult(
            variant_name="variant_a",
            response="test response",
            success=True,
            tokens_used=100,
            duration=1.5
        )
        assert result.variant_name == "variant_a"
        assert result.success is True

    def test_result_with_error(self):
        """Test result with error."""
        result = ABTestResult(
            variant_name="variant_a",
            response="",
            success=False,
            error="LLM error"
        )
        assert result.success is False
        assert result.error == "LLM error"


class TestPromptABTest:
    """Test PromptABTest class."""

    def test_ab_test_initialization(self):
        """Test A/B test can be initialized."""
        ab_test = PromptABTest(experiment_name="test_experiment")
        assert ab_test is not None

    def test_add_variant(self):
        """Test adding variants to A/B test."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))
        assert len(ab_test.get_variants()) == 2

    def test_get_winner_empty(self):
        """Test getting winner from empty test."""
        ab_test = PromptABTest(experiment_name="test")
        winner = ab_test.get_winner()
        assert winner is None

    def test_record_result(self):
        """Test recording result for a variant."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))

        result = ABTestResult(
            variant_name="A",
            response="response",
            success=True,
            tokens_used=100,
            duration=1.0
        )
        ab_test.record_result("A", result)

        results = ab_test.get_results("A")
        assert len(results) == 1

    def test_get_results_for_variant(self):
        """Test getting results for specific variant."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        result1 = ABTestResult(variant_name="A", response="r1", success=True, tokens_used=100, duration=1.0)
        result2 = ABTestResult(variant_name="A", response="r2", success=True, tokens_used=100, duration=1.0)
        ab_test.record_result("A", result1)
        ab_test.record_result("A", result2)

        results = ab_test.get_results("A")
        assert len(results) == 2

    def test_get_statistics(self):
        """Test getting statistics for variants."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        # Add results for variant A
        ab_test.record_result("A", ABTestResult(variant_name="A", response="r1", success=True, tokens_used=100, duration=1.0))
        ab_test.record_result("A", ABTestResult(variant_name="A", response="r2", success=True, tokens_used=100, duration=1.0))

        # Add results for variant B
        ab_test.record_result("B", ABTestResult(variant_name="B", response="r3", success=False, tokens_used=100, duration=1.0))

        stats = ab_test.get_statistics()
        assert stats["A"]["total_runs"] == 2
        assert stats["A"]["success_rate"] == 1.0
        assert stats["B"]["success_rate"] == 0.0

    def test_get_winner(self):
        """Test getting winner based on success rate."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        # Variant A: 100% success rate
        ab_test.record_result("A", ABTestResult(variant_name="A", response="r1", success=True, tokens_used=100, duration=1.0))

        # Variant B: 0% success rate
        ab_test.record_result("B", ABTestResult(variant_name="B", response="r2", success=False, tokens_used=100, duration=1.0))

        winner = ab_test.get_winner()
        assert winner == "A"

    def test_select_variant_round_robin(self):
        """Test variant selection uses round-robin."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        selected = ab_test.select_variant()
        assert selected.name in ["A", "B"]

    def test_select_best_variant(self):
        """Test selecting best performing variant."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        # A performs better
        for _ in range(5):
            ab_test.record_result("A", ABTestResult(variant_name="A", response="r", success=True, tokens_used=100, duration=1.0))

        # B performs worse
        for _ in range(5):
            ab_test.record_result("B", ABTestResult(variant_name="B", response="r", success=False, tokens_used=100, duration=1.0))

        best = ab_test.select_best_variant()
        assert best == "A"

    def test_reset_experiment(self):
        """Test resetting experiment."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.record_result("A", ABTestResult(variant_name="A", response="r", success=True, tokens_used=100, duration=1.0))

        ab_test.reset()
        assert len(ab_test.get_results("A")) == 0


class TestGetABTestManager:
    """Test get_ab_test_manager function."""

    def test_get_manager_singleton(self):
        """Test singleton pattern for manager."""
        manager1 = get_ab_test_manager()
        manager2 = get_ab_test_manager()
        assert manager1 is manager2

    def test_create_experiment(self):
        """Test creating experiment through manager."""
        manager = get_ab_test_manager()
        exp = manager.create_experiment("test_exp")
        assert exp is not None


class TestPromptABTestEdgeCases:
    """Test edge cases for A/B testing."""

    def test_empty_variant_name(self):
        """Test handling empty variant name."""
        ab_test = PromptABTest(experiment_name="test")
        result = ab_test.get_results("")
        assert result == []

    def test_nonexistent_variant(self):
        """Test getting results for nonexistent variant."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        result = ab_test.get_results("C")  # Doesn't exist
        assert result == []

    def test_all_failed_results(self):
        """Test winner selection when all results failed."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        ab_test.record_result("A", ABTestResult(variant_name="A", response="r", success=False, tokens_used=100, duration=1.0))
        ab_test.record_result("B", ABTestResult(variant_name="B", response="r", success=False, tokens_used=100, duration=1.0))

        # Should return None when no successes
        winner = ab_test.get_winner()
        assert winner is None

    def test_tie_in_success_rate(self):
        """Test winner selection with tied success rates."""
        ab_test = PromptABTest(experiment_name="test")
        ab_test.add_variant(PromptVariant(name="A", prompt="prompt A"))
        ab_test.add_variant(PromptVariant(name="B", prompt="prompt B"))

        # Both have same success rate
        ab_test.record_result("A", ABTestResult(variant_name="A", response="r", success=True, tokens_used=100, duration=1.0))
        ab_test.record_result("B", ABTestResult(variant_name="B", response="r", success=True, tokens_used=100, duration=1.0))

        winner = ab_test.get_winner()
        # When tied, returns first one by default
        assert winner in ["A", "B"]