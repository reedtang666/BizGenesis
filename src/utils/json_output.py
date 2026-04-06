"""JSON output formatter for structured agent responses."""
import json
import re
from typing import Dict, Any, Optional

from loguru import logger


class JSONOutputFormatter:
    """
    Formatter for parsing and validating JSON output from agents.

    Supports:
    - Extracting JSON from markdown code blocks
    - Validating against JSON schema
    - Fallback handling for invalid JSON
    """

    DEFAULT_SCHEMA = {
        "type": "object",
        "properties": {
            "market_analysis": {"type": "string", "description": "市场分析结果"},
            "product_plan": {"type": "string", "description": "产品规划"},
            "business_model": {"type": "string", "description": "商业模式"},
            "finance_plan": {"type": "string", "description": "财务规划"},
            "risk_analysis": {"type": "string", "description": "风险评估"},
            "design_strategy": {"type": "string", "description": "设计策略"},
            "marketing_script": {"type": "string", "description": "营销脚本"},
            "seo_strategy": {"type": "string", "description": "SEO策略"}
        }
    }

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize JSON output formatter.

        Args:
            schema: Optional JSON schema for validation
        """
        self._schema = schema or self.DEFAULT_SCHEMA

    def format_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Format agent response to JSON.

        Args:
            response: Raw response string from agent

        Returns:
            Parsed JSON data or fallback structure
        """
        if not response or not response.strip():
            return self._get_fallback_data("Empty response")

        # Try to extract JSON from response
        parsed = self._parse_json_from_text(response)

        if parsed is not None:
            # Validate if schema is provided
            if self._schema:
                if not self.validate_output(parsed):
                    logger.warning("JSON validation failed, using fallback")
                    return self._get_fallback_data("Validation failed", parsed)
            return parsed

        # Return fallback structure with original text
        return self._get_fallback_data("Invalid JSON", {"raw_response": response})

    def _parse_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON from text.

        Handles:
        - Plain JSON
        - JSON in markdown code blocks (```json ... ```)
        - JSON with leading/trailing text

        Args:
            text: Text containing JSON

        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Try to find JSON in markdown code blocks
        json_block_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_block_pattern, text, re.DOTALL)

        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # Try to find JSON without code blocks
        # First, try direct parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON object from text
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)

        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try more aggressive extraction for nested structures
        brace_start = text.find('{')
        if brace_start != -1:
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(text[brace_start:], start=brace_start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[brace_start:i+1])
                        except json.JSONDecodeError:
                            break

        return None

    def build_json_prompt(self, prompt: str) -> str:
        """
        Build prompt that requests JSON output.

        Args:
            prompt: Original prompt

        Returns:
            Modified prompt requesting JSON output
        """
        schema_hint = json.dumps(self._schema.get("properties", {}), ensure_ascii=False)

        json_instruction = f"""
请以JSON格式返回结果。JSON结构如下:
```json
{schema_hint}
```
请确保返回的是有效的JSON格式，不要包含其他文本。
"""
        return f"{prompt}\n{json_instruction}"

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate JSON output against schema.

        Args:
            data: Parsed JSON data

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        # Check required fields based on schema
        required = self._schema.get("required", [])
        # If no explicit required fields, check if at least some expected fields exist
        properties = self._schema.get("properties", {})

        if required:
            for field in required:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False
        elif properties:
            # Check if at least one property from schema exists in data
            matching_fields = set(data.keys()) & set(properties.keys())
            if not matching_fields:
                logger.warning("No matching fields found in schema")
                return False

        # Check property types
        for key, value in data.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    logger.warning(f"Field {key} should be string, got {type(value)}")
                    return False
                elif expected_type == "array" and not isinstance(value, list):
                    logger.warning(f"Field {key} should be array, got {type(value)}")
                    return False
                elif expected_type == "object" and not isinstance(value, dict):
                    logger.warning(f"Field {key} should be object, got {type(value)}")
                    return False

        return True

    def _get_fallback_data(self, error_msg: str, extra: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create fallback data structure when JSON parsing fails.

        Args:
            error_msg: Error message describing the failure
            extra: Optional extra data to include

        Returns:
            Fallback data structure
        """
        fallback = {
            "error": error_msg,
            "fallback": True
        }
        if extra:
            fallback["data"] = extra
        return fallback


# Singleton instance
_formatter: Optional[JSONOutputFormatter] = None


def get_json_formatter() -> JSONOutputFormatter:
    """Get singleton JSON formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = JSONOutputFormatter()
    return _formatter