"""Web search tools for market research."""
import json
from typing import Dict, Any, List, Optional
from loguru import logger

from .base import BaseTool


class WebSearchTool(BaseTool):
    """Web search tool supporting multiple search APIs."""
    
    name = "web_search"
    description = "Search the web for market information and trends"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize search tool.
        
        Args:
            api_key: Serper API key (optional, falls back to DuckDuckGo)
        """
        self.api_key = api_key
        self._use_serper = bool(api_key)
    
    def run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        try:
            if self._use_serper:
                return self._search_serper(query, num_results)
            else:
                return self._search_duckduckgo(query, num_results)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e), "results": []}
    
    def _search_serper(self, query: str, num_results: int) -> Dict[str, Any]:
        """Search using Serper API (Google Search)."""
        import requests
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"q": query, "num": num_results}
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        
        return {
            "query": query,
            "source": "serper",
            "results": results
        }
    
    def _search_duckduckgo(self, query: str, num_results: int) -> Dict[str, Any]:
        """Search using DuckDuckGo (free, no API key required)."""
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num_results):
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        
        return {
            "query": query,
            "source": "duckduckgo",
            "results": results
        }


class MarketSearchTool(BaseTool):
    """Specialized tool for market research searches."""
    
    name = "market_search"
    description = "Search for market trends, competitors, and industry insights"
    
    def __init__(self, search_tool: Optional[WebSearchTool] = None):
        self._search = search_tool or WebSearchTool()
    
    def run(self, industry: str, search_type: str = "trends") -> Dict[str, Any]:
        """
        Perform market-specific searches.
        
        Args:
            industry: Industry or niche to research
            search_type: Type of search (trends, competitors, keywords)
            
        Returns:
            Aggregated market research results
        """
        queries = {
            "trends": f"{industry} market trends 2024",
            "competitors": f"top {industry} brands competitors",
            "keywords": f"{industry} popular keywords SEO",
            "pain_points": f"{industry} customer problems pain points"
        }
        
        query = queries.get(search_type, queries["trends"])
        return self._search.run(query)


# Factory function
def get_search_tool(api_key: Optional[str] = None) -> WebSearchTool:
    """Get configured search tool."""
    return WebSearchTool(api_key)
