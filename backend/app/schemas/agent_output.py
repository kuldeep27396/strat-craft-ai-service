"""
Structured output schemas for AI agent responses.

These Pydantic models ensure LLM output matches the expected format
for strategy generation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class StrategySection(BaseModel):
    """A single section of a marketing strategy."""
    heading: str = Field(description="Section title (e.g., 'Executive Summary', 'SEO Strategy')")
    content: str = Field(description="Section body content with detailed explanation")
    tactics: List[str] = Field(description="List of 3-5 specific tactical actions to implement")
    kpis: List[str] = Field(description="List of 2-4 key performance indicators to track")


class PricingInfo(BaseModel):
    """Pricing and team recommendation for the strategy."""
    monthly_cost: int = Field(description="Estimated monthly cost in USD (integer)")
    team: List[str] = Field(description="Recommended team roles (e.g., 'SEO Specialist', 'Content Writer')")


class StrategyContent(BaseModel):
    """Complete marketing strategy document structure."""
    title: str = Field(description="Strategy document title (e.g., 'Growth Strategy for {client_name}')")
    sections: List[StrategySection] = Field(description="Array of strategy sections (3-5 sections)")
    pricing: Optional[PricingInfo] = Field(default=None, description="Optional pricing information")


class AgentContext(BaseModel):
    """Context built from business profile and questionnaire."""
    client_name: str = Field(description="Name of the client/business")
    industry: str = Field(description="Industry sector")
    problem_statement: str = Field(description="Primary problem the business solves")
    target_icp: str = Field(description="Ideal customer profile description")
    business_objectives: List[str] = Field(description="List of business objectives")
    budget_range: Optional[str] = Field(default=None, description="Client's budget range")
    marketing_channels: Optional[List[str]] = Field(default=None, description="Preferred marketing channels")
    products: Optional[List[str]] = Field(default=None, description="Main products/services")
    target_customers: Optional[List[str]] = Field(default=None, description="Target customer segments")


class AgentState(BaseModel):
    """State passed between LangGraph agent nodes."""
    context: AgentContext = Field(description="Built context from business profile and questionnaire")
    executive_summary: Optional[StrategySection] = Field(default=None, description="Executive summary section")
    seo_section: Optional[StrategySection] = Field(default=None, description="SEO strategy section")
    content_section: Optional[StrategySection] = Field(default=None, description="Content marketing section")
    paid_ads_section: Optional[StrategySection] = Field(default=None, description="Paid advertising section")
    quality_passed: Optional[bool] = Field(default=None, description="Quality check result")
    final_strategy: Optional[StrategyContent] = Field(default=None, description="Final assembled strategy")
    iteration: int = Field(default=0, description="Current iteration for refinement loop")
