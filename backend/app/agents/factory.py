"""
Agent factory for creating agent instances.

Following Factory Pattern.
"""

from dataclasses import dataclass
from typing import Callable, Optional

from app.agents.base import ExecutiveSummaryAgent, SEOAgent, ContentAgent, PaidAdsAgent
from app.interfaces.agents import Agent
from app.infrastructure.llm import GroqChainFactory
from app.schemas.agent_output import AgentContext


@dataclass
class AgentDefinition:
    """Definition for creating an agent."""
    name: str
    state_key: str
    system_prompt: str
    user_prompt: str
    use_fast_llm: bool = False
    skip_condition: Optional[Callable[[AgentContext], bool]] = None


class AgentFactory:
    """Factory for creating agent instances."""

    # Agent prompt templates
    PROMPTS = {
        "executive_summary": {
            "system": """You are an expert marketing strategist. Generate a compelling executive summary for a marketing strategy.

Executive Summary should:
- Provide a high-level overview of the recommended approach
- Highlight the key opportunity identified
- Outline the primary focus areas
- Be concise but impactful (2-3 paragraphs)

{format_instructions}""",
            "user": """Generate an executive summary for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Focus on creating a summary that builds confidence and clarity."""
        },
        "seo": {
            "system": """You are an SEO expert. Generate a comprehensive SEO strategy section.

The SEO Strategy should include:
- Technical SEO recommendations
- Content strategy for organic growth
- Keyword approach and target topics
- Link building strategy
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
            "user": """Generate an SEO strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Products: {products}

Focus on practical, actionable SEO recommendations that align with their business."""
        },
        "content": {
            "system": """You are a content marketing expert. Generate a content marketing strategy section.

The Content Marketing Strategy should include:
- Editorial approach and content themes
- Content types and formats
- Distribution channels
- Content calendar framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
            "user": """Generate a content marketing strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Preferred Channels: {marketing_channels}

Create a content strategy that speaks directly to their target audience's needs."""
        },
        "paid_ads": {
            "system": """You are a paid advertising expert. Generate a paid advertising strategy section.

The Paid Ads Strategy should include:
- Platform recommendations (Google, Meta, LinkedIn, etc.)
- Budget allocation strategy
- Campaign types and targeting approach
- Ad creative framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
            "user": """Generate a paid advertising strategy for:

Client: {client_name}
Industry: {industry}
Target ICP: {target_icp}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Recommend efficient paid channels that maximize ROI within their budget."""
        },
    }

    # Agent type mapping
    AGENT_CLASSES = {
        "executive_summary": ExecutiveSummaryAgent,
        "seo": SEOAgent,
        "content": ContentAgent,
        "paid_ads": PaidAdsAgent,
    }

    def __init__(self, chain_factory: GroqChainFactory):
        self.chain_factory = chain_factory

    def create_agent(self, agent_type: str) -> Agent:
        """Create an agent instance by type."""
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Unknown agent type: {agent_type}")

        prompts = self.PROMPTS[agent_type]
        chain = self.chain_factory.create_strategy_chain(
            prompts["system"],
            prompts["user"]
        )

        agent_class = self.AGENT_CLASSES[agent_type]
        state_key = f"{agent_type}_section" if agent_type != "executive_summary" else "executive_summary"

        return agent_class(chain, state_key)

    def create_all_agents(self) -> list[Agent]:
        """Create all available agents."""
        return [self.create_agent(agent_type) for agent_type in self.AGENT_CLASSES.keys()]
