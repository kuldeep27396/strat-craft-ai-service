"""
AI Agent Orchestrator using LangGraph

This module implements a multi-agent system for strategy generation
using Groq's fast LLM models (Llama 3.1 and Mixtral).
"""

import os
from typing import Dict, Any, Optional, TypedDict
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import StateGraph, END

from app.config import settings
from app.schemas.agent_output import (
    StrategySection,
    PricingInfo,
    StrategyContent,
    AgentContext,
    AgentState
)


class GraphState(TypedDict):
    """State for the LangGraph workflow."""
    context: AgentContext
    executive_summary: Optional[StrategySection]
    seo_section: Optional[StrategySection]
    content_section: Optional[StrategySection]
    paid_ads_section: Optional[StrategySection]
    quality_passed: Optional[bool]
    final_strategy: Optional[Dict[str, Any]]
    iteration: int


class StrategyOrchestrator:
    """
    Main orchestrator for AI strategy generation using LangGraph.

    The workflow consists of:
    1. Context Builder - Analyzes business profile and questionnaire
    2. Parallel Agent Execution:
       - SEO Agent - Generates SEO strategy
       - Content Agent - Generates content marketing strategy
       - Paid Ads Agent - Generates paid advertising strategy
    3. Quality Reviewer - Validates strategy quality
    4. Final Assembler - Combines all sections into final output
    """

    def __init__(self):
        """Initialize the orchestrator with Groq LLM models."""
        # Check for Groq API key
        groq_api_key = getattr(settings, 'GROQ_API_KEY', None) or os.getenv('GROQ_API_KEY')

        if not groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is required. Set it in .env or as environment variable. "
                "Get your API key at https://console.groq.com/"
            )

        # Initialize Groq models
        model_name = getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use')
        fast_model_name = getattr(settings, 'GROQ_FAST_MODEL', 'llama-3.1-8b-instant')

        self.llm = ChatGroq(
            api_key=groq_api_key,
            model_name=model_name,
            temperature=0.7,
            max_tokens=4096
        )

        self.fast_llm = ChatGroq(
            api_key=groq_api_key,
            model_name=fast_model_name,
            temperature=0.5,
            max_tokens=2048
        )

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_context(self, business_profile: Dict[str, Any], questionnaire: Dict[str, Any]) -> AgentContext:
        """Build structured context from raw input data."""
        return AgentContext(
            client_name=questionnaire.get('client_name', business_profile.get('name', 'Client')),
            industry=business_profile.get('industry', 'Unknown'),
            problem_statement=questionnaire.get('problem_statement', ''),
            target_icp=questionnaire.get('target_icp', '') if isinstance(questionnaire.get('target_icp'), str) else str(questionnaire.get('target_icp', {})),
            business_objectives=questionnaire.get('business_objectives', []) if isinstance(questionnaire.get('business_objectives'), list) else [str(questionnaire.get('business_objectives', 'Grow business'))],
            budget_range=questionnaire.get('budget_range'),
            marketing_channels=questionnaire.get('marketing_channels') if isinstance(questionnaire.get('marketing_channels'), list) else None,
            products=business_profile.get('products') if isinstance(business_profile.get('products'), list) else None,
            target_customers=business_profile.get('target_customers') if isinstance(business_profile.get('target_customers'), list) else None
        )

    async def _context_builder(self, state: GraphState) -> GraphState:
        """Build context from business profile and questionnaire."""
        # Context is already built in generate_strategy, just pass it through
        return state

    async def _executive_summary_agent(self, state: GraphState) -> GraphState:
        """Generate executive summary section."""
        context = state['context']

        parser = PydanticOutputParser(pydantic_object=StrategySection)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert marketing strategist. Generate a compelling executive summary for a marketing strategy.

Executive Summary should:
- Provide a high-level overview of the recommended approach
- Highlight the key opportunity identified
- Outline the primary focus areas
- Be concise but impactful (2-3 paragraphs)

