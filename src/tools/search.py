"""Web search tool (placeholder for future implementation)."""
from typing import Dict, Any
from .base import BaseTool


class WebSearchTool(BaseTool):
    """Web search tool for market research."""
    
    name = "web_search"
    description = "Search the web for market information"
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Search the web for information.
        Note: Requires API key for real implementation.
        """
        # Placeholder - returns mock data
        return {
            "query": query,
            "results": [
                f"Mock search result for: {query}",
                "To enable real search, configure SERPER_API_KEY or similar"
            ],
            "note": "Implement with Google Serper API for production"
        }
