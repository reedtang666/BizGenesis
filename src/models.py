"""
Pydantic models for BizGenesis.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class UserInput(BaseModel):
    """User's initial business idea."""
    idea: str = Field(..., description="User's business idea or keyword")
    industry: Optional[str] = Field(None, description="Industry category")


class MarketAnalysis(BaseModel):
    """Market research results."""
    niche_name: str
    target_audience: str
    pain_point: str


class ProductConcept(BaseModel):
    """Product definition."""
    product_name: str
    usp: str
    differentiators: List[str] = []


class BrandIdentity(BaseModel):
    """Brand and design concepts."""
    brand_name: str
    logo_concept: str
    midjourney_prompt: str


class ContentScript(BaseModel):
    """Marketing content script."""
    platform: str
    hook: str
    script: str
    cta: str


class SEOKeywords(BaseModel):
    """SEO keywords and hashtags."""
    long_tail_keywords: List[str] = []
    hashtags: List[str] = []


class BusinessPlan(BaseModel):
    """Complete business plan."""
    user_input: UserInput
    market_analysis: Optional[MarketAnalysis] = None
    product_concept: Optional[ProductConcept] = None
    brand_identity: Optional[BrandIdentity] = None
    content_script: Optional[ContentScript] = None
    seo_keywords: Optional[SEOKeywords] = None