{format_instructions}"""),
            ("user", """Generate an executive summary for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Focus on creating a summary that builds confidence and clarity.""")
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "business_objectives": ", ".join(context.business_objectives) if context.business_objectives else "Growth",
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels) if context.marketing_channels else "Various"
        })

        state['executive_summary'] = result
        return state

    async def _seo_agent(self, state: GraphState) -> GraphState:
        """Generate SEO strategy section."""
        context = state['context']

        parser = PydanticOutputParser(pydantic_object=StrategySection)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an SEO expert. Generate a comprehensive SEO strategy section.

The SEO Strategy should include:
- Technical SEO recommendations
- Content strategy for organic growth
- Keyword approach and target topics
- Link building strategy
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}"""),
            ("user", """Generate an SEO strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Products: {products}

Focus on practical, actionable SEO recommendations that align with their business.""")
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "products": ", ".join(context.products) if context.products else context.client_name
        })

        state['seo_section'] = result
        return state

    async def _content_agent(self, state: GraphState) -> GraphState:
        """Generate content marketing section."""
        context = state['context']

        parser = PydanticOutputParser(pydantic_object=StrategySection)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content marketing expert. Generate a content marketing strategy section.

The Content Marketing Strategy should include:
- Editorial approach and content themes
- Content types and formats
- Distribution channels
- Content calendar framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}"""),
            ("user", """Generate a content marketing strategy for:

Client: {client_name}
Industry: {industry}
Problem They Solve: {problem_statement}
Target ICP: {target_icp}
Business Objectives: {business_objectives}
Preferred Channels: {marketing_channels}

Create a content strategy that speaks directly to their target audience's needs.""")
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "problem_statement": context.problem_statement,
            "target_icp": context.target_icp,
            "business_objectives": ", ".join(context.business_objectives) if context.business_objectives else "Growth",
            "marketing_channels": ", ".join(context.marketing_channels) if context.marketing_channels else "Website, LinkedIn, Email"
        })

        state['content_section'] = result
        return state

    async def _paid_ads_agent(self, state: GraphState) -> GraphState:
        """Generate paid advertising section (optional based on budget/channels)."""
        context = state['context']

        # Skip if budget is very low or channels exclude paid ads
        budget = context.budget_range or ""
        if any(term in budget.lower() for term in ['$0', 'none', 'organic only', 'no budget']):
            state['paid_ads_section'] = None
            return state

        parser = PydanticOutputParser(pydantic_object=StrategySection)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a paid advertising expert. Generate a paid advertising strategy section.

The Paid Ads Strategy should include:
- Platform recommendations (Google, Meta, LinkedIn, etc.)
- Budget allocation strategy
- Campaign types and targeting approach
- Ad creative framework
- Specific tactics (3-5 actions)
- Measurable KPIs (2-4 metrics)

{format_instructions}"""),
            ("user", """Generate a paid advertising strategy for:

Client: {client_name}
Industry: {industry}
Target ICP: {target_icp}
Budget: {budget_range}
Preferred Channels: {marketing_channels}

