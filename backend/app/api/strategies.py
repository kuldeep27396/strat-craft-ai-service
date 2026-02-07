"""
Strategy API endpoints using Repository Pattern.

Following Service Layer pattern for business logic separation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Callable

from app.database import get_db
from app.schemas import StrategyGenerate, StrategyResponse, StrategyUpdate
from app.models import Strategy
from app.infrastructure.repositories import (
    SQLAlchemyQuestionnaireRepository,
    SQLAlchemyStrategyRepository
)
from app.agents import create_orchestrator
from app.interfaces.llm_provider import LLMProvider

router = APIRouter()


# Dependency injection factory
def get_questionnaire_repository(db: Session = Depends(get_db)) -> SQLAlchemyQuestionnaireRepository:
    """Get questionnaire repository (DI)."""
    return SQLAlchemyQuestionnaireRepository(db)


def get_strategy_repository(db: Session = Depends(get_db)) -> SQLAlchemyStrategyRepository:
    """Get strategy repository (DI)."""
    return SQLAlchemyStrategyRepository(db)


def get_orchestrator() -> Callable:
    """Get orchestrator factory (DI)."""
    return create_orchestrator


# Helper functions (Single Responsibility)
def to_profile_dict(profile) -> dict:
    """Convert business profile to dict."""
    return {
        "name": profile.business_name,
        "industry": profile.industry,
        "products": profile.products,
        "problems_solving": profile.problems_solving,
        "target_customers": profile.target_customers,
    }


def to_questionnaire_dict(q) -> dict:
    """Convert questionnaire to dict."""
    return {
        "client_name": q.client_name,
        "problem_statement": q.problem_statement,
        "target_icp": q.target_icp,
        "business_objectives": q.business_objectives,
        "budget_range": q.budget_range,
        "marketing_channels": q.marketing_channels,
    }


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def generate_strategy(
    req: StrategyGenerate,
    qr: SQLAlchemyQuestionnaireRepository = Depends(get_questionnaire_repository),
    sr: SQLAlchemyStrategyRepository = Depends(get_strategy_repository),
    orchestrator_factory: Callable = Depends(get_orchestrator)
):
    """Generate a marketing strategy using Repository Pattern."""
    # Fetch related data via repository
    questionnaire, profile = qr.get_with_business_profile(req.questionnaire_id)

    # Create strategy with generating status
    strategy = sr.create_with_status(req.questionnaire_id, "generating")

    try:
        # Generate using orchestrator (DI)
        orchestrator = orchestrator_factory()
        data = await orchestrator.generate_strategy(
            to_profile_dict(profile),
            to_questionnaire_dict(questionnaire)
        )

        # Update via repository
        sr.update_content(strategy, data, data.get("metadata"))
        sr.update_status(strategy, "completed")

    except ValueError as e:
        sr.update_status(strategy, "failed", {"error": str(e), "type": "configuration"})
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Configuration error: {e}")
    except Exception as e:
        sr.update_status(strategy, "failed", {"error": str(e), "type": "generation"})
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Generation failed: {e}")

    return sr.get_by_id(strategy.id)


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    sr: SQLAlchemyStrategyRepository = Depends(get_strategy_repository)
):
    """Get strategy by ID via repository."""
    if not (s := sr.get_by_id(strategy_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    return s


@router.get("/{strategy_id}/status")
async def get_strategy_status(
    strategy_id: UUID,
    sr: SQLAlchemyStrategyRepository = Depends(get_strategy_repository)
):
    """Get strategy status via repository."""
    if not (s := sr.get_by_id(strategy_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    return {"id": str(s.id), "status": s.status, "progress": 100 if s.status == "completed" else 50}


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    data: StrategyUpdate,
    sr: SQLAlchemyStrategyRepository = Depends(get_strategy_repository)
):
    """Update strategy via repository."""
    if not (s := sr.get_by_id(strategy_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")

    s.strategy_content = data.strategy_content
    s.version += 1
    return sr.save(s)


@router.post("/{strategy_id}/export")
async def export_strategy(
    strategy_id: UUID,
    sr: SQLAlchemyStrategyRepository = Depends(get_strategy_repository)
):
    """Export strategy to PDF."""
    if not (s := sr.get_by_id(strategy_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    if s.status != "completed":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Strategy not completed")
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "PDF export coming soon")
