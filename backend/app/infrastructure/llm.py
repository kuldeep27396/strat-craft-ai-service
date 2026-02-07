"""
Concrete LLM provider implementations.

Following Factory Pattern and Dependency Injection.
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import Runnable

from app.interfaces.llm_provider import LLMProvider, ChainFactory
from app.config import settings
from app.schemas.agent_output import StrategySection, PricingInfo


class GroqLLMProvider(LLMProvider):
    """Groq LLM provider implementation."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or getattr(settings, 'GROQ_API_KEY', None)
        if not self.api_key:
            raise ValueError("GROQ_API_KEY required")

    def get_model(self, model_name: str | None = None) -> Runnable:
        model = model_name or getattr(settings, 'GROQ_MODEL', 'llama-3.1-70b-tool-use')
        return ChatGroq(api_key=self.api_key, model_name=model_name)

    def supports_streaming(self) -> bool:
        return True


class GroqChainFactory(ChainFactory):
    """Factory for creating Groq LLM chains."""

    def __init__(self, provider: GroqLLMProvider):
        self.provider = provider
        self.llm = provider.get_model()
        self.fast_llm = provider.get_model(getattr(settings, 'GROQ_FAST_MODEL', 'llama-3.1-8b-instant'))

    def create_chain(
        self,
        system_prompt: str,
        user_prompt_template: str,
        output_schema: type,
        use_fast_llm: bool = False
    ) -> Runnable:
        """Create an LLM chain with the given configuration."""
        parser = PydanticOutputParser(pydantic_object=output_schema)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt_template)
        ])
        llm = self.fast_llm if use_fast_llm else self.llm
        return prompt | llm | parser

    def create_strategy_chain(self, system_prompt: str, user_prompt: str) -> Runnable:
        """Create a chain specifically for strategy sections."""
        return self.create_chain(system_prompt, user_prompt, StrategySection)

    def create_pricing_chain(self) -> Runnable:
        """Create a chain for pricing generation."""
        return self.create_chain(
            """Generate appropriate pricing and team recommendations. Consider industry, scope, and budget. {format_instructions}""",
            "Client: {client_name}\nIndustry: {industry}\nBudget: {budget_range}\nChannels: {marketing_channels}",
            PricingInfo,
            use_fast_llm=True
        )
