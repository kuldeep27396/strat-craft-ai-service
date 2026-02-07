"""
SQLAlchemy repository implementations.

Following Repository Pattern to abstract database access.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.interfaces.repositories import BaseRepository, QuestionnaireRepository, StrategyRepository
from app.models import Questionnaire, Strategy, BusinessProfile


class BaseSQLAlchemyRepository(BaseRepository):
    """Base repository with common SQLAlchemy operations."""

    def __init__(self, session: Session, model: type):
        self.session = session
        self.model = model

    def get_by_id(self, id: UUID) -> Optional[Any]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def list_all(self) -> List[Any]:
        return self.session.query(self.model).all()

    def save(self, entity: Any) -> Any:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, id: UUID) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False


class SQLAlchemyQuestionnaireRepository(BaseSQLAlchemyRepository, QuestionnaireRepository):
    """Repository for Questionnaire entities."""

    def __init__(self, session: Session):
        super().__init__(session, Questionnaire)

    def get_with_business_profile(self, id: UUID) -> tuple[Questionnaire, BusinessProfile]:
        """Get questionnaire with its business profile."""
        q = self.get_by_id(id)
        if not q:
            raise ValueError(f"Questionnaire {id} not found")

        p = self.session.query(BusinessProfile).filter(
            BusinessProfile.id == q.business_profile_id
        ).first()

        if not p:
            raise ValueError(f"Business profile for questionnaire {id} not found")

        return q, p


class SQLAlchemyStrategyRepository(BaseSQLAlchemyRepository, StrategyRepository):
    """Repository for Strategy entities."""

    def __init__(self, session: Session):
        super().__init__(session, Strategy)

    def get_by_questionnaire_id(self, questionnaire_id: UUID) -> List[Strategy]:
        return self.session.query(Strategy).filter(
            Strategy.questionnaire_id == questionnaire_id
        ).all()

    def get_by_status(self, status: str) -> List[Strategy]:
        return self.session.query(Strategy).filter(Strategy.status == status).all()

    def create_with_status(
        self,
        questionnaire_id: UUID,
        status: str = "generating",
        content: dict | None = None
    ) -> Strategy:
        """Create a new strategy with the given status."""
        strategy = Strategy(
            questionnaire_id=questionnaire_id,
            status=status,
            strategy_content=content or {}
        )
        return self.save(strategy)

    def update_content(self, strategy: Strategy, content: dict, metadata: dict | None = None) -> Strategy:
        """Update strategy content and metadata."""
        strategy.strategy_content = content
        if metadata:
            strategy.generation_metadata = metadata
        self.session.commit()
        self.session.refresh(strategy)
        return strategy

    def update_status(self, strategy: Strategy, status: str, metadata: dict | None = None) -> Strategy:
        """Update strategy status."""
        strategy.status = status
        if metadata:
            strategy.generation_metadata = metadata
        self.session.commit()
        self.session.refresh(strategy)
        return strategy
