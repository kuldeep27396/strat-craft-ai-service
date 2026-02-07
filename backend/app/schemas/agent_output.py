"""
Structured output schemas for AI agent responses.

These Pydantic models ensure LLM output matches the expected format
for strategy generation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class StrategySection(BaseModel):
    """A single section of a marketing strategy."""
    heading: str = Field(description="Section title")
    content: str = Field(description="Section body content")
    tactics: List[str] = Field(description="List of tactical actions")
    kpis: List[str] = Field(description="Key performance indicators")


class PricingInfo(BaseModel):
    """Pricing and team recommendation."""
    monthly_cost: int = Field(description="Monthly cost in USD")
    team: List[str] = Field(description="Team roles")


class AgentContext(BaseModel):
    """Context from business profile and questionnaire."""
    client_name: str
    industry: str
    problem_statement: str
    target_icp: str
    business_objectives: List[str]
    budget_range: Optional[str] = None
    marketing_channels: Optional[List[str]] = None
    products: Optional[List[str]] = None
    target_customers: Optional[List[str]] = None
