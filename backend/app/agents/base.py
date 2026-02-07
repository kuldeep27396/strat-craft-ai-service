"""
Base agent implementations using Strategy Pattern.

Each agent is a concrete strategy that can be swapped independently.
"""

from abc import abstractmethod
from typing import Optional
from langchain_core.runnables import Runnable

from app.interfaces.agents import Agent
from app.schemas.agent_output import StrategySection, AgentContext


class BaseLLMAgent(Agent):
    """Base class for LLM-powered agents."""

    def __init__(self, chain: Runnable, state_key: str):
        self.chain = chain
        self.state_key = state_key

    @property
    def name(self) -> str:
        return self.state_key.replace("_section", "").replace("_", " ").title()

    def should_skip(self, context: AgentContext) -> bool:
        """Default: never skip."""
        return False

    async def execute(self, context: AgentContext) -> StrategySection:
        """Execute the agent with the given context."""
        params = self._build_params(context)
        return await self.chain.ainvoke(params)

    @abstractmethod
    def _build_params(self, context: AgentContext) -> dict:
        """Build parameters for the LLM chain."""
        pass


class ExecutiveSummaryAgent(BaseLLMAgent):
    """Generates executive summary section."""

    def _build_params(self, context: AgentContext) -> dict:
        return {
            "format_instructions": self._format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "business_objectives": ", ".join(context.business_objectives or []),
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels or []),
        }

    def _format_instructions(self) -> str:
        return self.chain.middleware[0].parser.get_format_instructions()


class SEOAgent(BaseLLMAgent):
    """Generates SEO strategy section."""

    def _build_params(self, context: AgentContext) -> dict:
        return {
            "format_instructions": self._format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "products": ", ".join(context.products or []),
        }


class ContentAgent(BaseLLMAgent):
    """Generates content marketing section."""

    def _build_params(self, context: AgentContext) -> dict:
        return {
            "format_instructions": self._format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "business_objectives": ", ".join(context.business_objectives or []),
            "marketing_channels": ", ".join(context.marketing_channels or []),
        }


class PaidAdsAgent(BaseLLMAgent):
    """Generates paid advertising section."""

    def should_skip(self, context: AgentContext) -> bool:
        """Skip if budget indicates no paid ads."""
        budget = (context.budget_range or "").lower()
        return any(term in budget for term in ['$0', 'none', 'organic only', 'no budget'])

    def _build_params(self, context: AgentContext) -> dict:
        return {
            "format_instructions": self._format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "target_icp": context.target_icp,
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels or []),
        }
