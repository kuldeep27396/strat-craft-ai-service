from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.schemas import StrategyGenerate, StrategyResponse, StrategyUpdate
from app.models import Strategy, Questionnaire, BusinessProfile
from app.agents.orchestrator import StrategyOrchestrator

router = APIRouter()


# Helpers (DRY: extract repeated logic)
def get_questionnaire_with_profile(qid: UUID, db: Session) -> tuple[Questionnaire, BusinessProfile]:
    """Fetch questionnaire and its business profile."""
    q = db.query(Questionnaire).filter(Questionnaire.id == qid).first()
    if not q:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Questionnaire not found")

    p = db.query(BusinessProfile).filter(BusinessProfile.id == q.business_profile_id).first()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business profile not found")

    return q, p


def to_profile_dict(profile: BusinessProfile) -> dict:
    return {
        "name": profile.business_name,
        "industry": profile.industry,
        "products": profile.products,
        "problems_solving": profile.problems_solving,
        "target_customers": profile.target_customers,
    }


def to_questionnaire_dict(q: Questionnaire) -> dict:
    return {
        "client_name": q.client_name,
        "problem_statement": q.problem_statement,
        "target_icp": q.target_icp,
        "business_objectives": q.business_objectives,
        "budget_range": q.budget_range,
        "marketing_channels": q.marketing_channels,
    }


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def generate_strategy(req: StrategyGenerate, db: Session = Depends(get_db)):
    """Generate a marketing strategy from questionnaire."""
    questionnaire, profile = get_questionnaire_with_profile(req.questionnaire_id, db)

    strategy = Strategy(
        questionnaire_id=req.questionnaire_id,
        status="generating",
        strategy_content={}
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    try:
        data = await StrategyOrchestrator().generate_strategy(
            to_profile_dict(profile),
            to_questionnaire_dict(questionnaire)
        )
        strategy.strategy_content = data
        strategy.status = "completed"
        strategy.generation_metadata = data.get("metadata", {})

    except ValueError as e:
        strategy.status = "failed"
        strategy.generation_metadata = {"error": str(e), "error_type": "configuration"}
        db.commit()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Configuration error: {e}")

    except Exception as e:
        strategy.status = "failed"
        strategy.generation_metadata = {"error": str(e), "error_type": "generation"}
        db.commit()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Generation failed: {e}")

    db.commit()
    db.refresh(strategy)
    return strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    if not (s := db.query(Strategy).filter(Strategy.id == strategy_id).first()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    return s


@router.get("/{strategy_id}/status")
async def get_strategy_status(strategy_id: UUID, db: Session = Depends(get_db)):
    if not (s := db.query(Strategy).filter(Strategy.id == strategy_id).first()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    return {"id": s.id, "status": s.status, "progress": 100 if s.status == "completed" else 50}


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: UUID, data: StrategyUpdate, db: Session = Depends(get_db)):
    if not (s := db.query(Strategy).filter(Strategy.id == strategy_id).first()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")

    s.strategy_content = data.strategy_content
    s.version += 1
    db.commit()
    db.refresh(s)
    return s


@router.post("/{strategy_id}/export")
async def export_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    if not (s := db.query(Strategy).filter(Strategy.id == strategy_id).first()):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Strategy not found")
    if s.status != "completed":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Strategy not completed")
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "PDF export coming soon")