Recommend efficient paid channels that maximize ROI within their budget.""")
        ])

        chain = prompt | self.llm | parser

        result = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "target_icp": context.target_icp,
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels) if context.marketing_channels else "All relevant channels"
        })

        state['paid_ads_section'] = result
        return state

    async def _quality_reviewer(self, state: GraphState) -> GraphState:
        """Review the generated strategy for quality and completeness."""
        # Simple quality check - ensure all required sections are present
        has_executive = state.get('executive_summary') is not None
        has_seo = state.get('seo_section') is not None
        has_content = state.get('content_section') is not None

        # Quality passes if we have at least executive + 1 other section
        quality_passed = has_executive and (has_seo or has_content)

        state['quality_passed'] = quality_passed
        return state

    async def _final_assembler(self, state: GraphState) -> GraphState:
        """Assemble the final strategy from all generated sections."""
        context = state['context']

        # Build sections list
        sections = []

        if state.get('executive_summary'):
            sections.append(state['executive_summary'].model_dump())

        if state.get('seo_section'):
            sections.append(state['seo_section'].model_dump())

        if state.get('content_section'):
            sections.append(state['content_section'].model_dump())

        if state.get('paid_ads_section'):
            sections.append(state['paid_ads_section'].model_dump())

        # Generate pricing info
        pricing = await self._generate_pricing(context)

        # Create final strategy
        final_strategy = {
            "title": f"Growth Strategy for {context.client_name}",
            "sections": sections,
            "pricing": pricing
        }

        state['final_strategy'] = final_strategy
        return state

    async def _generate_pricing(self, context: AgentContext) -> Dict[str, Any]:
        """Generate pricing and team recommendations."""
        parser = PydanticOutputParser(pydantic_object=PricingInfo)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a marketing agency pricing expert. Generate appropriate pricing and team recommendations.

Consider:
- The industry and complexity
- The scope of work (SEO, Content, Paid Ads)
- The client's budget range
- Standard agency rates

{format_instructions}"""),
            ("user", """Generate pricing for:

Client: {client_name}
Industry: {industry}
Budget Range: {budget_range}
Channels: {marketing_channels}

Provide realistic monthly pricing (in USD) and team composition.""")
        ])

        chain = prompt | self.fast_llm | parser

        result = await chain.ainvoke({
            "format_instructions": parser.get_format_instructions(),
            "client_name": context.client_name,
            "industry": context.industry,
            "budget_range": context.budget_range or "Not specified",
            "marketing_channels": ", ".join(context.marketing_channels) if context.marketing_channels else "SEO, Content"
        })

        return result.model_dump()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("context_builder", self._context_builder)
        workflow.add_node("executive_summary", self._executive_summary_agent)
        workflow.add_node("seo_agent", self._seo_agent)
        workflow.add_node("content_agent", self._content_agent)
        workflow.add_node("paid_ads_agent", self._paid_ads_agent)
        workflow.add_node("quality_reviewer", self._quality_reviewer)
        workflow.add_node("final_assembler", self._final_assembler)

        # Define edges
        workflow.set_entry_point("context_builder")

        # After context, run executive summary first (needed for quality)
        workflow.add_edge("context_builder", "executive_summary")

        # Then run SEO, content, and paid ads in parallel
        workflow.add_edge("executive_summary", "seo_agent")
        workflow.add_edge("executive_summary", "content_agent")
        workflow.add_edge("executive_summary", "paid_ads_agent")

        # All agents converge at quality reviewer
        workflow.add_edge("seo_agent", "quality_reviewer")
        workflow.add_edge("content_agent", "quality_reviewer")
        workflow.add_edge("paid_ads_agent", "quality_reviewer")

        # Quality check decision
        workflow.add_conditional_edges(
            "quality_reviewer",
            lambda s: "final_assembler" if s.get('quality_passed') else END,
            {
                "final_assembler": "final_assembler",
                END: END
            }
        )

        # End at final assembler
        workflow.add_edge("final_assembler", END)

        return workflow.compile()

    async def generate_strategy(
        self,
        business_profile: Dict[str, Any],
        questionnaire: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate marketing strategy using AI agents.

        Args:
            business_profile: Business intelligence data containing:
                - name: Business name
                - industry: Industry sector
                - products: List of products/services
                - problems_solving: Problems the business solves
                - target_customers: Target customer segments
            questionnaire: Client questionnaire data containing:
                - client_name: Name of the client
                - problem_statement: Primary problem statement
                - target_icp: Ideal customer profile
                - business_objectives: List of business objectives
                - budget_range: Budget range
                - marketing_channels: Preferred marketing channels

        Returns:
            Generated strategy as dict with structure:
            {
                "title": "Strategy title",
                "sections": [...],
                "pricing": {...}
            }
        """
        # Build context
        context = self._build_context(business_profile, questionnaire)

        # Initialize state
        initial_state: GraphState = {
            "context": context,
            "executive_summary": None,
            "seo_section": None,
            "content_section": None,
            "paid_ads_section": None,
            "quality_passed": None,
            "final_strategy": None,
            "iteration": 0
        }

        # Run workflow
        result = await self.workflow.ainvoke(initial_state)

        # Extract final strategy
        final_strategy = result.get('final_strategy')

        if not final_strategy:
            raise ValueError("Strategy generation failed - no output produced")

        # Add generation metadata
        final_strategy['metadata'] = {
            "model": getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use'),
            "generated_at": datetime.utcnow().isoformat(),
            "sections_count": len(final_strategy.get('sections', []))
        }

        return final_strategy
