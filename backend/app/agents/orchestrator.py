"""
AI Agent Orchestrator using LangGraph

This module implements a multi-agent system for strategy generation
using Groq's fast LLM models (Llama 3.1 and Mixtral).

Refactored following SOLID, DRY, and YAGNI principles.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

from app.config import settings
from app.schemas.agent_output import StrategySection, PricingInfo, AgentContext


@dataclass
class AgentConfig:
    """Configuration for a strategy generation agent."""
    name: str
    state_key: str
    system_prompt: str
    user_prompt_template: str
    skip_condition: Optional[Callable[[AgentContext], bool]] = None
    use_fast_llm: bool = False


@dataclass
class GraphState:
    """State for the LangGraph workflow."""
    context: AgentContext
    sections: dict[str, StrategySection] = field(default_factory=dict)
    pricing: Optional[dict] = None
    quality_passed: bool = False


# Agent configurations - DRY: define once, use everywhere
AGENT_CONFIGS = [
    AgentConfig(
        name="executive_summary",
        state_key="executive_summary",
        system_prompt="""You are an expert marketing strategist. Generate a compelling executive summary for a marketing strategy.

Executive Summary should:
- Provide a high-level overview of the recommended approach
- Highlight the key opportunity identified
- Outline the primary focus areas
- Be concise but impactful (2-3 paragraphs)

{format_instructions}""",
        user_prompt_template="""Generate an executive summary for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Focus on creating a summary that builds confidence and clarity."""
    ),
    AgentConfig(
        name="seo",
        state_key="seo_section",
        system_prompt="""You are an SEO expert. Generate a comprehensive SEO strategy section.

The SEO Strategy should include:
- Technical SEO recommendations
- Content strategy for organic growth
- Keyword approach and target topics
- Link building strategy
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
        user_prompt_template="""Generate an SEO strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Products: {products}

Focus on practical, actionable SEO recommendations that align with their business."""
    ),
    AgentConfig(
        name="content",
        state_key="content_section",
        system_prompt="""You are a content marketing expert. Generate a content marketing strategy section.

The Content Marketing Strategy should include:
- Editorial approach and content themes
- Content types and formats
- Distribution channels
- Content calendar framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
        user_prompt_template="""Generate a content marketing strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Preferred Channels: {marketing_channels}

Create a content strategy that speaks directly to their target audience's needs."""
    ),
    AgentConfig(
        name="paid_ads",
        state_key="paid_ads_section",
        system_prompt="""You are a paid advertising expert. Generate a paid advertising strategy section.

The Paid Ads Strategy should include:
- Platform recommendations (Google, Meta, LinkedIn, etc.)
- Budget allocation strategy
- Campaign types and targeting approach
- Ad creative framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}""",
        user_prompt_template="""Generate a paid advertising strategy for:

Client: {client_name}
Industry: {industry}
Target ICP: {target_icp}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Recommend efficient paid channels that maximize ROI within their budget.""",
        skip_condition=lambda ctx: any(term in (ctx.budget_range or "").lower() for term in ['$0', 'none', 'organic only', 'no budget'])
    ),
]


