"""Tests for JSON output formatter."""
import pytest
from unittest.mock import MagicMock, patch
from src.utils.json_output import JSONOutputFormatter, get_json_formatter


class TestJSONOutputFormatter:
    """Test JSONOutputFormatter class."""

    def test_formatter_initialization(self):
        """Test formatter can be initialized."""
        formatter = JSONOutputFormatter()
        assert formatter is not None

    def test_formatter_with_custom_schema(self):
        """Test formatter with custom JSON schema."""
        schema = {
            "type": "object",
            "properties": {
                "market_analysis": {"type": "string"},
                "product_plan": {"type": "string"}
            }
        }
        formatter = JSONOutputFormatter(schema=schema)
        assert formatter._schema == schema

    def test_format_agent_response_valid_json(self):
        """Test formatting valid JSON response."""
        formatter = JSONOutputFormatter()
        json_str = '{"market_analysis": "test market", "product_plan": "test product"}'
        result = formatter.format_agent_response(json_str)
        assert result is not None
        assert "market_analysis" in result

    def test_format_agent_response_with_json_wrapper(self):
        """Test formatting response wrapped in markdown code block."""
        formatter = JSONOutputFormatter()
        json_str = '```json\n{"market_analysis": "test market"}\n```'
        result = formatter.format_agent_response(json_str)
        assert result is not None

    def test_format_agent_response_plain_json(self):
        """Test formatting plain JSON without wrapper."""
        formatter = JSONOutputFormatter()
        json_str = '{"market_analysis": "test market"}'
        result = formatter.format_agent_response(json_str)
        assert result is not None

    def test_format_agent_response_invalid_json_returns_fallback(self):
        """Test fallback when invalid JSON is provided."""
        formatter = JSONOutputFormatter()
        invalid_json = "This is not JSON"
        result = formatter.format_agent_response(invalid_json)
        # Should return original text in fallback format
        assert result is not None

    def test_format_agent_response_empty_string(self):
        """Test handling empty string."""
        formatter = JSONOutputFormatter()
        result = formatter.format_agent_response("")
        assert result is not None

    def test_build_json_prompt_basic(self):
        """Test building prompt that requests JSON output."""
        formatter = JSONOutputFormatter()
        prompt = "分析市场"
        result = formatter.build_json_prompt(prompt)
        assert "JSON" in result
        assert prompt in result

    def test_build_json_prompt_with_schema(self):
        """Test building prompt with custom schema."""
        schema = {
            "type": "object",
            "properties": {
                "market_analysis": {"type": "string", "description": "市场分析"}
            }
        }
        formatter = JSONOutputFormatter(schema=schema)
        prompt = "分析市场"
        result = formatter.build_json_prompt(prompt)
        assert "JSON" in result
        assert "market_analysis" in result

    def test_validate_output_valid(self):
        """Test validating valid JSON output."""
        formatter = JSONOutputFormatter()
        data = {"market_analysis": "test"}
        assert formatter.validate_output(data) is True

    def test_validate_output_invalid(self):
        """Test validating invalid JSON output."""
        formatter = JSONOutputFormatter()
        data = {"invalid_field": "test"}
        # Should fail validation when required fields missing
        result = formatter.validate_output(data)
        assert result is False

    def test_validate_output_with_schema(self):
        """Test validation with custom schema."""
        schema = {
            "type": "object",
            "required": ["market_analysis"],
            "properties": {
                "market_analysis": {"type": "string"}
            }
        }
        formatter = JSONOutputFormatter(schema=schema)
        valid_data = {"market_analysis": "test"}
        invalid_data = {"other": "test"}
        assert formatter.validate_output(valid_data) is True
        assert formatter.validate_output(invalid_data) is False

    def test_get_json_formatter_singleton(self):
        """Test singleton pattern for get_json_formatter."""
        formatter1 = get_json_formatter()
        formatter2 = get_json_formatter()
        assert formatter1 is formatter2

    def test_parse_json_from_text_with_backticks(self):
        """Test parsing JSON from text with backticks."""
        formatter = JSONOutputFormatter()
        text = 'Here is the JSON: ```json\n{"key": "value"}\n```'
        result = formatter._parse_json_from_text(text)
        assert result is not None

    def test_parse_json_from_text_without_wrapper(self):
        """Test parsing JSON without backtick wrapper."""
        formatter = JSONOutputFormatter()
        text = '{"key": "value"}'
        result = formatter._parse_json_from_text(text)
        assert result is not None

    def test_parse_json_from_text_malformed(self):
        """Test parsing malformed JSON."""
        formatter = JSONOutputFormatter()
        text = "not valid json at all"
        result = formatter._parse_json_from_text(text)
        assert result is None


class TestJSONOutputFormatterEdgeCases:
    """Test edge cases for JSON output formatter."""

    def test_nested_json_parsing(self):
        """Test parsing nested JSON structures."""
        formatter = JSONOutputFormatter()
        json_str = '{"data": {"nested": {"deep": "value"}}}'
        result = formatter.format_agent_response(json_str)
        assert result is not None

    def test_json_with_special_characters(self):
        """Test JSON with special characters."""
        formatter = JSONOutputFormatter()
        json_str = '{"text": "测试中文 with \"quotes\" and \\ backslash"}'
        result = formatter.format_agent_response(json_str)
        assert result is not None

    def test_json_array_parsing(self):
        """Test parsing JSON arrays."""
        formatter = JSONOutputFormatter()
        json_str = '{"items": ["a", "b", "c"]}'
        result = formatter.format_agent_response(json_str)
        assert result is not None