"""
Abstract base classes for LLM providers.

Following Dependency Inversion Principle: depend on abstractions, not concretions.
"""

from abc import ABC, abstractmethod
from typing import Any
from langchain_core.runnables import Runnable


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_model(self, model_name: str | None = None) -> Runnable:
        """Get an LLM model instance."""
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        pass


class ChainFactory(ABC):
    """Abstract factory for creating LLM chains."""

    @abstractmethod
    def create_chain(self, prompt_template: str, system_prompt: str, output_schema: type) -> Runnable:
        """Create an LLM chain with the given configuration."""
        pass