class StrategyOrchestrator:
    """
    Orchestrator for AI strategy generation using LangGraph.

    Follows Single Responsibility: only coordinates workflow execution.
    Agent logic is data-driven via AgentConfig.
    """

    def __init__(self, groq_api_key: str | None = None):
        """Initialize with LLM clients."""
        self.api_key = groq_api_key or getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY required. Get it at https://console.groq.com/")

        # YAGNI: Only two models needed, not three
        self.llm = ChatGroq(api_key=self.api_key, model_name=getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use'))
        self.fast_llm = ChatGroq(api_key=self.api_key, model_name=getattr(settings, 'GROQ_FAST_MODEL', 'llama-3.1-8b-instant'))

        # Pre-build chains for each agent (Open/Closed Principle)
        self._chains: dict[str, Runnable] = {}
        for config in AGENT_CONFIGS:
            self._chains[config.name] = self._build_chain(config)

        self.workflow = self._build_workflow()

    def _build_chain(self, config: AgentConfig) -> Runnable:
        """Build an LLM chain from config."""
        parser = PydanticOutputParser(pydantic_object=StrategySection)
        prompt = ChatPromptTemplate.from_messages([
            ("system", config.system_prompt),
            ("user", config.user_prompt_template)
        ])
        llm = self.fast_llm if config.use_fast_llm else self.llm
        return prompt | llm | parser

    def _build_context(self, business_profile: Dict, questionnaire: Dict) -> AgentContext:
        """Build context with safe defaults (DRY: extract helper logic)."""
        def safe_list(val: Any) -> list | None:
            return val if isinstance(val, list) else None

        def safe_str(val: Any) -> str:
            return val if isinstance(val, str) else str(val) if val else ""

        return AgentContext(
            client_name=questionnaire.get('client_name', business_profile.get('name', 'Client')),
            industry=business_profile.get('industry', 'Unknown'),
            problem_statement=questionnaire.get('problem_statement', ''),
            target_icp=safe_str(questionnaire.get('target_icp')),
            business_objectives=safe_list(questionnaire.get('business_objectives')) or ['Grow business'],
            budget_range=questionnaire.get('budget_range'),
            marketing_channels=safe_list(questionnaire.get('marketing_channels')),
            products=safe_list(business_profile.get('products')),
            target_customers=safe_list(business_profile.get('target_customers'))
        )

    def _format_context_params(self, context: AgentContext, include_products: bool = False) -> Dict[str, str]:
        """Format context for LLM prompts (DRY: single source of truth)."""
        return {
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "business_objectives": ", ".join(context.business_objectives or []),
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels or []),
            **({"products": ", ".join(context.products or [])} if include_products else {})
        }

    async def _run_agent(self, config: AgentConfig, state: GraphState) -> GraphState:
        """Run a single agent (Template Method pattern)."""
        # Check skip condition
        if config.skip_condition and config.skip_condition(state['context']):
            return state

        chain = self._chains[config.name]
        params = self._format_context_params(
            state['context'],
            include_products=config.name == "seo"
        )

        result = await chain.ainvoke(params)
        state['sections'][config.state_key] = result
        return state

    async def _check_quality(self, state: GraphState) -> GraphState:
        """Validate minimum required sections."""
        state['quality_passed'] = len(state['sections']) >= 2
        return state

    async def _assemble_pricing(self, state: GraphState) -> GraphState:
        """Generate pricing using fast LLM."""
        parser = PydanticOutputParser(pydantic_object=PricingInfo)
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate appropriate pricing and team recommendations. Consider industry, scope, and budget. {format_instructions}"""),
            ("user", "Client: {client_name}\nIndustry: {industry}\nBudget: {budget_range}\nChannels: {marketing_channels}")
        ])

        chain = prompt | self.fast_llm | parser
        params = self._format_context_params(state['context'])

        result = await chain.ainvoke(params)
        state['pricing'] = result.model_dump()
        return state

    async def _assemble_final(self, state: GraphState) -> GraphState:
        """Build final output structure."""
        return {
            **state,
            'final_strategy': {
                "title": f"Growth Strategy for {state['context'].client_name}",
                "sections": [s.model_dump() for s in state['sections'].values()],
                "pricing": state['pricing']
            }
        }

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(GraphState)

        # Add all agent nodes dynamically (DRY: no repetition)
        for config in AGENT_CONFIGS:
            workflow.add_node(config.name, lambda s, c=config: self._run_agent(c, s))

        workflow.add_node("quality_check", self._check_quality)
        workflow.add_node("pricing", self._assemble_pricing)
        workflow.add_node("final", self._assemble_final)

        # Build sequential workflow (simpler than claimed "parallel")
        workflow.set_entry_point(AGENT_CONFIGS[0].name)
        for i in range(len(AGENT_CONFIGS) - 1):
            workflow.add_edge(AGENT_CONFIGS[i].name, AGENT_CONFIGS[i + 1].name)

        workflow.add_edge(AGENT_CONFIGS[-1].name, "quality_check")
        workflow.add_conditional_edges(
            "quality_check",
            lambda s: "pricing" if s['quality_passed'] else END,
            {"pricing": "pricing", END: END}
        )
        workflow.add_edge("pricing", "final")
        workflow.add_edge("final", END)

        return workflow.compile()

    async def generate_strategy(self, business_profile: Dict, questionnaire: Dict) -> Dict[str, Any]:
        """
        Generate marketing strategy.

        Args:
            business_profile: {name, industry, products, problems_solving, target_customers}
            questionnaire: {client_name, problem_statement, target_icp, business_objectives, budget_range, marketing_channels}

        Returns:
            {title, sections: [...], pricing: {...}, metadata: {...}}
        """
        context = self._build_context(business_profile, questionnaire)
        result = await self.workflow.ainvoke(GraphState(context=context))

        if not result.get('final_strategy'):
            raise ValueError("Strategy generation failed")

        result['final_strategy']['metadata'] = {
            "model": getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use'),
            "generated_at": datetime.utcnow().isoformat(),
            "sections_count": len(result['final_strategy'].get('sections', []))
        }

        return result['final_strategy']
