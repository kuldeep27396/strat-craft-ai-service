"""
Abstract base classes for strategy generation agents.

Following Strategy Pattern and Open/Closed Principle.
"""

from abc import ABC, abstractmethod
from typing import Any
from app.schemas.agent_output import StrategySection, AgentContext


class Agent(ABC):
    """Abstract base class for strategy generation agents."""

    @abstractmethod
    async def execute(self, context: AgentContext) -> StrategySection:
        """Execute the agent and generate a strategy section."""
        pass

    @abstractmethod
    def should_skip(self, context: AgentContext) -> bool:
        """Determine if this agent should be skipped."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the agent name."""
        pass


class WorkflowNode(ABC):
    """Abstract base class for workflow nodes."""

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the workflow node."""
        pass
