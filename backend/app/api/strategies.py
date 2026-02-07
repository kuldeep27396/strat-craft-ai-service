from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.schemas import StrategyGenerate, StrategyResponse, StrategyUpdate
from app.models import Strategy, Questionnaire, BusinessProfile
from app.agents.orchestrator import StrategyOrchestrator

router = APIRouter()


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def generate_strategy(strategy_request: StrategyGenerate, db: Session = Depends(get_db)):
    """Generate a new marketing strategy from questionnaire"""
    # Verify questionnaire exists
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == strategy_request.questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Questionnaire not found")
    
    # Create strategy record with 'generating' status
    new_strategy = Strategy(
        questionnaire_id=strategy_request.questionnaire_id,
        status="generating",
        strategy_content={}
    )
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)

    # Fetch related business profile
    business_profile = db.query(BusinessProfile).filter(
        BusinessProfile.id == questionnaire.business_profile_id
    ).first()

    if not business_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found for this questionnaire"
        )

    # Initialize orchestrator and generate strategy using AI agents
    try:
        orchestrator = StrategyOrchestrator()

        # Prepare business profile data
        business_profile_data = {
            "name": business_profile.business_name,
            "industry": business_profile.industry,
            "products": business_profile.products,
            "problems_solving": business_profile.problems_solving,
            "target_customers": business_profile.target_customers,
        }

        # Prepare questionnaire data
        questionnaire_data = {
            "client_name": questionnaire.client_name,
            "problem_statement": questionnaire.problem_statement,
            "target_icp": questionnaire.target_icp,
            "business_objectives": questionnaire.business_objectives,
            "budget_range": questionnaire.budget_range,
            "marketing_channels": questionnaire.marketing_channels,
        }

        # Generate strategy using AI agents
        strategy_data = await orchestrator.generate_strategy(
            business_profile=business_profile_data,
            questionnaire=questionnaire_data
        )

        new_strategy.strategy_content = strategy_data
        new_strategy.status = "completed"
        new_strategy.generation_metadata = {
            "model": strategy_data.get("metadata", {}).get("model", "unknown"),
            "generated_at": strategy_data.get("metadata", {}).get("generated_at", datetime.utcnow().isoformat()),
            "sections_count": strategy_data.get("metadata", {}).get("sections_count", 0)
        }

    except ValueError as e:
        # Handle configuration errors (e.g., missing API key)
        new_strategy.status = "failed"
        new_strategy.generation_metadata = {
            "error": str(e),
            "error_type": "configuration_error"
        }
        db.add(new_strategy)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation configuration error: {str(e)}"
        )
    except Exception as e:
        # Handle generation errors
        new_strategy.status = "failed"
        new_strategy.generation_metadata = {
            "error": str(e),
            "error_type": "generation_error",
            "timestamp": datetime.utcnow().isoformat()
        }
        db.add(new_strategy)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation failed: {str(e)}"
        )

    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)

    return new_strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    """Get a specific strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    return strategy


@router.get("/{strategy_id}/status")
async def get_strategy_status(strategy_id: UUID, db: Session = Depends(get_db)):
    """Get generation status of a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    return {
        "id": strategy.id,
        "status": strategy.status,
        "progress": 100 if strategy.status == "completed" else 50  # Placeholder
    }


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update/edit a strategy"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    
    strategy.strategy_content = strategy_data.strategy_content
    strategy.version += 1
    
    db.commit()
    db.refresh(strategy)
    
    return strategy


@router.post("/{strategy_id}/export")
async def export_strategy(strategy_id: UUID, db: Session = Depends(get_db)):
    """Export strategy to PDF"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    if strategy.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Strategy is not completed yet"
        )
    
    # TODO: Implement PDF export
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="PDF export coming soon")
