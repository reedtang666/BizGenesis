"""Tests for competitor data integration functionality."""
import pytest
from unittest.mock import Mock, patch
from src.utils.competitor_data import (
    CompetitorDataCollector,
    CompetitorInfo,
    SearchResult,
    integrate_competitor_data
)


class TestCompetitorInfo:
    """Test cases for CompetitorInfo dataclass."""

    def test_competitor_info_creation(self):
        """Test creating a CompetitorInfo instance."""
        info = CompetitorInfo(
            name="TestCompany",
            description="Test description",
            website="https://test.com",
            strengths=["Strength 1"],
            weaknesses=["Weakness 1"],
            market_position="Leader"
        )

        assert info.name == "TestCompany"
        assert info.description == "Test description"
        assert info.website == "https://test.com"
        assert info.strengths == ["Strength 1"]
        assert info.weaknesses == ["Weakness 1"]
        assert info.market_position == "Leader"


class TestSearchResult:
    """Test cases for SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        result = SearchResult(
            title="Test Result",
            link="https://test.com",
            snippet="Test snippet"
        )

        assert result.title == "Test Result"
        assert result.link == "https://test.com"
        assert result.snippet == "Test snippet"


class TestCompetitorDataCollector:
    """Test cases for CompetitorDataCollector."""

    @pytest.fixture
    def collector(self):
        """Create a CompetitorDataCollector instance."""
        return CompetitorDataCollector()

    def test_collector_initialization(self, collector):
        """Test collector initializes correctly."""
        assert collector.max_competitors == 5
        assert collector.max_results_per_search == 5

    def test_collector_with_custom_config(self):
        """Test collector with custom configuration."""
        collector = CompetitorDataCollector(
            max_competitors=3,
            max_results_per_search=10
        )
        assert collector.max_competitors == 3
        assert collector.max_results_per_search == 10

    def test_search_competitors(self):
        """Test searching for competitors."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {
            "results": [
                {"title": "Company A", "link": "https://companya.com", "snippet": "Desc A"},
                {"title": "Company B", "link": "https://companyb.com", "snippet": "Desc B"},
            ],
            "source": "test"
        }
        collector._search = mock_search

        results = collector.search_competitors("AI SaaS")

        assert len(results) == 2
        assert results[0].title == "Company A"
        assert results[1].title == "Company B"

    def test_search_with_empty_results(self):
        """Test search with no results."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {"results": []}
        collector._search = mock_search

        results = collector.search_competitors("Nonexistent")

        assert len(results) == 0

    def test_search_with_error(self):
        """Test search handles errors gracefully."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {"error": "Search failed", "results": []}
        collector._search = mock_search

        results = collector.search_competitors("Test")

        assert len(results) == 0

    def test_analyze_competitor(self, collector):
        """Test analyzing a competitor."""
        search_result = SearchResult(
            title="Test Company",
            link="https://test.com",
            snippet="A company that does X, Y, Z"
        )

        analysis = collector.analyze_competitor(search_result)

        assert isinstance(analysis, CompetitorInfo)
        assert analysis.name == "Test Company"
        assert analysis.website == "https://test.com"

    def test_collect_all_competitors(self):
        """Test collecting all competitor data."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {
            "results": [
                {"title": "Company A", "link": "https://a.com", "snippet": "Desc A"},
                {"title": "Company B", "link": "https://b.com", "snippet": "Desc B"},
                {"title": "Company C", "link": "https://c.com", "snippet": "Desc C"},
            ],
            "source": "test"
        }
        collector._search = mock_search

        competitors = collector.collect("AI SaaS")

        assert len(competitors) == 3
        assert all(isinstance(c, CompetitorInfo) for c in competitors)

    def test_collect_respects_max_competitors(self):
        """Test collecting respects max_competitors limit."""
        collector = CompetitorDataCollector(max_competitors=2)
        mock_search = Mock()
        mock_search.run.return_value = {
            "results": [
                {"title": f"Company {i}", "link": f"https://c{i}.com", "snippet": f"Desc {i}"}
                for i in range(10)
            ],
            "source": "test"
        }
        collector._search = mock_search

        competitors = collector.collect("Test Industry")

        assert len(competitors) == 2

    def test_get_industry_trends(self):
        """Test getting industry trends."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {
            "results": [
                {"title": "Trend 1", "link": "https://t1.com", "snippet": "Trend desc 1"},
                {"title": "Trend 2", "link": "https://t2.com", "snippet": "Trend desc 2"},
            ],
            "source": "test"
        }
        collector._search = mock_search

        trends = collector.get_industry_trends("AI")

        assert len(trends) == 2

    def test_get_market_keywords(self):
        """Test getting market keywords."""
        collector = CompetitorDataCollector()
        mock_search = Mock()
        mock_search.run.return_value = {
            "results": [
                {"title": "Keyword 1", "link": "", "snippet": "Volume: 10000"},
                {"title": "Keyword 2", "link": "", "snippet": "Volume: 5000"},
            ],
            "source": "test"
        }
        collector._search = mock_search

        keywords = collector.get_market_keywords("SaaS")

        assert len(keywords) == 2


class TestIntegrateCompetitorData:
    """Test cases for integrate_competitor_data function."""

    def test_integrate_competitor_data(self):
        """Test integrating competitor data into context."""
        context = {"industry": "SaaS"}
        competitors = [
            CompetitorInfo(
                name="Company A",
                description="Leader in enterprise",
                website="https://a.com",
                strengths=["Strong brand"],
                weaknesses=["Expensive"],
                market_position="Leader"
            )
        ]

        result = integrate_competitor_data(context, competitors)

        assert "competitor_analysis" in result
        assert "Company A" in result["competitor_analysis"]
        assert result["industry"] == "SaaS"

    def test_integrate_empty_competitors(self):
        """Test integrating with no competitors."""
        context = {"industry": "New Tech"}

        result = integrate_competitor_data(context, [])

        assert "competitor_analysis" in result
        assert "暂无" in result["competitor_analysis"] or "无" in result["competitor_analysis"].lower()

    def test_integrate_preserves_existing_data(self):
        """Test integrating preserves existing context data."""
        context = {
            "industry": "SaaS",
            "existing_key": "existing_value"
        }
        competitors = []

        result = integrate_competitor_data(context, competitors)

        assert result["existing_key"] == "existing_value"
        assert result["industry"] == "SaaS"