"""
Abstract repository interfaces.

Following Repository Pattern and Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID


class BaseRepository(ABC):
    """Abstract base repository with common CRUD operations."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Any]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def list_all(self) -> List[Any]:
        """List all entities."""
        pass

    @abstractmethod
    def save(self, entity: Any) -> Any:
        """Save entity."""
        pass

    @abstractmethod
    def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        pass


class QuestionnaireRepository(BaseRepository):
    """Repository for Questionnaire entities."""

    @abstractmethod
    def get_with_business_profile(self, id: UUID) -> tuple[Any, Any]:
        """Get questionnaire with its business profile."""
        pass


class StrategyRepository(BaseRepository):
    """Repository for Strategy entities."""

    @abstractmethod
    def get_by_questionnaire_id(self, questionnaire_id: UUID) -> List[Any]:
        """Get all strategies for a questionnaire."""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Any]:
        """Get strategies by status."""
        pass
