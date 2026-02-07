"""
AI Agent Orchestrator using LangGraph with proper design patterns.

Implements:
- Dependency Injection (inject providers, repositories)
- Factory Pattern (AgentFactory, ChainFactory)
- Strategy Pattern (concrete Agent implementations)
- Repository Pattern (database access)
- Builder Pattern (StrategyBuilder)
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime
from uuid import UUID

from langgraph.graph import StateGraph, END

from app.config import settings
from app.interfaces.llm_provider import LLMProvider
from app.interfaces.repositories import StrategyRepository, QuestionnaireRepository
from app.infrastructure.llm import GroqLLMProvider, GroqChainFactory
from app.infrastructure.repositories import SQLAlchemyStrategyRepository, SQLAlchemyQuestionnaireRepository
from app.agents.factory import AgentFactory
from app.schemas.agent_output import StrategySection, PricingInfo, AgentContext


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    llm_provider: LLMProvider | None = None
    chain_factory: GroqChainFactory | None = None
    agent_factory: AgentFactory | None = None
    strategy_repository: StrategyRepository | None = None
    questionnaire_repository: QuestionnaireRepository | None = None

    def __post_init__(self):
        """Initialize defaults if not provided."""
        if self.llm_provider and not self.chain_factory:
            self.chain_factory = GroqChainFactory(self.llm_provider)
        if self.chain_factory and not self.agent_factory:
            self.agent_factory = AgentFactory(self.chain_factory)


@dataclass
class GraphState:
    """State for the LangGraph workflow."""
    context: AgentContext
    sections: dict[str, StrategySection] = field(default_factory=dict)
    pricing: Optional[dict] = None
    quality_passed: bool = False
    error: Optional[str] = None


class StrategyBuilder:
    """Builder for constructing the final strategy output."""

    @staticmethod
    def build_title(client_name: str) -> str:
        return f"Growth Strategy for {client_name}"

    @staticmethod
    def build_sections(sections_dict: dict[str, StrategySection]) -> list[dict]:
        return [s.model_dump() for s in sections_dict.values()]

    @staticmethod
    def build_metadata(model: str, sections_count: int) -> dict:
        return {
            "model": model,
            "generated_at": datetime.utcnow().isoformat(),
            "sections_count": sections_count
        }

    @classmethod
    def build(cls, context: AgentContext, sections: dict[str, StrategySection], pricing: dict, model: str) -> dict:
        """Build the complete strategy output."""
        return {
            "title": cls.build_title(context.client_name),
            "sections": cls.build_sections(sections),
            "pricing": pricing,
            "metadata": cls.build_metadata(model, len(sections))
        }


class StrategyOrchestrator:
    """
    Orchestrator for AI strategy generation with proper dependency injection.

    Following SOLID principles:
    - Single Responsibility: coordinates workflow
    - Open/Closed: extensible via factory pattern
    - Liskov Substitution: works with any LLMProvider/Repository
    - Interface Segregation: focused interfaces
    - Dependency Inversion: depends on abstractions
    """

    def __init__(self, config: OrchestratorConfig | None = None):
        """Initialize with dependency injection."""
        self.config = config or OrchestratorConfig()

        # Initialize dependencies
        if not self.config.llm_provider:
            self.config.llm_provider = GroqLLMProvider()

        if not self.config.chain_factory:
            self.config.chain_factory = GroqChainFactory(self.config.llm_provider)

        if not self.config.agent_factory:
            self.config.agent_factory = AgentFactory(self.config.chain_factory)

        # Get agents
        self.agents = self.config.agent_factory.create_all_agents()

        # Build workflow
        self.workflow = self._build_workflow()

    def _build_context(self, business_profile: dict, questionnaire: dict) -> AgentContext:
        """Build context with safe defaults."""
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

    async def _run_agent(self, agent: Any, state: GraphState) -> GraphState:
        """Run a single agent (Strategy Pattern)."""
        if agent.should_skip(state['context']):
            return state

        try:
            section = await agent.execute(state['context'])
            state['sections'][agent.state_key] = section
        except Exception as e:
            state['error'] = f"{agent.name} failed: {e}"

        return state

    async def _check_quality(self, state: GraphState) -> GraphState:
        """Validate minimum required sections."""
        state['quality_passed'] = len(state['sections']) >= 2 and not state['error']
        return state

    async def _generate_pricing(self, state: GraphState) -> GraphState:
        """Generate pricing using chain factory."""
        chain = self.config.chain_factory.create_pricing_chain()
        params = {
            "client_name": state['context'].client_name,
            "industry": state['context'].industry,
            "budget_range": state['context'].budget_range or "Not specified",
            "marketing_channels": ", ".join(state['context'].marketing_channels or []),
        }

        result = await chain.ainvoke(params)
        state['pricing'] = result.model_dump()
        return state

    async def _build_final(self, state: GraphState) -> GraphState:
        """Build final output using Builder Pattern."""
        if not state['quality_passed']:
            state['final_strategy'] = None
            return state

        model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use')
        state['final_strategy'] = StrategyBuilder.build(
            state['context'],
            state['sections'],
            state['pricing'],
            model
        )
        return state

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(GraphState)

        # Add agent nodes dynamically
        for agent in self.agents:
            workflow.add_node(agent.state_key, lambda s, a=agent: self._run_agent(a, s))

        workflow.add_node("quality_check", self._check_quality)
        workflow.add_node("pricing", self._generate_pricing)
        workflow.add_node("final", self._build_final)

        # Build sequential workflow
        workflow.set_entry_point(self.agents[0].state_key)
        for i in range(len(self.agents) - 1):
            workflow.add_edge(self.agents[i].state_key, self.agents[i + 1].state_key)

        workflow.add_edge(self.agents[-1].state_key, "quality_check")
        workflow.add_conditional_edges(
            "quality_check",
            lambda s: "pricing" if s['quality_passed'] else END,
            {"pricing": "pricing", END: END}
        )
        workflow.add_edge("pricing", "final")
        workflow.add_edge("final", END)

        return workflow.compile()

    async def generate_strategy(self, business_profile: dict, questionnaire: dict) -> dict:
        """
        Generate marketing strategy.

        Args:
            business_profile: Business profile data
            questionnaire: Questionnaire data

        Returns:
            Generated strategy dict
        """
        context = self._build_context(business_profile, questionnaire)
        result = await self.workflow.ainvoke(GraphState(context=context))

        if not result.get('final_strategy'):
            error_msg = result.get('error', 'Unknown error')
            raise ValueError(f"Strategy generation failed: {error_msg}")

        return result['final_strategy']


# Convenience factory function
def create_orchestrator(
    llm_provider: LLMProvider | None = None,
    strategy_repository: StrategyRepository | None = None,
    questionnaire_repository: QuestionnaireRepository | None = None
) -> StrategyOrchestrator:
    """Factory function to create an orchestrator with dependencies."""
    config = OrchestratorConfig(
        llm_provider=llm_provider,
        strategy_repository=strategy_repository,
        questionnaire_repository=questionnaire_repository
    )
    return StrategyOrchestrator(config)
