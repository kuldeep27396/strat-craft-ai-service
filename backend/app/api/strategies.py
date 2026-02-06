from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas import StrategyGenerate, StrategyResponse, StrategyUpdate
from app.models import Strategy, Questionnaire

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
    
    # TODO: Trigger async AI agent workflow here
    # For now, just return the created strategy
    
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
