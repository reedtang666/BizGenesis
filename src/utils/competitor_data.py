"""Competitor data collection and integration."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from loguru import logger

from src.tools.search import WebSearchTool


@dataclass
class SearchResult:
    """Represents a search result."""
    title: str
    link: str
    snippet: str


@dataclass
class CompetitorInfo:
    """Represents a competitor's information."""
    name: str
    description: str
    website: str
    strengths: List[str]
    weaknesses: List[str]
    market_position: str  # Leader, Challenger, Niche, Emerging


class CompetitorDataCollector:
    """Collect competitor data using web search."""

    def __init__(
        self,
        max_competitors: int = 5,
        max_results_per_search: int = 5,
        search_api_key: Optional[str] = None
    ):
        """
        Initialize competitor data collector.

        Args:
            max_competitors: Maximum number of competitors to analyze
            max_results_per_search: Maximum results per search query
            search_api_key: Optional Serper API key for better results
        """
        self.max_competitors = max_competitors
        self.max_results_per_search = max_results_per_search
        self._search = WebSearchTool(api_key=search_api_key)

    def search_competitors(self, industry: str) -> List[SearchResult]:
        """
        Search for competitors in an industry.

        Args:
            industry: Industry to search

        Returns:
            List of search results
        """
        query = f"top {industry} companies competitors market leaders"
        logger.info(f"Searching for competitors: {query}")

        try:
            result = self._search.run(query, self.max_results_per_search)

            # Handle error case
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Search error: {result.get('error', 'Unknown')}")
                return []

            # Handle mock or regular response
            results_list = result.get("results", []) if isinstance(result, dict) else []
            if not results_list:
                return []

            results = []
            for item in results_list[:self.max_results_per_search]:
                results.append(SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", "")
                ))

            logger.info(f"Found {len(results)} competitor results")
            return results

        except Exception as e:
            logger.error(f"Failed to search competitors: {e}")
            return []

    def analyze_competitor(self, search_result: SearchResult) -> Optional[CompetitorInfo]:
        """
        Analyze a competitor from search result.

        Args:
            search_result: Raw search result

        Returns:
            CompetitorInfo or None
        """
        try:
            # For now, create basic info from search result
            # In production, could enhance with additional searches
            return CompetitorInfo(
                name=search_result.title,
                description=search_result.snippet,
                website=search_result.link,
                strengths=[],  # To be filled by LLM later
                weaknesses=[],
                market_position="Unknown"
            )
        except Exception as e:
            logger.error(f"Failed to analyze competitor: {e}")
            return None

    def collect(self, industry: str) -> List[CompetitorInfo]:
        """
        Collect competitor data for an industry.

        Args:
            industry: Industry to research

        Returns:
            List of competitor information
        """
        # Search for competitors
        search_results = self.search_competitors(industry)

        if not search_results:
            logger.warning(f"No competitor results for {industry}")
            return []

        # Analyze each competitor
        competitors = []
        for result in search_results[:self.max_competitors]:
            info = self.analyze_competitor(result)
            if info:
                competitors.append(info)

        logger.info(f"Collected {len(competitors)} competitors")
        return competitors

    def get_industry_trends(self, industry: str) -> List[SearchResult]:
        """
        Get industry trends.

        Args:
            industry: Industry to research

        Returns:
            List of trend results
        """
        query = f"{industry} market trends 2024 2025"
        logger.info(f"Searching for trends: {query}")

        try:
            result = self._search.run(query, self.max_results_per_search)

            # Handle error case
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Search error: {result.get('error', 'Unknown')}")
                return []

            # Handle mock or regular response
            results_list = result.get("results", []) if isinstance(result, dict) else []
            if not results_list:
                return []

            return [
                SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", "")
                )
                for item in results_list[:self.max_results_per_search]
            ]

        except Exception as e:
            logger.error(f"Failed to search trends: {e}")
            return []

    def get_market_keywords(self, industry: str) -> List[SearchResult]:
        """
        Get popular keywords for an industry.

        Args:
            industry: Industry to research

        Returns:
            List of keyword results
        """
        query = f"{industry} popular keywords SEO trends"
        logger.info(f"Searching for keywords: {query}")

        try:
            result = self._search.run(query, self.max_results_per_search)

            # Handle error case
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Search error: {result.get('error', 'Unknown')}")
                return []

            # Handle mock or regular response
            results_list = result.get("results", []) if isinstance(result, dict) else []
            if not results_list:
                return []

            return [
                SearchResult(
                    title=item.get("title", ""),
                    link=item.get("link", ""),
                    snippet=item.get("snippet", "")
                )
                for item in results_list[:self.max_results_per_search]
            ]

        except Exception as e:
            logger.error(f"Failed to search keywords: {e}")
            return []


def integrate_competitor_data(
    context: Dict[str, Any],
    competitors: List[CompetitorInfo]
) -> Dict[str, Any]:
    """
    Integrate competitor data into context.

    Args:
        context: Existing context dictionary
        competitors: List of competitors

    Returns:
        Updated context with competitor data
    """
    if not competitors:
        context["competitor_analysis"] = "暂无竞品数据，请手动补充"
        context["competitors"] = []
        return context

    # Build competitor analysis text
    analysis_parts = ["# 竞品分析\n"]

    for i, comp in enumerate(competitors, 1):
        analysis_parts.append(f"## {i}. {comp.name}")
        analysis_parts.append(f"官网: {comp.website}")
        analysis_parts.append(f"简介: {comp.description}")
        analysis_parts.append(f"市场定位: {comp.market_position}")

        if comp.strengths:
            analysis_parts.append("优势:")
            for s in comp.strengths:
                analysis_parts.append(f"- {s}")

        if comp.weaknesses:
            analysis_parts.append("劣势:")
            for w in comp.weaknesses:
                analysis_parts.append(f"- {w}")

        analysis_parts.append("")  # Empty line

    context["competitor_analysis"] = "\n".join(analysis_parts)
    context["competitors"] = [
        {
            "name": c.name,
            "website": c.website,
            "position": c.market_position
        }
        for c in competitors
    ]

    return context


# Global collector instance
_collector: Optional[CompetitorDataCollector] = None


def get_competitor_collector(
    max_competitors: int = 5,
    search_api_key: Optional[str] = None
) -> CompetitorDataCollector:
    """Get or create competitor collector instance."""
    global _collector
    if _collector is None:
        _collector = CompetitorDataCollector(
            max_competitors=max_competitors,
            search_api_key=search_api_key
        )
    return _collector